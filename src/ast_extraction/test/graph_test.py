from .. import symbols_parser
import os
import json
from tree_sitter import Parser, Tree
from tree_sitter_language_pack import get_parser
from ...graphs import DepGraph
import ast

TEST_FILE = os.path.join(os.path.dirname(__file__), "trt_convert.py")
from tree_sitter_language_pack import get_parser

if __name__ == "__main__":
    # Initialize simple parser instance, run on a test file
    parser = symbols_parser.SymbolParser("python")
    #Generate AST
    ASTGen = get_parser("python")
    with open(TEST_FILE, "r") as file:
        code = file.read()
    tree = ASTGen.parse(bytes(code, "utf8"))
    parser.parse(tree)

    #Create graph
    graph = DepGraph()
    #add nodes
    for func in parser.functions_map:
        for call in parser.functions_map[func].calls:
            graph.add_dependency(func, call)
    for cls in parser.classes_map:
        for base in parser.classes_map[cls].base_classes:
            graph.add_dependency(cls, base)
        for method in parser.classes_map[cls].methods:
            graph.add_dependency(cls, method)
    print(parser.classes_map["_TRTEngineResource"].methods)
    #NOTE: Visualization is the performance bottleneck 
    #self is being recognized as a base class
    graph.visualize("_TRTEngineResource")
    
