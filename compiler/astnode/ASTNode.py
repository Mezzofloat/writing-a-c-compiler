class ASTNode:
    def __init__(self, ident, child=None):
        self.ident = ident
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
                    entry = keys[i]
                    if type(self.child[entry]) is list:
                        s += print_list(self.child[entry])
                    else:
                        s += f"{entry}={self.child[entry]}"

                    if i != len(keys) - 1:
                        s += "\n"

            # consider the lists
            elif type(self.child) is list:
                s += print_list(self.child)
            else: 
                s += str(self.child)

            s += "\n)"

        return tabbify(s)