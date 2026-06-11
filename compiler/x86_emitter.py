from astnode.x86_node import x86_node

def emit_x86(node: x86_node) -> str:
    match node.ident:
        case ("Identifier", ident):
            return ident
        case ("Stack", stack_amount):
            return f"{stack_amount}(%rbp)"
        case "Cmp":
            l = node.child["left"]
            r = node.child["right"]

            return f"cmpl\t{emit_x86(l)}, {emit_x86(r)}"
        case "Jmp":
            return f"jmp\t{emit_x86(node.child)}"
        case "JmpCC":
            cond_code = emit_x86(node.child["cond"])
            label = emit_x86(node.child["label"])

            return f"j{cond_code}\t{label}"
        case "E" | 'NE' | 'L' | 'LE' | 'G' | 'GE':
            return node.ident.lower()
        case "SetCC":
            cond_code = emit_x86(node.child["cond"])
            dst4 = emit_x86(node.child["dst"])

            dst = dst4
            match dst4:
                case "%eax":
                    dst = "%al"
                case "%edx":
                    dst = "%dl"
                case "%r10d":
                    dst = "%r10b"
                case "%r11d":
                    dst = "%r11b"
            
            return f"set{cond_code}\t{dst}"
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
                if inst.ident[0] == "Identifier":
                    s += inst.ident[1] + ':\n'
                else:
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