import os
import json
import time

from typing import Dict, Set, Optional


from .graphs import DepGraph
from .ast_extraction import symbols_parser
from tree_sitter_language_pack import get_parser
from . import trees
from .filedeps import crawler
from .filedeps import dep_builder
from .ast_extraction.symbols_data import GenSymbol

TEST_DIR = os.path.join(os.path.dirname(__file__), "test/tensorflow/tensorflow/python")
LANGUAGE = "python"

if __name__ == "__main__":
    crawlerObj = crawler.Crawler(TEST_DIR)
    directory_tree = crawlerObj.build_directory_tree()
    source_dict = crawlerObj.source_dict #structure is {".py": set(), ".js": set(), ...}
    crawlerObj.normalize_source_paths()
    #debug
    #directory_tree.tree.traverse()


    #build dependency graph using the source set
    #try for cpp
    
    start=time.time()
    prevTime = start
    depBuilder = dep_builder.DepBuilder(source_dict[".py"], TEST_DIR, LANGUAGE)
    dep_graph = depBuilder.build_dependency_graph()
    print("dependencies built")
    # depBuilder.log_unresolved_imports()
    #dep_graph.print_graph()
    # dep_graph.visualize()
    dep_graph.print_source_set()
    #Generate ASTs of all source files

    nameToSyms = {}
    astparser = get_parser(LANGUAGE)
    numFiles = len(depBuilder.source_set)
    count = 0
    prevTime = time.time()

    #Symbol table for global resolution
    symbolTable: Dict[str, GenSymbol] = {}

    for file in depBuilder.source_set:
        print(f"Parsing: {file}")
        symParser = symbols_parser.SymbolParser(LANGUAGE)
        #fully qualify file
        file_full_path = os.path.join(TEST_DIR, file)
        with open(file_full_path, "r") as f:
            code = f.read()
        # try:
        tree = astparser.parse(bytes(code, "utf8"))
        symParser.parse(tree)
        symParser.build_dependency_graph()
        nameToSyms[file] = symParser
        print(f"Parsed {file} in {time.time()-prevTime:.2f} seconds")
        prevTime = time.time()
        
        #add to symbol table
        for func in symParser.functions_map:
            #file is relative to project root
            full_path = f"{file}.{func}"
            symbolTable[full_path] = symParser.functions_map[func]
        for cls in symParser.classes_map:
            full_path = f"{file}.{cls}"
            symbolTable[full_path] = symParser.classes_map[cls]
    print(f"Parsed all files in {time.time()-start:.2f} seconds")
    print(f"Failed to parse {count} / {numFiles} files")
    
    #print symbol table
    # print("All collected symbols")
    # for key in symbolTable:
    #     print(f"{key}: {symbolTable[key].name} - {type(symbolTable[key])}")

    #run through symbols again, for each dependent of a symbol, try to resolve
    
    for file, symParser in nameToSyms.items():
        symParser.dependency_graph.visualize()
        symParser.log_unresolved_imports()
        input("Press Enter to continue...")

    #Featurization

    
    #TODO: Attempt a global artbitrary-depth resolve - for now, nodes only connect to their same level (file to file, symbols  to symbols)

