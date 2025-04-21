import os
import trees

#input - directory
#otuput - directory tree, source file dependency tree
#approach - crawl through directories first, then use the output to build source trees

class Crawler:
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.directory_tree = trees.DirFileTree(root_directory)
        self.source_set = set()
    
    def _build_tree_recursively(self, current_path, current_node):
        for entry in os.listdir(current_path):
            entry_path = os.path.join(current_path, entry)
            
            if os.path.isdir(entry_path):
                new_node = trees.DirFileNode(entry_path, parent=current_node, isFile=False)
                current_node.add_child(new_node)
                self._build_tree_recursively(entry_path, new_node)
            else:
                new_node = trees.DirFileNode(entry_path, parent=current_node, isFile=True)
                # add to source set if extension is .py
                if entry.endswith('.py'):
                    self.source_set.add(entry_path)
                current_node.add_child(new_node)

    def build_directory_tree(self):
        self._build_tree_recursively(self.root_directory, self.directory_tree.tree.root)
        return self.directory_tree

    def debug(self):
        print("Directory Tree:")
        self.directory_tree.tree.traverse()

if __name__ == "__main__":
    root_directory = "test/requests"
    crawler = Crawler(root_directory)
    directory_tree = crawler.build_directory_tree()
    crawler.debug()

