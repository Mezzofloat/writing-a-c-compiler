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