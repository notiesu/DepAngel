#design - use the graph class for graph design  

#Input - AST, symbol identifiers, 
# - Symbols to track for now: functions, classes, function args
#Output - dependency graph(s), source Set
#Possible challenges - name conflicts (dotted names),
#TODO: Namespace resolution
#TODO: Function signature analysis/handle overloading and inheritance
#TODO: Resolve scoping?

import json
import os 
from jsonschema import validate, ValidationError
from typing import Optional, Set, Dict, List
from tree_sitter import Tree as ASTree
from tree_sitter import Node as ASTNode
from tree_sitter import Language, Parser
from tree_sitter import TreeCursor
from .symbols_data import FunctionSymbol, VariableSymbol, ClassSymbol, GenSymbol
from ..graphs import DepGraph

#Initialize symbols_map schema for validation reference
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
SYMBOLS_MAP_PATH = CURR_DIR + "/symbols_map.json"
VALIDATION_SCHEMA_PATH = CURR_DIR + "/validation_schema.json"

class SymbolParser:
    #globals
    language_map: Dict = {}
    valid_schema: Dict = {}
    def __init__(self, language: Optional[str] = None):
        self.language: str = language
        self.symbol_paths: Dict = {}
        self.functions: Set[str] = set()
        self.classes: Set[str] = set()
        self.functions_map: Dict[str, FunctionSymbol] = {}
        self.variables_map: Dict[str, VariableSymbol] = {}
        self.classes_map: Dict[str, ClassSymbol] = {}
        self.dependency_graph: DepGraph = DepGraph()


        #load the language map
        if not SymbolParser.language_map:
            with open(SYMBOLS_MAP_PATH, "r") as file:
                file_contents = file.read()
                SymbolParser.language_map = json.loads(file_contents)

        #load the validation schema
        if not SymbolParser.valid_schema:
            with open(VALIDATION_SCHEMA_PATH, "r") as file:
                file_contents = file.read()
                SymbolParser.valid_schema = json.loads(file_contents)

        if language:
            self.set_language(language)

        #print(SymbolParser.language_map)

    def set_language(self, language: str) -> Dict:
        self.language = language
        #load from language map, return the mapping of keywords to symbols
        if language in SymbolParser.language_map:
            self.symbol_paths = SymbolParser.language_map[language]
            #validate the schema
            try:
                validate(instance=self.symbol_paths, schema=self.valid_schema)
                print(f"Validation successful for {language} symbols map.")
            except ValidationError as e:
                print(f"Validation error: {e.message}")
                raise
        else:
            raise ValueError(f"Language '{language}' not supported.")
        
    def refresh(self) -> None:
        with open(SYMBOLS_MAP_PATH, "r") as file:
            file_contents = file.read()
            SymbolParser.language_map = json.loads(file_contents)

        with open(VALIDATION_SCHEMA_PATH, "r") as file:
            file_contents = file.read()
            SymbolParser.valid_schema = json.loads(file_contents)

    def _follow_path(self, curr_node: ASTNode, path: List[str], ind: int, results: Set[str]) -> None:
        # Input - path (arr[str]) outlined in the symbol_paths 
        # Output - 
        #approach - recurse when wildcard, otherwise check if node type matches, move ind. Base when ind == len(path)
        if (ind == len(path)):
            results.add(curr_node.text.decode("utf-8"))
            return
        node_type = curr_node.type
        for child in curr_node.children:
            if child.type == path[ind]:
                #check if the child is a wildcard
                self._follow_path(child, path, ind + 1, results)
            elif path[ind] == "**":
                #if wildcard, check both moving forward and staying
                self._follow_path(child, path, ind + 1, results)
                self._follow_path(child, path, ind, results)
        #Go to child

    def _populate_func_symbol(self, symbol: GenSymbol, node: ASTNode) -> None:
        #fields: name, args, return_type, calls
        symbol.return_type = None 
        names = set() #temp set to store names
        self._follow_path(node, self.symbol_paths["function"]["name_path"], 0, names)
        symbol.name = next(iter(names))
        self._follow_path(node, self.symbol_paths["function"]["args_path"], 0, symbol.args)
        self._follow_path(node, self.symbol_paths["function"]["calls_path"], 0, symbol.calls)

    def _populate_class_symbol(self, symbol: GenSymbol, node: ASTNode) -> None:
        #fields: name, base_classes, init_args, methods, attributes
        #paths: name_path, base_classes_path, init_args_path, methods_path, attributes_path
        names = set()
        self._follow_path(node, self.symbol_paths["function"]["name_path"], 0, names)
        symbol.name = next(iter(names))
        self._follow_path(node, self.symbol_paths["class"]["methods_path"], 0, symbol.methods)
        self._follow_path(node, self.symbol_paths["class"]["attributes_path"], 0, symbol.attributes)
        self._follow_path(node, self.symbol_paths["class"]["base_classes_path"], 0, symbol.base_classes)
        #self._follow_path(node, self.symbol_paths["class"]["init_args_path"], 0, symbol.init_args)
    

    def _traverse(self, cursor: TreeCursor, parent_symbol: Optional[GenSymbol] = None) -> None:
        node = cursor.node
        node_type = node.type

        # Process node
        if node_type == self.symbol_paths.get("function").get("def_keyword"):
            sym = FunctionSymbol()
            self._populate_func_symbol(sym, node)
            self.functions_map[sym.name] = sym 
            self.functions.add(sym.name)

        elif node_type == self.symbol_paths.get("class").get("def_keyword"):
            sym = ClassSymbol()
            self._populate_class_symbol(sym, node)
            self.classes_map[sym.name] = sym
            self.classes.add(sym.name)

        # Recurse into children
        if cursor.goto_first_child():
            while True:
                self._traverse(cursor, parent_symbol)
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

    def parse(self, AST: ASTree) -> None:
        cursor = AST.root_node.walk()
        self._traverse(cursor)

    def __str__(self) -> str:
        return f"Language: {self.language}, Functions: {self.functions}, Classes: {self.classes}"