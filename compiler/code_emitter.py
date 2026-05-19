from ASTNode import Assembly_node

def emit_code(node: Assembly_node) -> str:
    if type(node.ident) is tuple:
        return str(node.ident[1])
    
    match node.ident:
        case "Program":
            s = "\t.file	\"return_2.c\"\n\t.text\n\t.globl	main\n\t.type	main, @function\n"
            s += emit_code(node.child)
            s += "\t.section .note.GNU-stack,\"\",@progbits"
            return s
        case "Function":
            s = emit_code(node.child["name"]) + ":\n"
            s += emit_code(node.child["instructions"])
            return s
        case "Instructions":
            s = ""
            for inst in node.child:
                s += "\t" + emit_code(inst) + "\n"
            return s
        case "Mov":
            s = f"movl\t{emit_code(node.child["src"])}, {emit_code(node.child["dst"])}"
            return s
        case "Ret":
            return "ret"
        case "Imm":
            return f"${emit_code(node.child)}"