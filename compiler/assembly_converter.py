from ASTNode import C_node, Assembly_node

# traverse the tree given in C_ast
def convert_to_assembly_ast(node: C_node) -> Assembly_node:
    if type(node.ident) is tuple:
        return Assembly_node(node.ident)

    match node.ident:
        case "Program":
            func = convert_to_assembly_ast(node.child)

            n = Assembly_node("Program")
            n.child = func
            return n
        case "Function":
            instructions = convert_to_assembly_ast(node.child["body"])

            n = Assembly_node("Function")
            n.child = {
                "name": node.child["name"],
                "instructions": instructions
            }
            return n
        case "Return":
            exp = convert_to_assembly_ast(node.child)

            reg = Assembly_node(("Reg", "%eax"))

            mov = Assembly_node("Mov")
            mov.child = {
                "src": exp,
                "dst": reg
            }

            ret = Assembly_node("Ret")

            n = Assembly_node("Instructions")
            n.child = [mov, ret]

            return n
        case "Expression":
            imm = Assembly_node("Imm")

            num = convert_to_assembly_ast(node.child)
            imm.child = num
            return imm
    
    raise SyntaxError(f"Unknown node in tree: {str(node)}")