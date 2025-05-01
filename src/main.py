import os
import json
import time


from .graphs import DepGraph
from .ast_extraction import symbols_parser
from tree_sitter_language_pack import get_parser
from . import trees
from .filedeps import crawler
from .filedeps import dep_builder

TEST_DIR = os.path.join(os.path.dirname(__file__), "test/requests")
if __name__ == "__main__":
    crawler = crawler.Crawler(TEST_DIR)
    directory_tree = crawler.build_directory_tree()
    source_set = crawler.source_set

    #debug
    #directory_tree.tree.traverse()


    #build dependency graph using the source set
    dep_builder = dep_builder.DepBuilder(source_set, TEST_DIR)
    dep_graph = dep_builder.build_dependency_graph()
    dep_builder.log_unresolved_imports()
    #dep_graph.print_graph()
    # dep_graph.visualize()
    dep_graph.print_source_set()
    #Generate ASTs of all source files
    
    symParse = symbols_parser.SymbolParser("python")
    nameToSyms = {}
    astparser = get_parser("python")
    numFiles = len(source_set)
    count = 0
    start=time.time()
    prevTime = start
    for file in source_set:
        symParse = symbols_parser.SymbolParser("python")
        with open(file, "r") as f:
            code = f.read()
        try:
            tree = astparser.parse(bytes(code, "utf8"))
            symParse.parse(tree)
            nameToSyms[file] = symParse
            print(f"Parsed {file} in {time.time()-prevTime:.2f} seconds")
            prevTime = time.time()
        except:
            print(f"Failed to parse {file}")
            count += 1
            continue
    print(f"Parsed all files in {time.time()-start:.2f} seconds")
    print(f"Failed to parse {count} / {numFiles} files")

