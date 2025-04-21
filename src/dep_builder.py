import os
from tree_sitter import Language, Parser
from tree_sitter import Tree as ASTree
from tree_sitter import Node as ASTNode
import tree_sitter_python as tspython
from graphs import FileDepGraph
from dotenv import load_dotenv
import trees 
from import_resolve import ImportTarget, ExternalDepResolver

# Load environment variables for Tree-sitter library path
# load_dotenv()
# LIBRARY_PATH = os.getenv('TREE_SITTER_LIB_PATH')
# if not LIBRARY_PATH:
#     raise ValueError("Environment variable 'TREE_SITTER_LIB_PATH' is not set or is empty.")
PYTHON_LANGUAGE = Language(tspython.language())

class DepBuilder:
    def __init__(self, source_set: set[str], root_directory: str):
        self.source_set: set[str] = source_set
        self.dependency_graph: FileDepGraph = FileDepGraph()
        self.parser: Parser = Parser(PYTHON_LANGUAGE)
        self.visited: set[str] = set()
        self.root_directory: str = root_directory  
        self.dep: ExternalDepResolver = ExternalDepResolver(source_set)

    def _parse_AST(self, node: ASTNode, file_path: str) -> list[str]:
        """Parse the AST node to extract import paths."""
        import_paths = set()
        #TODO: We'll need a more flexible solution for filtering for multiple languages.
        if (node.type == 'import_statement' or node.type == 'import_from_statement'):
            import_target = ImportTarget(node, file_path, self.dep)
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

    
    def build_dependency_graph(self) -> FileDepGraph:
        """Build the source file dependency graph."""
        for file_path in self.source_set:
            if file_path not in self.visited:
                self._build_graph_recursively(file_path)

        return self.dependency_graph
