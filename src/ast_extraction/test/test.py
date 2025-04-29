from .. import symbols_parser
import os
import json
from tree_sitter import Parser, Tree
from tree_sitter_language_pack import get_parser
import ast

TEST_FILE = os.path.join(os.path.dirname(__file__), "test/trt_convert.py")

def get_all_function_names(file_path):
    with open(file_path, "r") as file:
        source_code = file.read()
    tree = ast.parse(source_code)
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

def get_all_class_names(file_path):
    with open(file_path, "r") as file:
        source_code = file.read()
    tree = ast.parse(source_code)
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

if __name__ == "__main__":
    # Initialize simple parser instance, run on a test file
    parser = symbols_parser.SymbolParser("python")
    #Generate AST
    ASTGen = get_parser("python")
    with open(TEST_FILE, "r") as file:
        code = file.read()
    tree = ASTGen.parse(bytes(code, "utf8"))
    parser.parse(tree)
    # print(parser)
    
    # #ground truth - python ast library
    # print(get_all_function_names(TEST_FILE))

    #Diff check - functions
    for func in parser.functions_map:
        if func not in get_all_function_names(TEST_FILE):
            print(f"Function {func} not found in ground truth")

    for func in get_all_function_names(TEST_FILE):
        if func not in parser.functions_map:
            print(f"Function {func} not found in parser")

    #Diff check - classes
    for cls in parser.classes_map:
        if cls not in get_all_class_names(TEST_FILE):
            print(f"Class {cls} not found in ground truth")

    for cls in get_all_class_names(TEST_FILE):
        if cls not in parser.classes_map:
            print(f"Class {cls} not found in parser")

    #print symbol args
    for func in parser.functions_map:
        print(f"Function {func} args: {parser.functions_map[func].args}")
        print("\n")
        #print(f"Function {func} calls: {parser.functions_map[func].calls}")
        #print only function
        print("\n")
        print(f"Function {func} class_deps: {parser.functions_map[func].class_deps}")
        print("\n")
        print(f"Function {func} return_type: {parser.functions_map[func].return_type}")
        print("*****************************************\n")
        
    for cls in parser.classes_map:
        #class symbol: methods, attributes, base_classes, init_args
        print(f"Class {cls} attributes: {parser.classes_map[cls].attributes}")
        print("\n")
        print(f"Class {cls} methods: {parser.classes_map[cls].methods}")
        print("\n")
        print(f"Class {cls} base_classes: {parser.classes_map[cls].base_classes}")
        print("\n")
        print(f"Class {cls} init_args: {parser.classes_map[cls].init_args}")
        print("\n")
        print("*****************************************\n")
