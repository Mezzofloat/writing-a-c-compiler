from astnode.ASTNode import ASTNode

"""
Definitions for the types of x86 nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    instructions: list of instructions (Instructions)
Identifier:
    [name for the node with this as a child (String)]
Instructions:
    list of assembly instructions (Binary | Unary | Mov | Sext | Ret | Cmp | Jmp | JmpCC | SetCC | Identifier)
Binary:
    op: binary operation being applied to destination (Add | Sub | Mult)
    src: left operand (Stack | Register | Imm)
    dst: right operand, and destination of operation (Register | Stack)
    (unable to operate on Stack and Stack)
Unary:
    op: unary operation being applied to destination (Not | Neg | Div)
    dst: destination of operation (Register | Stack)
    (for Div, dst is the dividend and EDX:EAX is destination)
Mov:
    src: source from which destination gets its value (Stack | Register | Imm)
    dst: destination, which is set to the value in source (Register | Stack)
    (unable to move from Stack to Stack)
Stack:
    [address on the stack that the node with this as a child is using (Int)]
    (Pseudo is ultimately converted to this)
Register:
    [register that the node with this as a child is referring to (String)]
Imm:
    [value for the node with this as a child (Int)]
Cmp:
    left: left comparand (Imm, Register, Pseudo, Stack)
    right: right comparand (Imm, Register, Pseudo, Stack)
Jmp:
    label to jump to (Identifier)
JmpCC:
    cond: condition to jump if (E | NE | G | GE | L | LE)
    label: label to jump to (Identifier)
SetCC:
    cond: condition to set byte to (E | NE | G | GE | L | LE)
    dst: byte to set (Register)
Ret, Not, Neg, Add, Sub, Mult, Div, Sext (sign-extend), E, NE, G, GE, L, LE:
    -
"""

x86_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"], "instructions": ["Instruction*"]},
    "Instruction": ['Binary', 'Unary', 'Mov', 'Sext', 'Ret', 'Cmp', 'Jmp', 'JmpCC', 'SetCC', 'Identifier', 'AllocateStack'],
    "Binary": {"op": ['Add', 'Sub', 'Mult'],
               "src": ['Pseudo', 'Stack', 'Register', 'Imm'],
               "dst": ['Pseudo', 'Stack', 'Register']},
    "Unary": {"op": ["Not", "Neg", "Div"],
              "dst": ['Pseudo', 'Stack','Register','Imm']},
    "Cmp": {"left": ['Pseudo', 'Stack', 'Register', 'Imm'],
            "right": ['Pseudo', 'Stack', 'Register', 'Imm']},
    "Jmp": ['Identifier'],
    "JmpCC": {"cond": ['E', 'NE', 'G', 'GE', 'L', 'LE'],
              "label": ['Identifier']},
    "SetCC": {"cond": ['E', 'NE', 'G', 'GE', 'L', 'LE'],
              "dst": ['Pseudo', 'Stack', 'Register', 'Imm']},
    "Mov": {"src": ['Pseudo', 'Stack', 'Register', 'Imm'],
            "dst": ['Pseudo', 'Stack', 'Register']},
    "AllocateStack": ["Imm"],
    "Pseudo": ["Identifier"],
    "Not": [],
    "Neg": [],
    "Add": [],
    "Sub": [],
    "Mult": [],
    "Div": [],
    "Sext": [],
    "E": [],
    "NE": [],
    "G": [],
    "GE": [],
    "L": [],
    "LE": [],
    "Ret": []
}

class x86_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        if ident not in x86_node_types:
            if type(ident) is not tuple:
                raise ValueError(f"unexpected node {ident}")
        else:
            vals = x86_node_types[ident]
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
                raise TypeError(f"unexpected type of node {ident} in x86_node_types")
        
        self.child = child