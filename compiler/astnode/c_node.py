from astnode.ASTNode import ASTNode

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
Complement, Negate, Add, Sub, Multiply, Divide, Modulus, Not, And, Or, etc.:
    -
"""

C_node_types = {
    "Program": ["Function"],
    "Function": {"name": ["Identifier"], "body": ["Return"]},
    "Return": ['Constant', 'Unary', 'Binary'],
    "Unary": {"op": ["Complement", "Negate", "Not"], "inner_exp": ["Constant", "Unary", "Binary"]},
    "Binary": {"op": ['Add', 'Sub', 'Multiply', 'Divide', 'Modulus', 'And', 'Or', 'LessThan', 'GreaterThan', 'Equal', 'NotEqual', 'LessOrEqual', 'GreaterOrEqual'], 
                "left": ["Constant", "Unary", "Binary"], 
                "right": ["Constant", "Unary", "Binary"]},
    "Complement": [],
    "Negate": [],
    "Add": [],
    "Sub": [],
    "Multiply": [],
    "Divide": [],
    "Modulus": [],
    "And": [],
    "Or": [],
    "Equal": [],
    "NotEqual": [],
    "LessThan": [],
    "GreaterThan": [],
    "LessOrEqual": [],
    "GreaterOrEqual": [],
    "Not": []
}

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

            if ident not in C_node_types:
                if type(ident) is tuple:
                    pass
                else:
                    raise ValueError(f"unexpected node {ident}")
            else:
                vals = C_node_types[ident]
                if type(vals) is dict:
                    for key, ls in vals.items():
                        expect(key, ls)
                elif type(vals) is list:
                    if len(vals) == 0:
                        expect()
                    else:
                        expect(vals)
                else:
                    raise TypeError(f"unexpected type of node {ident} in C_node_types")

        except AttributeError:
            raise AssertionError(f"Error in accessing attribute; {child} is either None or wrong type")
        except KeyError:
            raise AssertionError(f"Error in accessing dict; {child} is either not dict or doesn't have required key")
        except IndexError:
            raise AssertionError(f"Error in indexing tuple; {child} doesn't have a tuple somewhere")
        finally:
            self.child = child
        