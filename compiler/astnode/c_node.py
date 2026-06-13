from astnode.ASTNode import ASTNode

"""
Definitions for the types of C nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    body: body of the function (Return)
Identifier: 
    [name for the node with this as a child (String)]
Return:
    expression being returned (Constant | Unary | Binary)
Constant:
    [value for the node with this as a child (Int)]
Unary:
    op: unary operator that acts on the inner expression (Complement | Negate)
    inner_exp: the expression that is being acted on (Constant | Unary | Binary)
Binary:
    op: binary operator that acts on the left and right operands (Add | Sub | Multiply | Divide | Modulus
                                                                | And | Or | Equal | NotEqual | LessThan
                                                                | LessOrEqual | GreaterThan | GreaterOrEqual)
    left: left operand (Constant | Unary | Binary)
    right: right operand (Constant | Unary | Binary)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus, Not, And, Or, etc.:
    -
"""

C_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"], "body": ["Return"]},
    "Return": ['Constant', 'Unary', 'Binary'],
    "Unary": {"op": ["Complement", "Negate", "Not"], "inner_exp": ["Constant", "Unary", "Binary"]},
    "Binary": {"op": ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'And', 'Or', 'LessThan', 'GreaterThan', 'Equal', 'NotEqual', 'LessOrEqual', 'GreaterOrEqual'], 
                "left": ["Constant", "Unary", "Binary"], 
                "right": ["Constant", "Unary", "Binary"]},
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
    "Not": []
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
                    if child[key].ident not in ls and child[key].ident[0] not in ls:
                        raise ValueError(f"{key} should be in {ls} but got {child[key].ident} for node {ident}")
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
        