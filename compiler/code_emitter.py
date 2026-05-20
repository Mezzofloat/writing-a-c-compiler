from ASTNode import Assembly_node

def emit_code(node: Assembly_node) -> str:
    match node.ident:
        case ("Identifier", ident):
            return ident
        case ("Stack", stack_amount):
            return f"{stack_amount}(%rbp)"
        case "Unary":
            op = node.child["op"]
            dst = node.child["dst"]
            return f"{emit_code(op)}\t{emit_code(dst)}"
        case "Neg":
            return "negl"
        case "Not":
            return "notl"
        case "AllocateStack":
            return f"subq\t{emit_code(node.child)}, %rsp"
        case ("Register", x):
            return x
        case "Program":
            s = "\t.file	\"return_2.c\"\n\t.text\n\t.globl	main\n\t.type	main, @function\n"
            s += emit_code(node.child)
            s += "\t.section .note.GNU-stack,\"\",@progbits"
            return s
        case "Function":
            s = emit_code(node.child["name"]) + ":\n"
            s += "\tpushq\t%rbp\n\tmovq\t%rsp, %rbp\n"
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
            return "movq\t%rbp, %rsp\n\tpopq\t%rbp\nret"
        case ("Imm", x):
            return "$" + str(x)
        case _:
            raise ValueError(f"Unknown node: {node}")