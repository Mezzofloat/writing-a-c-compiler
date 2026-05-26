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
                if type(inst.ident) is tuple and inst.ident[0] == "Identifier":
                    s += emit_risc(inst) + ':\n'
                else:
                    s += '\t' + emit_risc(inst) + '\n'
             
            s = f"{s[:-5]}{end}{s[-5:]}"

            return s
        case "Load":
            if node.child["src"].ident[0] == "Imm" and node.child["dst"].ident[0] == "Stack":
                return ''
            if node.child["src"].ident[0] == "Imm":
                #print(node)
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
        case "Binary":
            op = node.child["op"]

            if op.ident == "Sub" and node.child["src2"].ident[0] == "Imm":
                #print("addi comes from sub imm")
                dst = emit_risc(node.child["dst"])
                src1 = emit_risc(node.child["src1"])
                imm = f"-{node.child["src2"].ident[1]}"

                s = f"addi {dst}, {src1}, {imm}"
            else:
                #print("addi comes from add imm")
                i = 'i' if node.child["src2"].ident[0] == "Imm" else ''
                s = emit_risc(node.child["op"]) + i + ' '

                s += emit_risc(node.child["dst"]) + ', '

                if node.child["op"].ident == "Sub":
                    s += emit_risc(node.child["src1"]) + ', '
                    s += emit_risc(node.child["src2"])
                else:
                    s += emit_risc(node.child["src1"]) + ', '
                    s += emit_risc(node.child["src2"])

            return s
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
        case "Add":
            return "add"
        case "Sub":
            return "sub"
        case "Branch":
            s = 'b' + emit_risc(node.child["cond"]) + ' '
            s += emit_risc(node.child["src1"]) + ', '
            s += emit_risc(node.child["src2"]) + ', '
            s += emit_risc(node.child["branch"])

            return s
        case "Eq":
            return "eq"
        case "Lt":
            return "lt"
        case "Ge": return "ge"