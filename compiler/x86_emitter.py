from ASTNode import Assembly_node

def emit_x86(node: Assembly_node) -> str:
    match node.ident:
        case ("Identifier", ident):
            return ident
        case ("Stack", stack_amount):
            return f"{stack_amount}(%rbp)"
        case "Unary":
            op = node.child["op"]
            dst = node.child["dst"]
            return f"{emit_x86(op)}\t{emit_x86(dst)}"
        case "Binary":
            op = node.child["op"]
            src = node.child["src"]
            dst = node.child["dst"]

            return f"{emit_x86(op)}\t{emit_x86(src)}, {emit_x86(dst)}"
        case "Neg":
            return "negl"
        case "Not":
            return "notl"
        case "AllocateStack":
            return f"subq\t{emit_x86(node.child)}, %rsp"
        case ("Register", x):
            return x
        case "Program":
            s = emit_x86(node.child)
            s += "\t.section .note.GNU-stack,\"\",@progbits"
            return s
        case "Function":
            name = emit_x86(node.child["name"])

            s = f"\t.globl {name}\n"
            s += name + ":\n"
            s += "\tpushq\t%rbp\n\tmovq\t%rsp, %rbp\n"
            s += emit_x86(node.child["instructions"])
            return s
        case "Instructions":
            s = ""
            for inst in node.child:
                s += "\t" + emit_x86(inst) + "\n"
            return s
        case "Mov":
            s = f"movl\t{emit_x86(node.child["src"])}, {emit_x86(node.child["dst"])}"
            return s
        case "Ret":
            return "movq\t%rbp, %rsp\n\tpopq\t%rbp\n\tret"
        case "Add":
            return "addl"
        case "Sub":
            return "subl"
        case "Mult":
            return "imull"
        case "Div":
            return "idivl"
        case "Sext":
            return "cdq"
        case ("Imm", x):
            return "$" + str(x)
        case _:
            raise ValueError(f"Unknown node: {node}")