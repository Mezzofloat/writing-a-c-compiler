from astnode.ASTNode import ASTNode

"""
Definitions for the types of RISC-V nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    instructions: list of instructions (Instructions)
Identifier:
    [name for the node with this as a child (String)]
Instructions:
    list of assembly instructions (Binary | Unary | Branch | Identifier | Load | Store | Ret | SetLessThan | SetLessThanU)
Binary:
    op: operation (Add | Sub | Xor)
    src1: left operand (Register | Stack | Imm)
    src2: right operand (Register | Stack | Imm)
    dst: result (Register | Stack)
    (subi is not a thing, src1 should eventually be not imm)
Unary:
    op: operation (Not | Neg | Mov)
    src: operand (Stack | Imm | Register)
    dst: result (Stack | Register)
Branch:
    cond: condition of branching (Eq | Lt | Ge | Ne | Le | Gt | LtU)
    src1: left operand of comparison (Register | Stack)
    src2: right operand of comparison (Register | Stack)
    branch: location to branch to (Identifier)
Load:
    src: source which destination gets value from (Imm | Stack)
    dst: destination register (Register)
Store:
    src: source register which destination gets value from (Register)
    dst: destination on the stack (Stack)
SetLessThan(U):
    src1: *left* < right (Stack | Register | Imm)
    src2: left < *right* (Stack | Register | Imm)
    dst: (Stack | Register)
Imm:
    [value for the node with this as a child (Int)]
Stack:
    [address away from sp where the value is at (Int)]
Register:
    [register that node with this as a child uses (String)]
Ret, Not, Neg, Add, Sub, Eq, Ne, Le, Lt, Ge, Gt:
    -
"""

RISC_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"],
                 "instructions": ["Instruction*"]},
    "Instruction": ['Binary', 'Unary', 'Branch', 'Identifier', 'Load', 'Store', 'Ret', 'SetLessThan', 'SetLessThanU'],
    "Binary": {"op": ['Add', 'Sub', 'Xor'],
               "src1": ['Pseudo', 'Register', 'Stack', 'Imm'],
               "src2": ['Pseudo', 'Register', 'Stack', 'Imm'],
               "dst": ['Pseudo', 'Register', 'Stack']},
    "Unary": {"op": ['Not', 'Neg', 'Mov'],
              "src": ['Pseudo', 'Stack', 'Imm', 'Register'],
              "dst": ['Pseudo', 'Stack', 'Register']},
    "Branch": {"cond": ['Eq', 'Lt', 'Ge', 'Ne', 'Le', 'Gt', 'LtU'],
               "src1": ['Pseudo', 'Register', 'Stack', 'Imm'],
               "src2": ['Pseudo', 'Register', 'Stack', 'Imm'],
               "branch": ['Identifier']},
    "Load": {"src": ['Pseudo', 'Imm', 'Stack'],
             "dst": ['Register', 'Stack']},
    "Store": {"src": ['Register'],
              "dst": ['Pseudo', 'Stack']},
    "SetLessThan": {"src1": ['Pseudo', 'Stack', 'Register', 'Imm'],
                    "src2": ['Pseudo', 'Stack', 'Register', 'Imm'],
                    "dst": ['Stack', 'Pseudo', 'Register']},
    "SetLessThanU": {"src1": ['Pseudo', 'Stack', 'Register', 'Imm'],
                     "src2": ['Pseudo', 'Stack', 'Register', 'Imm'],
                     "dst": ['Stack', 'Pseudo', 'Register']},
    "Pseudo": ["Identifier"],
    "Ret": [],
    "Not": [],
    "Neg": [],
    "Add": [],
    "Sub": [],
    "Xor": [],
    "Eq": [],
    "Ne": [],
    "Le": [],
    "Lt": [],
    "Ge": [],
    "Gt": [],
    "LtU": [],
    "Mov": []
}

class RISC_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        if ident not in RISC_node_types:
            if type(ident) is not tuple:
                raise ValueError(f"unexpected node {ident}")
        else:
            vals = RISC_node_types[ident]
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
                raise TypeError(f"unexpected type of node {ident} in RISC_node_types")
        
        self.child = child