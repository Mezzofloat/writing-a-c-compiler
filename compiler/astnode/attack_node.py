from astnode.ASTNode import ASTNode

"""
Definitions for the types of ATTACK nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    instructions: list of instructions (Instructions)
Instructions:
    list of ATTACK instructions (Binary | Unary | Return | Jump | JumpIfZero | JumpIfNotZero | Identifier)
Binary:
    op: operation (Add | Sub | Multiply | Divide | Modulus | Equal | NotEqual | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual)
    src1: left operand (Constant | Variable)
    src2: right operand (Constant | Variable)
    dst: destination of operation (Variable)
Unary:
    op: operation (Complement | Negate | Copy)
    src: operand (Constant | Variable)
    dst: destination of operation (Variable)
Constant:
    [value for the node with this as a child (Int)]
Variable:
    temporary name for this variable (Identifier)
Return:
    expression being returned (Constant | Variable | Unary | Binary)
Jump:
    label to jump to (Identifier)
JumpIfZero, JumpIfNotZero:
    cond: condition to compare to zero (Constant | Variable)
    label: label to jump to (Identifier)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus, Copy:
    -
"""

ATTACK_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"], "instructions": ["Instruction*"]},
    "Instruction": ['Binary', 'Unary', 'Return', 'Jump', 'JumpIfZero', 'JumpIfNotZero', 'Identifier'],
    "Return": ['Unary', 'Binary', 'Variable', 'Constant'],
    "Unary": {"op": ["Complement", "Negate", 'Copy', 'Not'], "src": ["Variable", "Constant"], "dst": ["Variable"]},
    "Binary": {"op": ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'Equal', 'NotEqual', 'LessThan', 'LessOrEqual', 'GreaterThan', 'GreaterOrEqual'], 
                "src1": ["Variable", "Constant"], 
                "src2": ["Variable", "Constant"], 
                "dst": ["Variable"]},
    "Variable": ["Identifier"],
    "Jump": ['Identifier'],
    "JumpIfZero": {"cond": ['Variable', 'Constant'], "label": ['Identifier']},
    "JumpIfNotZero": {"cond": ['Variable', 'Constant'], "label": ['Identifier']},
    "Complement": [],
    "Negate": [],
    "Copy": [],
    "Add": [],
    "Sub": [],
    "Multiply": [],
    "Divide": [],
    "Modulus": [],
    "Not": [],
    "LessThan": [],
    "LessOrEqual": [],
    "GreaterThan": [],
    "GreaterOrEqual": [],
    "Equal": [],
    "NotEqual": []
}

class ATTACK_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        if ident not in ATTACK_node_types:
            if type(ident) is not tuple:
                raise ValueError(f"unexpected node {ident}")
        else:
            vals = ATTACK_node_types[ident]
            if type(vals) is dict:
                for key, ls in vals.items():
                    in_list = False
                    for accepted_type in ls:
                        if accepted_type.endswith('*'):
                            for item in child[key]:
                                if item.ident == accepted_type[:-1] or item.ident[0] == accepted_type[:-1]:
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
                raise TypeError(f"unexpected type of node {ident} in ATTACK_node_types")
        
        self.child = child