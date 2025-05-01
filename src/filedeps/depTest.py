from .. import trees
from .. import graphs
from . import dep_builder
from . import crawler

import os
import time

TEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test/tensorflow")
if __name__ == "__main__":
    #test usage - crawl test directory, obtain directory structure + set of files, obtain dependency graph
    start=time.time()
    prev = start
    crawler = crawler.Crawler(TEST_DIR)
    directory_tree = crawler.build_directory_tree()
    source_dict = crawler.source_dict
    print(f"Source set: {source_dict}")
    print(f"Testing on {TEST_DIR}")
    print(f"Directory tree built in {time.time() - prev:.2f} seconds")
    prev = time.time()
    #debug
    #directory_tree.tree.traverse()
    

    #build dependency graph using the source set

    dep_builder = dep_builder.DepBuilder(source_dict[".cc"], TEST_DIR, "cpp")
    dep_graph = dep_builder.build_dependency_graph()
    dep_graph.print_graph()
    print(f"Dependency graph built in {time.time() - prev:.2f} seconds")
    prev = time.time()
    dep_builder.log_unresolved_imports()
    # dep_graph.visualize()
    # print(f"Visualized in {time.time() - prev:.2f} seconds")
