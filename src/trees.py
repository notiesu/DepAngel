# Base tree
class TreeNode:
    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.children = []

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def remove_child(self, child_node):
        self.children = [child for child in self.children if child != child_node]

    def traverse(self, depth=0):
        #incorporate tabbing
        print("\t" * depth, end="")
        print(self.value)
        for child in self.children:
            child.traverse(depth + 1)

class Tree:
    def __init__(self, root_node: str):
        self.root = TreeNode(root_node)

    def traverse(self):
        self.root.traverse()

    def add_node(self, parent_node, child_node):
        parent_node.add_child(child_node)

    def remove_node(self, parent_node, child_node):
        parent_node.remove_child(child_node)

# inheriting trees

class DirFileNode(TreeNode):
    def __init__(self, value, parent=None, isFile=False):
        super().__init__(value, parent)
        self.isFile = isFile

# Directory Tree - Using DirectoryNode
class DirFileTree:
    def __init__(self, root_value):
        self.root = DirFileNode(root_value)
        self.tree = Tree(self.root)
        
