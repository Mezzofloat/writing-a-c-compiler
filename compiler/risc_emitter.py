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

            for inst in node.child:
                s += '\t' + emit_risc(inst) + '\n'

            return s
        case "Load":
            num = node.child["src"].ident[1]
            reg = node.child["dst"].ident[1]

            s = f"li {reg}, {num}"
            return s
        case "Ret":
            return "Ret"