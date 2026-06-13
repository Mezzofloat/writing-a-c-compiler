from astnode.ASTNode import ASTNode

"""
x86_node_types is a dictionary mapping the name of a type of x86 node to either a list of possible children or a dictionary mapping the name of a child to a list of possible types for that child. Depending on the value, the node will have different structures:
Empty list: the node should have no children
List: the node should have one child in the list of possible children
Dictionary: the node should have one child for each key in the dictionary, and the child for each key should be in the list of possible types for that key
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