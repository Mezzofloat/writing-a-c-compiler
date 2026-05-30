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
    op: binary operator that acts on the left and right operands (Add | Sub | Multiply | Divide | Modulus
                                                                | And | Or | Equal | NotEqual | LessThan
                                                                | LessOrEqual | GreaterThan | GreaterOrEqual)
    left: left operand (Constant | Unary | Binary)
    right: right operand (Constant | Unary | Binary)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus, And, Or, etc.:
    -
"""


class C_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        try:
            LIST = 0

            def expect(*args):
                if len(args) == 1:
                    if type(args[0]) is not list or type(child) is not C_node:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    ls = args[0]
                    
                    if child.ident not in ls and child.ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                elif len(args) == 2:
                    if args[0] == LIST:
                        for entry in child: # type: ignore
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
                    expect("body", ["Return"])
                case "Return":
                    expect(['Constant', 'Unary', 'Binary'])
                case "Unary":
                    expect("op", ["Complement", "Negate", 'Not'])
                    expect("inner_exp", ["Constant", "Unary", "Binary"])
                case "Binary":
                    expect("op", ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'And', 'Or', 'LessThan', 'GreaterThan', 'Equal', 'NotEqual', 'LessOrEqual', 'GreaterOrEqual'])
                    expect("left", ["Constant", "Unary", "Binary"])
                    expect("right", ["Constant", "Unary", "Binary"])
                case "Complement" | "Negate" | "Add" | "Sub" | "Multiply" | "Divide" | "Modulus" | ("Identifier", _) | ("Constant", _):
                    expect()
                case "And" | "Or" | "Not" | "Equal" | "NotEqual" | "LessThan" | "GreaterThan" | "LessOrEqual" | "GreaterOrEqual":
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
    condition to compare to zero (Constant | Variable)
    label to jump to (Identifier)
Complement, Negate, Add, Sub, Multiply, Divide, Modulus, Copy:
    -
"""

class ATTACK_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        try:
            LIST = 0

            def expect(*args):
                if len(args) == 1:
                    if type(args[0]) is not list or type(child) is not ATTACK_node:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    ls = args[0]
                    
                    if child.ident not in ls and child.ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                elif len(args) == 2:
                    if args[0] == LIST:
                        for entry in child: # type: ignore
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
                    expect(LIST, ['Binary', 'Unary', 'Return', 'Jump', 'JumpIfZero', 'JumpIfNotZero'])
                case "Return":
                    expect(['Unary', 'Binary', 'Variable', 'Constant'])
                case "Unary":
                    expect("op", ["Complement", "Negate", 'Not', 'Copy'])
                    expect("src", ["Variable", "Constant"])
                    expect("dst", ["Variable"])
                case "Binary":
                    expect("op", ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'Equal', 'NotEqual', 'LessThan', 'LessOrEqual', 'GreaterThan', 'GreaterOrEqual'])
                    expect("src1", ["Variable", "Constant"])
                    expect("src2", ["Variable", "Constant"])
                    expect("dst", ["Variable"])
                case "Variable":
                    expect(["Identifier"])
                case "Jump":
                    expect(['Identifier'])
                case "JumpIfZero" | "JumpIfNotZero":
                    expect("cond", ['Variable', 'Constant'])
                    expect("label", ['Identifier'])
                case "Complement" | "Negate" | "Add" | "Sub" | "Multiply" | "Divide" | "Modulus" | ("Identifier", _) | ("Constant", _):
                    expect()
                case "Copy" | "Not" | "LessThan" | "LessOrEqual" | "GreaterThan" | "GreaterOrEqual" | "Equal" | "NotEqual":
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

