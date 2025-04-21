#simple script to generate an AST for analyzing

from tree_sitter import Language, Parser
from tree_sitter import Tree as ASTree
from dotenv import load_dotenv
import os
import tree_sitter_python as tspython

PYTHON_LANGUAGE = Language(tspython.language())
FILE_PATH = "test/requests/src/requests/__init__.py"  # Replace with your file path
def parse_source_code(file_path):
    parser = Parser(PYTHON_LANGUAGE)

    with open(file_path, 'r') as f:
        source_code = f.read().encode('utf8')

    tree = parser.parse(source_code)
    return tree

def dfs(node, depth=0):
    """Depth-first traversal to print the AST."""
    if node is None:
        return
    with open("ast.txt", "a") as f:
        f.write(f"{' ' * depth}{node.type}: {node.text.decode('utf8')}\n")
    for child in node.children:
        dfs(child, depth + 1)

if __name__ == "__main__":
    # Example usage
    file_path = FILE_PATH  # Replace with your file path
    tree = parse_source_code(file_path)
    dfs(tree.root_node)
