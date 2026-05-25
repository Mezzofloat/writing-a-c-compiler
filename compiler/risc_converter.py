from ASTNode import ATTACK_node, RISC_node

# based on my work in assembly_converter.py

allocate_offset = 0

def attack_to_risc_ast(node: ATTACK_node) -> RISC_node:
    match node.ident:
        case "Program":
            func = attack_to_risc_ast(node.child)

            return RISC_node("Program", func)
        case "Function":
            name = attack_to_risc_ast(node.child["name"])
            instructions = attack_to_risc_ast(node.child["instructions"])

            return RISC_node("Function", {
                "name": name,
                "instructions": instructions
            })
        case ("Identifier", _):
            return RISC_node(node.ident)
        case "Instructions":
            newinst = []

            for instr in node.child:
                outcome = attack_to_risc_ast(instr)

                if type(outcome) is list:
                    for entry in outcome:
                        newinst.append(entry)

                else:
                    newinst.append(outcome)
            
            return RISC_node("Instructions", newinst)
        case "Return":
            num = attack_to_risc_ast(node.child)
            reg = RISC_node(("Register", "a0"))
            load = RISC_node("Load", {
                "src": num,
                "dst": reg
            })

            ret = RISC_node("Ret")

            return [load, ret]
        
        case ("Constant", c):
            return RISC_node(("Imm", c))
        
        case "Unary":
            un = RISC_node("Unary", {
                "op": attack_to_risc_ast(node.child["op"]),
                "src": attack_to_risc_ast(node.child["src"]),
                "dst": attack_to_risc_ast(node.child["dst"])
            })

            return un
        
        case "Complement":
            return RISC_node("Not")
        case "Negate":
            return RISC_node("Neg")
        case "Variable":
            return RISC_node("Pseudo", attack_to_risc_ast(node.child))


def replace_pseudo_registers(ast: RISC_node):
    if ast.ident == "Program":
        if type(ast.child) is list:
            for func in ast.child:
                replace_pseudo_registers(func)
        else:
            replace_pseudo_registers(ast.child)
    elif ast.ident == "Function":
        # functions should have a list of instructions, which I am calling replace_pseudo on
        replace_pseudo(ast.child["instructions"].child)
    else:
        raise ValueError(f"Replace function called on {ast}")

def replace_pseudo(instructions: list[RISC_node]):
    global allocate_offset

    offset = 0
    mappings = {}

    for inst in instructions:
        if inst.child and type(inst.child) is dict:
            # consider the unaries
            if "src" in inst.child and inst.child["src"].ident == "Pseudo":
                pseudo_ident = inst.child["src"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = f"-{offset}"

                reg = RISC_node(("Stack", mappings[pseudo_ident]))

                inst.child["src"] = reg
            if "dst" in inst.child and inst.child["dst"].ident == "Pseudo":
                pseudo_ident = inst.child["dst"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = offset

                reg = RISC_node(("Stack", mappings[pseudo_ident]))

                inst.child["dst"] = reg

    allocate_offset = offset

def fix_instructions(ast: RISC_node):
    if ast.ident == "Program":
        # assuming I will later implement multiple functions in a program as a list
        if type(ast.child) is list:
            for func in ast.child:
                fix_instructions(func)
        else:
            fix_instructions(ast.child)
    elif ast.ident == "Function":
        # functions should have a list of instructions, which I am calling fix on
        fix(ast.child["instructions"].child)
    else:
        raise ValueError(f"fix_instructions called on {ast}")

def fix(instructions: list[RISC_node]):
    amount = RISC_node(("Imm", allocate_offset))
    new_inst = RISC_node("AllocateStack", amount)

    instructions.insert(0, new_inst)

    i = 0
    while i < len(instructions):
        instr = instructions[i]

        if instr.ident == "Unary":
            if instr.child["src"].ident[0] == "Stack" or instr.child["src"].ident[0] == "Imm":
                t0 = RISC_node(("Register", "t0"))

                load = RISC_node("Load", {
                    "src": instr.child["src"],
                    "dst": t0
                })

                op = RISC_node("Unary", {
                    "op": instr.child["op"],
                    "src": t0,
                    "dst": instr.child["dst"]
                })

                instructions.insert(i, load)
                instructions.insert(i+1, op)
                instructions.remove(instr)

                i += 1
                continue

            if instr.child["dst"].ident[0] == "Stack":
                t0 = RISC_node(("Register", "t0"))

                op = RISC_node("Unary", {
                    "op": instr.child["op"],
                    "src": instr.child["src"],
                    "dst": t0
                })
                store = RISC_node("Store", {
                    "src": t0,
                    "dst": instr.child["dst"]
                })

                instructions.insert(i, op)
                instructions.insert(i+1, store)
                instructions.remove(instr)

                i += 1
                continue
            
        i += 1