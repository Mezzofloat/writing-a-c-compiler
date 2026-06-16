from astnode.ASTNode import ASTNode

"""
C_node_types is a dictionary mapping the name of a type of C node to either a list of possible children or a dictionary mapping the name of a child to a list of possible types for that child. Depending on the value, the node will have different structures:
Empty list: the node should have no children
List: the node should have one child in the list of possible children
Dictionary: the node should have one child for each key in the dictionary, and the child for each key should be in the list of possible types for that key
"""

expr = ['Constant', 'Unary', 'Binary', 'Var', 'Assignment']
expr_optional = ['Constant?', 'Unary?', 'Binary?', 'Var?', 'Assignment?']

C_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"], "body": ["BlockItem*"]},
    "Return": expr,
    "Unary": {"op": ["Complement", "Negate", "Not"], "inner_exp": expr},
    "Binary": {"op": ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'And', 'Or', 'LessThan', 'GreaterThan', 'Equal', 'NotEqual', 'LessOrEqual', 'GreaterOrEqual'], 
                "left": expr, 
                "right": expr},
    "Var": ["Identifier"],
    "Assignment": {"lvalue": expr, "exp": expr},
    "Statement": ['Constant', 'Unary', 'Binary', 'Var', 'Assignment', 'Return', 'Null'],
    "Declaration": {"name": ["Identifier"], "init": expr_optional},
    "BlockItem": ["Statement", "Declaration"],
    "Complement": [],
    "Negate": [],
    "Add": [],
    "Sub": [],
    "Multiply": [],
    "Divide": [],
    "Modulus": [],
    "And": [],
    "Or": [],
    "Equal": [],
    "NotEqual": [],
    "LessThan": [],
    "GreaterThan": [],
    "LessOrEqual": [],
    "GreaterOrEqual": [],
    "Not": [],
    "Null": []
}

class C_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        if ident not in C_node_types:
            if type(ident) is not tuple:
                raise ValueError(f"unexpected node {ident}")
        else:
            vals = C_node_types[ident]
            if type(vals) is dict:
                for key, ls in vals.items():
                    in_list = False
                    for accepted_type in ls:
                        if accepted_type.endswith('*'):
                            if len(child[key]) == 0:
                                in_list = True
                            for item in child[key]:
                                if item.ident == accepted_type[:-1] or item.ident[0] == accepted_type[:-1]:
                                    in_list = True
                        elif accepted_type.endswith('?'):
                            if key not in child or child[key] is None:
                                in_list = True
                            elif child[key].ident == accepted_type[:-1] or child[key].ident[0] == accepted_type[:-1]:
                                in_list = True
                        else:
                            if child[key].ident == accepted_type or child[key].ident[0] == accepted_type:
                                in_list = True
                    if not in_list:
                        raise ValueError(f"{key} should be in {ls} but got {child[key]} for node {ident}")
            elif type(vals) is list:
                if len(vals) == 0:
                    if child is not None:
                        raise ValueError(f"unexpected child {child} for node {ident}")
                else:
                    if child.ident not in vals and child.ident[0] not in vals:
                        raise ValueError(f"unexpected child {child} for node {ident}")
            else:
                raise TypeError(f"unexpected type of node {ident} in C_node_types")

        self.child = child
        