#simple script to generate an AST for analyzing

from tree_sitter import Language, Parser
from tree_sitter import Tree as ASTree
from dotenv import load_dotenv
import os
from tree_sitter_language_pack import get_language

CURR_LANGUAGE = get_language("python")
FILE_PATH = "trees.py"  # Replace with your file path
OUTPUT_PATH = "ASTExtraction/examples/ast.txt"

def parse_source_code(file_path):
    parser = Parser(CURR_LANGUAGE)

    with open(file_path, 'r') as f:
        source_code = f.read().encode('utf8')

    tree = parser.parse(source_code)
    return tree

def dfs(node, depth=0):
    """Depth-first traversal to print the AST."""
    if node is None:
        return
    with open(OUTPUT_PATH, "a") as f:
        f.write(f"{' ' * depth}{node.type}: {node.text.decode('utf8')}\n")
    for child in node.children:
        dfs(child, depth + 1)

if __name__ == "__main__":
    # Example usage
    file_path = FILE_PATH  # Replace with your file path
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)
    tree = parse_source_code(file_path)
    dfs(tree.root_node)