class x86_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        try:
            LIST = 0
            VALUE = ['Imm', 'Pseudo', 'Stack', 'Register']

            def expect(*args):
                if len(args) == 1:
                    if type(args[0]) is not list or type(child) is not x86_node:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    ls = args[0]
                    
                    if child.ident not in ls and child.ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self}")
                elif len(args) == 2:
                    if args[0] == LIST:
                        for entry in child: # type: ignore
                            if entry.ident not in args[1] and entry.ident[0] not in args[1]:
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
                    expect(LIST, ['Binary', 'Unary', 'Mov', 'Sext', 'Ret', 'Cmp', 'Jmp', 'JmpCC', 'SetCC', 'Identifier'])
                case "Unary":
                    expect("op", ["Not", "Neg", "Div"])
                    expect("dst", ['Pseudo', 'Stack','Register','Imm'])
                case "Binary":
                    expect("op", ['Add', 'Sub', 'Mult'])
                    expect("src", ['Pseudo', 'Stack', 'Register', 'Imm'])
                    expect("dst", ['Pseudo', 'Stack', 'Register'])
                case "Cmp":
                    expect("left", VALUE)
                    expect("right", VALUE)
                case "Jmp":
                    expect(['Identifier'])
                case "JmpCC":
                    expect("cond", ['E', 'NE', 'G', 'GE', 'L', 'LE'])
                    expect("label", ['Identifier'])
                case "SetCC":
                    expect("cond", ['E', 'NE', 'G', 'GE', 'L', 'LE'])
                    expect("dst", VALUE)
                case "Mov":
                    expect("src", ['Pseudo', 'Stack', 'Register', 'Imm'])
                    expect("dst", ['Pseudo', 'Stack', 'Register'])
                case "AllocateStack":
                    expect(["Imm"])
                case "Pseudo":
                    expect(["Identifier"])
                case "Not" | "Neg" | "Add" | "Sub" | "Mult" | "Div" | ("Identifier", _) | ("Imm", _) | ("Stack", _) | ("Register", _) | "Ret" | "Sext" | "E" | "NE" | 'G' | 'GE' | 'L' | 'LE':
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
    list of assembly instructions (Binary | Unary | Branch | Identifier | Load | Store | Ret)
Binary:
    op: operation (Add | Sub)
    src1: left operand (Register | Stack | Imm)
    src2: right operand (Register | Stack | Imm)
    dst: result (Register | Stack)
    (subi is not a thing, src1 should eventually be not imm)
Unary:
    op: operation (Not | Neg)
    src: operand (Stack | Imm | Register)
    dst: result (Stack | Register)
Branch:
    cond: condition of branching (Eq | Lt | Ge)
    src1: left operand of comparison (Register | Stack)
    src2: right operand of comparison (Register | Stack)
    branch: location to branch to (Identifier)
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
Ret, Not, Neg, Add, Sub, Eq, Lt, Ge:
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
                        for entry in child: # type: ignore
                            if entry.ident not in args[1] and entry.ident[0] not in args[1]:
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
                    expect(LIST, ['Unary', 'Ret', 'Load', 'Store', 'Binary', 'Identifier', 'Branch'])
                case "Binary":
                    expect("op", ['Add', 'Sub'])
                    expect("src1", ['Register', 'Stack', 'Pseudo', 'Imm'])
                    expect("src2", ['Register', 'Stack', 'Pseudo', 'Imm'])
                    expect("dst", ['Register', 'Stack', 'Pseudo'])
                case "Unary":
                    expect("op", ['Not', 'Neg'])
                    expect("src", ['Pseudo', 'Stack', 'Imm', 'Register'])
                    expect("dst", ['Pseudo', 'Stack', 'Register'])
                case "Branch":
                    expect("cond", ['Eq', 'Lt', 'Ge'])
                    expect("src1", ['Register', 'Stack', 'Pseudo'])
                    expect("src2", ['Register', 'Stack', 'Pseudo'])
                    expect("branch", ['Identifier'])
                case "Load":
                    expect("src", ['Pseudo', 'Imm', 'Stack'])
                    expect("dst", ["Register", 'Stack'])
                case "Store":
                    expect("src", ["Register"])
                    expect("dst", ["Pseudo", "Stack"])
                case "Pseudo":
                    expect(["Identifier"])
                case "AllocateStack":
                    expect(["Imm"])
                case ("Identifier", _) | ("Imm", _) | ("Register", _) | ("Stack", _) | "Ret" | "Not" | "Neg" | "Add" | "Sub" | "Eq" | "Lt" | "Ge":
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