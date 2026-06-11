from astnode.ASTNode import ASTNode

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
    cond: condition to compare to zero (Constant | Variable)
    label: label to jump to (Identifier)
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