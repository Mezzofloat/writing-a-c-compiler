from enum import Enum

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
    op: binary operator that acts on the left and right operands (Add | Sub | Multiply | Divide | Modulus)
    left: left operand (Constant | Unary | Binary)
    right: right operand (Constant | Unary | Binary)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus:
    -
"""


class C_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)

        def expect(exp: bool):
            if not exp:
                raise AssertionError(f"Error in asserting grammar on {self}")
        
        try:
            match ident:
                case "Program":
                    expect(child.ident == "Function")
                case "Function":
                    expect(child["name"].ident[0] == "Identifier")
                    expect(child["body"].ident == "Return")
                case "Return":
                    expect(child.ident in ['Unary', 'Binary'] or child.ident[0] == "Constant")
                case "Unary":
                    expect(child["op"].ident in ["Complement", "Negate"])
                    expect(child["inner_exp"].ident in ["Unary", "Binary"] or child["inner_exp"].ident[0] == "Constant")
                case "Binary":
                    expect(child["op"].ident in ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus'])
                    expect(child["left"].ident in ["Unary", "Binary"] or child["left"].ident[0] == "Constant")
                    expect(child["right"].ident in ["Unary", "Binary"] or child["right"].ident[0] == "Constant")
                case "Complement" | "Negate" | "Add" | "Sub" | "Multiply" | "Divide" | "Modulus" | ("Identifier", _) | ("Constant", _):
                    expect(child is None)
                case _:
                    raise ValueError(f"unexpected node {ident}")
        except AttributeError:
            raise AssertionError(f"Error in accessing attribute; {child} is either None or wrong type")
        except KeyError:
            raise AssertionError(f"Error in accessing dict; {child} is either not dict or doesn't have required key")
        except IndexError:
            raise AssertionError(f"Error in indexing tuple; {child} doesn't have a tuple somewhere")
        finally:
            self.child = child
        
"""
Definitions for the types of ATTACK nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    instructions: list of instructions (Instructions)
Instructions:
    list of ATTACK instructions (Binary | Unary | Return)
Binary:
    op: operation (Add | Sub | Multiply | Divide | Modulus)
    src1: left operand (Constant | Variable)
    src2: right operand (Constant | Variable)
    dst: destination of operation (Variable)
Unary:
    op: operation (Complement | Negate)
    src: operand (Constant | Variable)
    dst: destination of operation (Variable)
Constant:
    [value for the node with this as a child (Int)]
Variable:
    temporary name for this variable (Identifier)
Return:
    expression being returned (Constant | Variable | Unary | Binary)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus:
    -
"""

class ATTACK_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        def expect(exp: bool):
            if not exp:
                raise AssertionError(f"Error in asserting grammar on {self}")
        
        try:
            match ident:
                case "Program":
                    expect(child.ident == "Function")
                case "Function":
                    expect(child["name"].ident[0] == "Identifier")
                    expect(child["instructions"].ident == "Instructions")
                case "Instructions":
                    expect(instr.ident in ['Binary', 'Unary', 'Return'] for instr in child)
                case "Return":
                    expect(child.ident in ['Unary', 'Binary', 'Variable'] or child.ident[0] == "Constant")
                case "Unary":
                    expect(child["op"].ident in ["Complement", "Negate"])
                    expect(child["src"].ident == "Variable" or child["src"].ident[0] == "Constant")
                    expect(child["dst"].ident == "Variable")
                case "Binary":
                    expect(child["op"].ident in ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus'])
                    expect(child["src1"].ident == "Variable" or child["src1"].ident[0] == "Constant")
                    expect(child["src2"].ident == "Variable" or child["src2"].ident[0] == "Constant")
                    expect(child["dst"].ident == "Variable")
                case "Variable":
                    expect(child.ident[0] == "Identifier")
                case "Complement" | "Negate" | "Add" | "Sub" | "Multiply" | "Divide" | "Modulus" | ("Identifier", _) | ("Constant", _):
                    expect(child is None)
                case _:
                    raise ValueError(f"unexpected node {ident}")
        except AttributeError:
            raise AssertionError(f"Error in accessing attribute; {child} is either None or wrong type")
        except KeyError:
            raise AssertionError(f"Error in accessing dict; {child} is either not dict or doesn't have required key")
        except IndexError:
            raise AssertionError(f"Error in indexing tuple; {child} doesn't have a tuple somewhere")
        finally:
            self.child = child

"""
Definitions for the types of Assembly nodes:
Format: (if ident is tuple: in []) name_of_node \n\t (if no children: -, if multiple: name_of_child:) objective (type1 | type2)

Program:
    function contained in the program (Function)
Function:
    name: name of the function (Identifier)
    instructions: list of instructions (Instructions)
Identifier:
    [name for the node with this as a child (String)]
Instructions:
    list of assembly instructions (Binary | Unary | Mov | Sext | Ret)
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
Ret, Not, Neg, Add, Sub, Mult, Div, Sext (sign-extend):
    -
