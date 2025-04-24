#design - use the graph class for graph design  

#Input - AST, symbol identifiers, 
# - Symbols to track for now: functions, classes, function args
#Output - dependency graph(s), source Set
#Possible challenges - name conflicts (dotted names),
#TODO: Namespace resolution
#TODO: Function signature analysis/handle overloading and inheritance
#TODO: Resolve scoping?

import json
from jsonschema import validate, ValidationError
from typing import Optional, Set, Dict
from tree_sitter import Tree as ASTree
from tree_sitter import Language, Parser
from tree_sitter import TreeCursor
from symbols_data import FunctionSymbol, VariableSymbol, ClassSymbol
from ..graphs import DepGraph

#Initialize symbols_map schema for validation reference
SYMBOLS_MAP_PATH = "symbols_map.json"
VALIDATION_SCHEMA_PATH = "validation_schema.json"

class SymbolParser:
    #globals
    language_map: Dict
    valid_schema: Dict
    def __init__(self, language: Optional[str] = None):
        self.language: str = language
        self.symbol_words: Dict = {}
        self.functions: Set[str] = set()
        self.classes: Set[str] = set()
        self.functions_map: Dict[str, FunctionSymbol] = {}
        self.variables_map: Dict[str, VariableSymbol] = {}
        self.classes_map: Dict[str, ClassSymbol] = {}
        self.dependency_graph: DepGraph = DepGraph()

        #load the language map
        if SymbolParser.language_map is None:
            with open(SYMBOLS_MAP_PATH, "r") as file:
                file_contents = file.read()
                self.language_map = json.loads(file_contents)

        #load the validation schema
        if SymbolParser.valid_schema is None:
            with open(VALIDATION_SCHEMA_PATH, "r") as file:
                file_contents = file.read()
                self.valid_schema = json.loads(file_contents)

        if language:
            self.set_language(language)
        

    def set_language(self, language: str) -> Dict:
        self.language = language
        #load from language map, return the mapping of keywords to symbols
        if language in SymbolParser.language_map:
            self.symbol_words = SymbolParser.language_map[language]
            #validate the schema
            try:
                validate(instance=self.symbol_words, schema=self.valid_schema)
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

        
    def parse(self, AST: ASTree) -> None:
        #A recursive walk through the AST - utilize tree sitter cursors
        cursor = AST.cursor()







