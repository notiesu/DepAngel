import os
import json
import time


from .graphs import DepGraph
from .ast_extraction import symbols_parser
from tree_sitter_language_pack import get_parser
from . import trees
from .filedeps import crawler
from .filedeps import dep_builder

TEST_DIR = os.path.join(os.path.dirname(__file__), "test/tensorflow/tensorflow/cc")
if __name__ == "__main__":
    crawler = crawler.Crawler(TEST_DIR)
    directory_tree = crawler.build_directory_tree()
    source_dict = crawler.source_dict #structure is {".py": set(), ".js": set(), ...}

    #debug
    #directory_tree.tree.traverse()


    #build dependency graph using the source set
    #try for cpp
    
    start=time.time()
    prevTime = start
    dep_builder_cpp = dep_builder.DepBuilder(source_dict[".cc"], TEST_DIR, "cpp")
    dep_graph = dep_builder_cpp.build_dependency_graph()
    print("dependencies built")
    # dep_builder_cpp.log_unresolved_imports()
    #dep_graph.print_graph()
    # dep_graph.visualize()
    dep_graph.print_source_set()
    #Generate ASTs of all source files

    nameToSyms = {}
    astparser = get_parser("cpp")
    numFiles = len(dep_builder_cpp.source_set)
    count = 0
    prevTime = time.time()
    for file in dep_builder_cpp.source_set:
        print(f"Parsing: {file}")
        symParser = symbols_parser.SymbolParser("cpp")
        with open(file, "r") as f:
            code = f.read()
        # try:
        tree = astparser.parse(bytes(code, "utf8"))
        symParser.parse(tree)
        symParser.build_dependency_graph()
        nameToSyms[file] = symParser
        print(f"Parsed {file} in {time.time()-prevTime:.2f} seconds")
        prevTime = time.time()
        # except:
        #     print(f"Failed to parse {file}")
        #     count += 1
        #     continue
    print(f"Parsed all files in {time.time()-start:.2f} seconds")
    print(f"Failed to parse {count} / {numFiles} files")
    
    for file, symParser in nameToSyms.items():
        symParser.dependency_graph.visualize()
        symParser.log_unresolved_imports()
        input("Press Enter to continue...")
    #TODO: Attempt a global artbitrary-depth resolve - for now, nodes only connect to their same level (file to file, symbols  to symbols)

