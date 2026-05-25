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
        case ("Identifier", ident):
            return ident
        case "Instructions":
            s = ""

            if node.child[0].ident == "AllocateStack":
                end = "\taddi sp, sp, " + str(node.child[0].child.ident[1]) + '\n'
            else:
                end = ""

            for inst in node.child:
                #print(inst)
                s += '\t' + emit_risc(inst) + '\n'
             
            s = f"{s[:-5]}{end}{s[-5:]}"

            return s
        case "Load":
            if node.child["src"].ident[0] == "Imm":
                num = node.child["src"].ident[1]
                reg = node.child["dst"].ident[1]
                s = f"li {reg}, {num}"
            else:
                stack = emit_risc(node.child["src"])
                reg = node.child["dst"].ident[1]
                s = f"lw {reg}, {stack}"

            return s
        case "Store":
            return f"sw {emit_risc(node.child["src"])}, {emit_risc(node.child["dst"])}"
        case ("Imm", imm):
            return str(imm)
        case "Unary":
            s = emit_risc(node.child["op"]) + ' '
            s += emit_risc(node.child["dst"]) + ', '
            s += emit_risc(node.child["src"])

            return s
        case ("Stack", adr):
            return f"{adr}(sp)"
        case ("Register", reg):
            return reg
        case "AllocateStack":
            return f"addi sp, sp, -{node.child.ident[1]}"
        case "Ret":
            return "ret"
        case "Not":
            return "not"
        case "Neg":
            return "neg"