"""

class Assembly_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)

        def expect(exp: bool):
            if not exp:
                raise AssertionError(f"Error in asserting grammar on {self}")
        
        try:
            match ident:
                case "Program":
                    expect(child.ident == "Function")
                case "Function":
                    expect(child["name"].ident[0] == "Identifier")
                    expect(child["instructions"].ident == "Instructions")
                case "Instructions":
                    expect(instr.ident in ['Binary', 'Unary', 'Mov', 'Sext', 'Ret'] for instr in child)
                case "Unary":
                    expect(child["op"].ident in ["Not", "Neg", "Div"])
                    expect(child["dst"].ident[0] in ['Stack','Register','Imm'] or child["dst"].ident == "Pseudo")
                case "Binary":
                    expect(child["op"].ident in ['Add', 'Sub', 'Mult'])
                    expect(child["src"].ident[0] in ['Stack', 'Register', 'Imm'] or child["src"].ident == "Pseudo")
                    expect(child["dst"].ident[0] in ['Stack', 'Register'] or child["dst"].ident == "Pseudo")
                case "Mov":
                    expect(child["src"].ident[0] in ['Stack', 'Register', 'Imm'] or child["src"].ident == "Pseudo")
                    expect(child["dst"].ident[0] in ['Stack', 'Register'] or child["dst"].ident == "Pseudo")
                case "AllocateStack":
                    expect(child.ident[0] == "Imm")
                case "Pseudo":
                    expect(child.ident[0] == "Identifier")
                case "Not" | "Neg" | "Add" | "Sub" | "Mult" | "Div" | ("Identifier", _) | ("Imm", _) | ("Stack", _) | ("Register", _) | "Ret" | "Sext":
                    expect(child is None)
                case _:
                    raise ValueError(f"unexpected node {ident}")
        except AttributeError:
            raise AssertionError(f"Error in accessing attribute; {child} is either None or wrong type")
        except KeyError:
            raise AssertionError(f"Error in accessing dict; {child} is either not dict or doesn't have required key")
        except IndexError:
            raise AssertionError(f"Error in indexing tuple; {child} doesn't have a tuple somewhere")
        finally:
            self.child = child

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
    list of assembly instructions (Unary | Load | Store | Ret)
Unary:
    op: operation (Not | Neg)
    src: operand (Stack | Imm | Register)
    dst: result (Stack | Register)
Load:
    src: source which destination gets value from (Imm | Stack)
    dst: destination register (Register)
Store:
    src: source register which destination gets value from (Register)
    dst: destination on the stack (Stack)
Imm:
    [value for the node with this as a child (Int)]
Stack:
    [address away from sp where the value is at (Int)]
AllocateStack:
    amount to be allocated (Imm)
Register:
    [register that node with this as a child uses (String)]
Ret, Not, Neg:
    -
"""

class RISC_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        try:
            LIST = 0

            def expect(*args):
                if len(args) == 1:
                    if type(args[0]) is not list or type(child) is not RISC_node:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    ls = args[0]
                    
                    if child.ident not in ls and child.ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                elif len(args) == 2:
                    if args[0] == LIST:
                        for entry in child:
                            if entry.ident not in args[1]:
                                raise AssertionError(f"Error in asserting grammar on {self}")
                            
                        return

                    if type(args[0]) is not str or type(args[1]) is not list or type(child) is not dict:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    key = args[0]
                    ls = args[1]

                    if child[key].ident not in ls and child[key].ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                elif len(args) == 0:
                    if child is not None:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                else:
                    raise SyntaxError("Incorrect number of arguments")

            match ident:
                case "Program":
                    expect(["Function"])
                case "Function":
                    expect("name", ["Identifier"])
                    expect("instructions", ["Instructions"])
                case "Instructions":
                    expect(LIST, ['Unary', 'Ret', 'Load', 'Store'])
                case "Unary":
                    expect("op", ['Not', 'Neg'])
                    expect("src", ['Pseudo', 'Stack', 'Imm', 'Register'])
                    expect("dst", ['Pseudo', 'Stack', 'Register'])
                case "Load":
                    expect("src", ['Pseudo', 'Imm', 'Stack'])
                    expect("dst", ["Register"])
                case "Store":
                    expect("src", ["Register"])
                    expect("dst", ["Pseudo", "Stack"])
                case "Pseudo":
                    expect(["Identifier"])
                case "AllocateStack":
                    expect(["Imm"])
                case ("Identifier", _) | ("Imm", _) | ("Register", _) | ("Stack", _) | "Ret" | "Not" | "Neg":
                    expect()
                case _:
                    raise ValueError(f"unexpected node {ident}")

        except AttributeError:
            raise AssertionError(f"Error in accessing attribute; {child} is either None or wrong type")
        except KeyError:
            raise AssertionError(f"Error in accessing dict; {child} is either not dict or doesn't have required key")
        except IndexError:
            raise AssertionError(f"Error in indexing tuple; {child} doesn't have a tuple somewhere")
        finally:
            self.child = child