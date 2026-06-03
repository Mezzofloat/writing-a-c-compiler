from ASTNode import RISC_node

def emit_risc(node: RISC_node) -> str:
    match node.ident:
        case "Program":
            s = emit_risc(node.child)
            s += "\t.section .note.GNU-stack,\"\",@progbits"
            return s
        case "Function":
            name = emit_risc(node.child["name"])
            s = f".globl {name}\n{name}:\n"

            insts = node.child["instructions"]
            s += emit_risc(insts)

            return s
        case "Instructions":
            s = ""

            for inst in node.child:
                if type(inst.ident) is tuple and inst.ident[0] == "Identifier":
                    s += emit_risc(inst) + ':\n'
                else:
                    s += '\t' + emit_risc(inst) + '\n'
             
            return s
        case "Load":
            if node.child["src"].ident[0] == "Imm":
                num = emit_risc(node.child["src"])
                reg = emit_risc(node.child["dst"])
                s = f"li {reg}, {num}"
            else:
                stack = emit_risc(node.child["src"])
                reg = emit_risc(node.child["dst"])
                s = f"lw {reg}, {stack}"

            return s
        case "Store":
            return f"sw {emit_risc(node.child["src"])}, {emit_risc(node.child["dst"])}"
        case "Binary":
            i = 'i' if node.child["src2"].ident[0] == "Imm" else ''
            s = emit_risc(node.child["op"]) + i + ' '

            s += emit_risc(node.child["dst"]) + ', '
            s += emit_risc(node.child["src1"]) + ', '
            s += emit_risc(node.child["src2"])

            return s
        case "Unary":
            s = emit_risc(node.child["op"]) + ' '
            s += emit_risc(node.child["dst"]) + ', '
            s += emit_risc(node.child["src"])

            return s
        case "Branch":
            s = 'b' + emit_risc(node.child["cond"]) + ' '
            s += emit_risc(node.child["src1"]) + ', '
            s += emit_risc(node.child["src2"]) + ', '
            s += emit_risc(node.child["branch"])

            return s
        case ("Stack", adr):
            return f"{adr}(sp)"
        case ("Register", reg):
            return reg
        case ("Identifier", ident):
            return ident
        case ("Imm", imm):
            return str(imm)
        case "Ret":
            return "ret"
        case "Not":
            return "not"
        case "Neg":
            return "neg"
        case "Add":
            return "add"
        case "Sub":
            return "sub"
        case "Eq":
            return "eq"
        case "Lt":
            return "lt"
        case "Ge":
            return "ge"
        case "Ne":
            return "ne"
        case "Le":
            return "le"
        case "Gt":
            return "gt"
        case "Mov":
            return "mv"
        case "SetLessThan":
            dst = emit_risc(node.child["dst"])
            rs1 = emit_risc(node.child["src1"])
            rs2 = emit_risc(node.child["src2"])
            return f"slt {dst}, {rs1}, {rs2}"
        case "SetLessThanU":
            dst = emit_risc(node.child["dst"])
            rs1 = emit_risc(node.child["src1"])
            rs2 = emit_risc(node.child["src2"])
            return f"sltu {dst}, {rs1}, {rs2}"
        case "Xor":
            return "xor"