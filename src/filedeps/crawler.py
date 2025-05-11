import os
from .. import trees

#input - directory
#otuput - directory tree, source file dependency tree
#approach - crawl through directories first, then use the output to build source trees

#TODO: We can make this cleaner, but for now we'll use a list of supported extensions
SUPPORTED_EXTENSIONS = set([".py", ".cpp", ".c", ".cc"])
class Crawler:
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.directory_tree = trees.DirFileTree(root_directory)
        #bucket the source set by extension
        self.source_dict: dict[str, set] = {}

    def normalize_source_paths(self):
        # Normalize the paths in the source_dict to be relative to the root directory
        for ext, paths in self.source_dict.items():
            normalized_paths = {os.path.relpath(path, self.root_directory) for path in paths}
            self.source_dict[ext] = normalized_paths
    
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
                ext = os.path.splitext(entry)[1]
                if ext in SUPPORTED_EXTENSIONS:
                    if ext not in self.source_dict:
                        self.source_dict[ext] = set()
                    self.source_dict[ext].add(entry_path)
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

