#Set of methods to deduce node type and find key attributes during an AST recursive walk
from tree_sitter import Language, Parser
from tree_sitter import tree as ASTree
from tree_sitter import Node as ASTNode

#Pass in node and symbol_words instances, parse the tree

def get_node_type(node: ASTNode, keywords: dict) -> str:
    return keywords.get(node.type, "unknown")

#do case work based on node type
def get_key_attributes(node: ASTNode, keywords: dict) -> dict:
    
    
def extract_function_attributes(node: ASTNode) -> dict:
    # Extract function-specific attributes
    function_name = node.child_by_field_name('name')
    parameters = node.child_by_field_name('parameters')
    return {
        'name': function_name.text.decode('utf-8') if function_name else None,
        'parameters': [param.text.decode('utf-8') for param in parameters.children] if parameters else []
    }
