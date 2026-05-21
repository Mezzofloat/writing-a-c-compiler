from enum import Enum

class ASTNode:
    def __init__(self):
        self.child = None

    def __str__(self):
        def tabbify(string: str) -> str:
            # for each newline but the last, add a tab after it
            newstr = ""

            for i in range(len(string)):
                newstr += string[i]
                if string[i] == "\n" and i != len(string) - 2:
                    newstr += "\t"
            
            return newstr
        
        def print_list(lst: list) -> str:
            s = "[\n"
            for item in lst:
                s += str(item) + ",\n"
            s += "]"

            return s
        
        s = str(self.ident)

        # only adds if there are children
        if self.child:
            s += "(\n"

            # consider the dictionaries
            if type(self.child) is dict:
                keys = list(self.child.keys())

                for i in range(len(keys)):
                    child = keys[i]
                    s += f"{child}={self.child[child]}"

                    if i != len(keys) - 1:
                        s += "\n"

            # consider the lists
            elif type(self.child) is list:
                s += print_list(self.child)
            else: 
                s += str(self.child)

            s += "\n)"

        return tabbify(s)

class C_node(ASTNode):
    class C_type(Enum):
        Program = 1,
        Function = 2,
        Return = 3,
        Identifier = 4,
        Constant = 5,
        Unary = 6,
        Complement = 7,
        Negate = 8

    def __init__(self, ident : C_type):
        super().__init__()
        self.ident = ident

class Assembly_node(ASTNode):
    class Assembly_type(Enum):
        Program = 1,
        Function = 2,
        Instructions = 3,
        Mov = 4,
        Ret = 5,
        Imm = 6,
        Pseudo = 7,
        Register = 8,
        Unary = 9,
        Neg = 10,
        Not = 11,
        Stack = 12,
        AllocateStack = 13
    
    def __init__(self, ident : Assembly_type):
        super().__init__()
        self.ident = ident

class ATTACK_node(ASTNode):
    class ATTACK_type(Enum):
        Program = 1,
        Function = 2,
        Identifier = 3,
        Value = 4,
        Constant = 5,
        Variable = 6
        Unary = 7
        Complement = 8,
        Negate = 9,
        Instructions = 10

    def __init__(self, ident : ATTACK_type):
        super().__init__()
        self.ident = ident