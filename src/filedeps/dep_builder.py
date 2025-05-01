import os
import json

from tree_sitter import Language, Parser
from tree_sitter import Tree as ASTree
from tree_sitter import Node as ASTNode
from tree_sitter_language_pack import get_parser
from ..graphs import DepGraph
from dotenv import load_dotenv
from .. import trees
from .import_resolve import ImportTarget, ExternalDepResolver

#NOTE: DepBuilder takes in a set, not a dict - will need to iterate over all language buckets, own builder instance
IMPORT_SYMS_PATH = os.path.join(os.path.dirname(__file__), "import_symbols.json")

class DepBuilder:
    import_symbols: dict[str, str] = None
    def __init__(self, source_set: set[str], root_directory: str, language: str):
        self.source_set = source_set
        self.dependency_graph: DepGraph = DepGraph()
        self.parser: Parser = get_parser(language)
        self.visited: set[str] = set()
        self.root_directory: str = root_directory  
        self.dep: ExternalDepResolver = ExternalDepResolver(source_set)
        self.language: str = language
        if not DepBuilder.import_symbols:
            with open(IMPORT_SYMS_PATH, 'r') as f:
                DepBuilder.import_symbols = json.load(f)

    def set_language(self, language: str) -> None:
        """Set the language for the parser."""
        if language == 'python':
            self.parser = get_parser(language)
            self.language = language
        else:
            raise ValueError(f"Unsupported language: {language}")
        
    
    def _parse_AST(self, node: ASTNode, file_path: str) -> list[str]:
        """Parse the AST node to extract import paths."""
        import_paths = set()
        #TODO: We'll need a more flexible solution for filtering for multiple languages.
        if node.type in DepBuilder.import_symbols[self.language]:
            import_target = ImportTarget(node, file_path, self.dep, self.language)
            target_paths = import_target.extract_import()
            if target_paths:
                import_paths.update(target_paths)
        #recursive walk
        for child in node.children:
            import_paths.update(self._parse_AST(child, file_path))
        #DEBUG
        # if import_paths:
        #     print(f"Visited: {file_path}")
        #     print(f"Dependencies for {file_path}: {self.dependency_graph.get_dependencies(file_path)}")
        #     print(f"Import paths: {import_paths}")
        #     print("\n")
        return import_paths
    
    def _get_ast(self, file_path: str) -> ASTree:
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
        except FileNotFoundError:
            return None
        return self.parser.parse(source_code)
    

    def _build_graph_recursively(self, file_path: str) -> None:
        """Recursively build the dependency tree."""
        if file_path in self.visited:
            return
        self.visited.add(file_path)
        ast = self._get_ast(file_path)
        if not ast:
            return
        root_node = ast.root_node
        import_paths = self._parse_AST(root_node, file_path)
        for import_path in import_paths:
            # Add the dependency to the graph
            if import_path:
                self.dependency_graph.add_dependency(file_path, import_path)
                self._build_graph_recursively(import_path)

            # Mark the file as visited
    def log_unresolved_imports(self) -> None:
        self.dep.log_unresolved_imports()

    
    def build_dependency_graph(self) -> DepGraph:
        """Build the source file dependency graph."""
        for file_path in self.source_set:
            if file_path not in self.visited:
                self._build_graph_recursively(file_path)

        return self.dependency_graph
