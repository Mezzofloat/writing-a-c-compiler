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
    cond: condition of branching (Eq | Lt | Ge | Ne | Le | Gt)
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
AllocateStack:
    amount to be allocated (Imm)
Register:
    [register that node with this as a child uses (String)]
Ret, Not, Neg, Add, Sub, Eq, Ne, Le, Lt, Ge, Gt:
    -
"""

class RISC_node(ASTNode):
    def __init__(self, ident, child=None):
        super().__init__(ident)
        
        try:
            LIST = 0
            VALUE = ['Imm', 'Pseudo', 'Stack', 'Register']

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
                                print(entry)
                                raise AssertionError(f"Error in asserting grammar on {self}")
                            
                        return

                    if type(args[0]) is not str or type(args[1]) is not list or type(child) is not dict:
                        raise TypeError(f"Error in function call of expect({args})")
                    
                    key = args[0]
                    ls = args[1]

                    if child[key].ident not in ls and child[key].ident[0] not in ls:
                        raise AssertionError(f"Error in asserting grammar on {self} with child {child}")
                elif len(args) == 0:
                    if child is not None:
                        raise AssertionError(f"Error in asserting grammar on {self} with child {child}")
                else:
                    raise SyntaxError("Incorrect number of arguments")

            match ident:
                case "Program":
                    expect(["Function"])
                case "Function":
                    expect("name", ["Identifier"])
                    expect("instructions", ["Instructions"])
                case "Instructions":
                    expect(LIST, ['Unary', 'Ret', 'Load', 'Store', 'Binary', 'Identifier', 'Branch', 'SetLessThan', 'SetLessThanU', 'Mov'])
                case "Binary":
                    expect("op", ['Add', 'Sub', 'Xor'])
                    expect("src1", ['Register', 'Stack', 'Pseudo', 'Imm'])
                    expect("src2", ['Register', 'Stack', 'Pseudo', 'Imm'])
                    expect("dst", ['Register', 'Stack', 'Pseudo'])
                case "Unary":
                    expect("op", ['Not', 'Neg', 'Mov'])
                    expect("src", ['Pseudo', 'Stack', 'Imm', 'Register'])
                    expect("dst", ['Pseudo', 'Stack', 'Register'])
                case "Branch":
                    expect("cond", ['Eq', 'Lt', 'Ge', 'Ne', 'Le', 'Gt'])
                    expect("src1", VALUE)
                    expect("src2", VALUE)
                    expect("branch", ['Identifier'])
                case "Load":
                    expect("src", ['Pseudo', 'Imm', 'Stack'])
                    expect("dst", ["Register", 'Stack'])
                case "Store":
                    expect("src", ["Register"])
                    expect("dst", ["Pseudo", "Stack"])
                case "Pseudo":
                    expect(["Identifier"])
                case ("Identifier", _) | ("Imm", _) | ("Register", _) | ("Stack", _) | "Ret" | "Not" | "Neg" | "Add" | "Sub" | "Eq" | "Ne" | "Le" | "Lt" | "Ge" | "Gt" | "Mov" | "Xor":
                    expect()
                case "SetLessThan" | "SetLessThanU":
                    expect("src1", VALUE)
                    expect("src2", VALUE)
                    expect("dst", ['Stack', 'Pseudo', 'Register'])
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