from graphviz import Digraph
import matplotlib.pyplot as plt

class DepGraph:
    def __init__(self):
        self.dependencies: dict[str, set[str]] = {} # Maps a name to its dependencies - str
        self.dependents: dict[str, set[str]] = {}   # Maps a name to its dependents
        self.source_set: set[str] = set()  # Set of all source names

    def add_dependency(self, name: str, dependency: str) -> None:
        # Add dependency to the graph
        if name not in self.dependencies:
            self.dependencies[name] = set()
        if dependency not in self.dependencies:
            self.dependencies[dependency] = set()
        if dependency not in self.dependencies[name]:
            self.dependencies[name].add(dependency)

        # Update dependents
        if dependency not in self.dependents:
            self.dependents[dependency] = set()
        self.dependents[dependency].add(name)

        #update source set
        self.source_set.add(name)
        self.source_set.add(dependency)

    def get_dependencies(self, name:str) -> set[str]:
        # Return the list of dependencies for a name
        return self.dependencies.get(name, [])

    def get_dependents(self, name:str) -> set[str]:
        # Return the list of dependents for a name
        return self.dependents.get(name, [])

    def get_all_dependencies(self) -> dict[str, set[str]]:
        # Return the entire dependency graph
        return self.dependencies
    
    def print_source_set(self) -> None:
        #for debugging mostly
        print(self.source_set)
    
    def print_graph(self, name: str = None) -> None:
        if name is None:
            for name_path, dependencies in self.dependencies.items():
                print(f"{name_path}: {', '.join(dependencies)}")
                print("\n")
        else:
            if name in self.dependencies:
                print(f"{name}: {', '.join(self.dependencies[name])}")
            else:
                print(f"{name} not found in the graph.")

    """NetworkX for quick visuals"""
    def visualize(self, name: str = None) -> None:
        """Visualize the dependency graph. If a name is provided, visualize only the subgraph that includes the given name."""
        dot = Digraph()

        if name is None:
            # Visualize the entire graph
            for node in self.dependencies:
                dot.node(node)
                for neighbor in self.dependencies[node]:
                    dot.edge(neighbor, node)
        else:
            # Visualize the subgraph including the given name
            stack = [name]
            visited = set()
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    dot.node(node)
                    if node in self.dependencies:
                        for neighbor in self.dependencies[node]:
                            dot.edge(neighbor, node)
                            stack.append(neighbor)

        dot.render('graph', format='png', view=True)

        