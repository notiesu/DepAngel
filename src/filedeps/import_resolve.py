from tree_sitter import Language, Parser
from tree_sitter import Tree as ASTree
from tree_sitter import Node as ASTNode
import os
import json

#input - AST node representing an import statement
#output - os.paths to imported files,  standard libraries, or site packages
#TODO: Make this an os environment variable
STD_LIBS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "std_libs.json")
SITE_LIBS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "site_libs.json")
IMPORT_SYMS_PATH = os.path.join(os.path.dirname(__file__), "import_symbols.json")


class UnresolvedDep:
    def __init__(self, src_path: str, keyword: str, statement: str):
        """Necessary info: file path, unresolved keyword, import statement"""
        self.src_path = src_path
        self.keyword = keyword
        self.statement = statement

    def __str__(self):
        return f"File: {self.file_path}, Unresolved Imports: {', '.join(self.imports)}"

class ExternalDepResolver:
    def __init__(self, source_set: set[str]):
        self.source_set = source_set
        self.stdlib: dict[str, str] = {}
        self.sitelib: dict[str, str]  = {}
        self.unresolved_imports: list[UnresolvedDep] = []
        with open(STD_LIBS_PATH, 'r') as f:
            self.stdlib = json.load(f)
        with open(SITE_LIBS_PATH, 'r') as f:
            self.sitelib = json.load(f)
        if not self.stdlib or not self.sitelib:
            print("Warning: Failed to load standard library or site packages data. Dependencies may be missing or will not resolve correctly.")

    def resolve(self, pkg_name: str) -> str:
        """Resolve the package name to its absolute path."""
        if pkg_name in self.stdlib:
            return "stdlib/" + os.path.join(self.stdlib[pkg_name], pkg_name)
        elif pkg_name in self.sitelib:
            return "sitepkg/" + os.path.join(self.sitelib[pkg_name], pkg_name)
        # no needto check source set - ImportTarget will resolve
        else:
            return None
        
    def log_unresolved_imports(self) -> None:
        """Print unresolved imports."""
        if self.unresolved_imports:
            with open('unresolved_imports.txt', 'w') as f:
                for dep in self.unresolved_imports:
                    f.write(f"File: {dep.src_path}, Unresolved Keyword: {dep.keyword}, Statement: {dep.statement}\n")
        else:
            print("No unresolved imports found.")
        

class ImportTarget:

    def _get_node_by_name(self, node:ASTNode, target: str) -> ASTNode:
        for child in node.children:
            if child.type == target:
                return child
        return None
    
    def __init__(self, root: ASTNode, src_path: str, dep: ExternalDepResolver, language: str):
        #extract - module name
        self.root = root
        self.importType = root.type
        self.src_path = src_path
        self.root_dir = os.path.dirname(src_path)
        self.dep = dep
        self.unresolved_imports = set()
        self.language = language

    
    def _resolve_external_import(self, pkg_name: str) -> str:
        return ""
    def extract_import(self) -> list[str]:
        """Get dependencies for a given AST"""
        #TODO: Handle dotted imports, dotted imports into stdlib/sitelib
        #starting with pure file dependencies for now - ignoring from statements

        if (self.language == 'python'):
            import_paths = set()
            #casework on import type - make sure to resolve relative imports
            if (self.importType == 'import_statement'):
                for child in self.root.children:
                    if child.type == 'dotted_name':
                        target_file = child.text.decode()
                        target_path = self.resolve_import(target_file)
                        import_paths.add(target_path)

            elif (self.importType == 'import_from_statement'):
                #need to look at relative_import type
                for child in self.root.children:
                    if (child.type == 'relative_import'):
                        target_file = child.text.decode()
                        target_path = self.resolve_import(target_file)
                        import_paths.add(target_path)
                    if (child.type == 'dotted_name'):
                        target_file = child.text.decode()
                        target_path = self.resolve_import(target_file)
                        import_paths.add(target_path)

            return import_paths
        elif (self.language == 'cpp'):
            import_paths = set()
            #somewhat redundant check
            #system lib string for syslibs, else string_literal for file deps
            if (self.importType == 'preproc_include'):
                nxt = self._get_node_by_name(self.root, 'string_literal')
                if nxt:
                    nxt2  = self._get_node_by_name(nxt, 'string_content')
                    if nxt2:
                        target_file = nxt2.text.decode()
                        target_path = self.resolve_import(target_file)
                        import_paths.add(target_path)
                else:
                    nxt = self._get_node_by_name(self.root, 'system_lib_string')
                    if nxt:
                        target_file = nxt.text.decode()
                        target_path = self.resolve_import(target_file)
                        import_paths.add(target_path)
            return import_paths

    def resolve_import(self, target: str) -> str:
        """Resolve relative imports to absolute paths."""
        #TODO: Might have to breakout based on language for right now case work
        if (self.language == 'python'):

            if target.startswith('.'):
                # Handle relative imports
                directory = os.path.dirname(self.src_path)
                resolved_path = os.path.normpath(os.path.join(directory, target.lstrip('.')))
                return resolved_path + '.py' if not resolved_path.endswith('.py') else resolved_path
            else:
                # Handle absolute imports
                # Check if external dependency
                res = self.dep.resolve(target)
                if res:
                    return res
                #TODO: Only handles same language imports. May have to flatten the source set to make it work better
                elif target in self.dep.source_set:
                    #Check if the target is in the source set
                    return os.path.join(self.root_dir, target) + '.py' if not target.endswith('.py') else target
                else:
                    # Handle case where the target is not found - pass to extract_import
                    self.dep.unresolved_imports.append(UnresolvedDep(self.src_path, target, self.root.text.decode()))
                    return ""
        elif (self.language == 'cpp'):
            if target.startswith('<'):
                # standard library import
                return "std_include/" + target[1:-1]
            else:
                #parsepath to compare
                base_dir = os.path.dirname(os.path.abspath(target))
                full_path = os.path.normpath(os.path.join(base_dir, target))
                if os.path.isfile(full_path):
                    return full_path
                else:
                    # Handle case where the target is not found - pass to extract_import
                    self.dep.unresolved_imports.append(UnresolvedDep(self.src_path, target, self.root.text.decode()))
                    return ""