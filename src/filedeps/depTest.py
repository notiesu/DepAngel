import trees
import graphs
import dep_builder
import crawler

import os

TEST_DIR = "test/requests"
if __name__ == "__main__":
    #test usage - crawl test directory, obtain directory structure + set of files, obtain dependency graph
    crawler = crawler.Crawler(TEST_DIR)
    directory_tree = crawler.build_directory_tree()
    source_set = crawler.source_set

    #debug
    #directory_tree.tree.traverse()
    

    #build dependency graph using the source set
    dep_builder = dep_builder.DepBuilder(source_set, TEST_DIR)
    dep_graph = dep_builder.build_dependency_graph()
    dep_graph.print_graph()
    dep_builder.log_unresolved_imports()
    dep_graph.visualize()
