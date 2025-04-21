import sys
import tree_sitter
from tree_sitter import Language, Parser
from dotenv import load_dotenv
import os

load_dotenv()
LIBRARY_PATH = os.getenv('TREE_SITTER_LIB_PATH')
PYTHON_LANGUAGE = Language(LIBRARY_PATH, 'python')

def parse_source_code(file_path) -> tree_sitter.Tree:
    parser = Parser()
    parser.set_language(PYTHON_LANGUAGE)

    with open(file_path, 'r') as f:
        source_code = f.read().encode('utf8')

    tree = parser.parse(source_code)
    return tree
