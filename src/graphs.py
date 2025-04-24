from graphviz import Digraph
import matplotlib.pyplot as plt

class DepGraph:
    def __init__(self):
        self.dependencies: dict[str, set[str]] = {} # Maps a file to its dependencies - str
        self.dependents: dict[str, set[str]] = {}   # Maps a file to its dependents
        self.source_set: set[str] = set()  # Set of all source files

    def add_dependency(self, file: str, dependency: str) -> None:
        # Add dependency to the graph
        if file not in self.dependencies:
            self.dependencies[file] = set()
        if dependency not in self.dependencies:
            self.dependencies[dependency] = set()
        if dependency not in self.dependencies[file]:
            self.dependencies[file].add(dependency)

        # Update dependents
        if dependency not in self.dependents:
            self.dependents[dependency] = set()
        self.dependents[dependency].add(file)

        #update source set
        self.source_set.add(file)
        self.source_set.add(dependency)

    def get_dependencies(self, file:str) -> set[str]:
        # Return the list of dependencies for a file
        return self.dependencies.get(file, [])

    def get_dependents(self, file:str) -> set[str]:
        # Return the list of dependents for a file
        return self.dependents.get(file, [])

    def get_all_dependencies(self) -> dict[str, set[str]]:
        # Return the entire dependency graph
        return self.dependencies
    
    def print_source_set(self) -> None:
        #for debugging mostly
        print(self.source_set)
    
    def print_graph(self) -> None:
        """Print the dependency graph."""
        for file_path, dependencies in self.dependencies.items():
            print(f"{file_path}: {', '.join(dependencies)}")
            print("\n")

    """NetworkX for quick visuals"""
    def visualize(self):
        dot = Digraph()

        for node in self.dependencies:
            dot.node(node)
            for neighbor in self.dependencies[node]:
                dot.edge(neighbor, node)

        dot.render('graph', format='png', view=True)

        