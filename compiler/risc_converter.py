from ASTNode import ATTACK_node, RISC_node

# based on my work in assembly_converter.py

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
    pass

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
    pass