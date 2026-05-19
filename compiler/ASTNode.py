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
            s = ["[\n"]
            for item in lst:
                s.append(str(item) + ",\n")
            s.append("]")

            return "".join(s)
        
        s = []

        # print only the value, not the type
        if type(self.ident) is tuple:
            s.append(self.ident[1])
        else:
            s.append(self.ident)

        # only adds if there are children
        if self.child:
            s.append("(\n")

            # consider the dictionaries
            if type(self.child) is dict:
                for child in self.child:
                    s.append(f"{child}=")
                    if type(self.child[child]) is list:
                        s.append(print_list(self.child[child]))
                    else:
                        s.append(f"{str(self.child[child])}\n")
            # consider the lists
            elif type(self.child) is list:
                s.append(print_list(self.child))
            else: 
                s.append(str(self.child))

            s.append("\n)")

        return tabbify("".join(s))

class C_node(ASTNode):
    class C_type(Enum):
        Program = 1,
        Function = 2,
        Return = 3,
        Expression = 4,
        Identifier = 5,
        Integer = 6

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
        Imm = 6
    
    def __init__(self, ident : Assembly_type):
        super().__init__()
        self.ident = ident