from dataclasses import dataclass, field
from typing import Optional, Set, Dict

#TODO: Implement scope resolution and variable dependencies. Could blow up code complexity though.
#TODO: encode node data for feaatures
@dataclass
class GenSymbol:
    name: str = ""

@dataclass
class FunctionSymbol(GenSymbol):
    args: Set[str] = field(default_factory=set)  
    calls: Set[str] = field(default_factory=set)
    class_deps: Set[str] = field(default_factory=set)
    return_type: Optional[str] = None
    #TODO: Add all below attributes to the ast parser
    source_file: Optional[str] = None

@dataclass
class VariableSymbol(GenSymbol):
    var_type: str = ""
    value: Optional[str] = None

@dataclass
class ClassSymbol(GenSymbol):
    methods: Set[str] = field(default_factory=set)
    func_deps: Set[str] = field(default_factory=set)
    base_classes: Set[str] = field(default_factory=set)
    attributes: Set[str] = field(default_factory=set)
    init_args: Set[str] = field(default_factory=set)
    source_file: Optional[str] = None




