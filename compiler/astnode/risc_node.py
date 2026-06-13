from astnode.ASTNode import ASTNode

"""
RISC_node_types is a dictionary mapping the name of a type of RISC node to either a list of possible children or a dictionary mapping the name of a child to a list of possible types for that child. Depending on the value, the node will have different structures:
Empty list: the node should have no children
List: the node should have one child in the list of possible children
Dictionary: the node should have one child for each key in the dictionary, and the child for each key should be in the list of possible types for that key
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