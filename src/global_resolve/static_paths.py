

class StaticPathResolver:
    """class to resolve arbitrary-depth dependencies for languages with static-path import models"""
    """Languages supported: python"""

    #Input: 
    def __init__(self, dep_graph, source_set):