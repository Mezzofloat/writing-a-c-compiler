from ASTNode import ATTACK_node, Assembly_node

# the amount the stack needs to allocate, set at the end of replace_pseudo
allocate_offset = 0

# converts a tree of attack nodes into a tree of assembly nodes
def attack_to_assembly_ast(node: ATTACK_node) -> Assembly_node:
    match node.ident:
        case "Binary":
            if node.child["op"].ident == "Divide":
                src1 = attack_to_assembly_ast(node.child["src1"])
                src2 = attack_to_assembly_ast(node.child["src2"])
                reg = Assembly_node(("Register", "%eax"))

                mov = Assembly_node("Mov", {
                    "src": src1,
                    "dst": reg
                })

                cdq = Assembly_node("Sext")

                idiv = Assembly_node("Unary", {
                    "op": Assembly_node("Div"),
                    "dst": src2
                })

                result = Assembly_node(("Register", "%eax"))
                movback = Assembly_node("Mov", {
                    "src": result,
                    "dst": attack_to_assembly_ast(node.child["dst"])
                })

                return [mov, cdq, idiv, movback]
            elif node.child["op"].ident == "Modulus":
                src1 = attack_to_assembly_ast(node.child["src1"])
                src2 = attack_to_assembly_ast(node.child["src2"])
                reg = Assembly_node(("Register", "%eax"))

                mov = Assembly_node("Mov", {
                    "src": src1,
                    "dst": reg
                })

                cdq = Assembly_node("Sext")

                print(src2)

                idiv = Assembly_node("Unary", {
                    "op": Assembly_node("Div"),
                    "dst": src2
                })

                result = Assembly_node(("Register", "%edx"))
                movback = Assembly_node("Mov", {
                    "src": result,
                    "dst": attack_to_assembly_ast(node.child["dst"])
                })

                return [mov, cdq, idiv, movback]
            else:
                left = attack_to_assembly_ast(node.child["src1"])
                dst = attack_to_assembly_ast(node.child["dst"])
                mov = Assembly_node("Mov", {
                    "src": left,
                    "dst": dst
                })

                binop = attack_to_assembly_ast(node.child["op"])
                right = attack_to_assembly_ast(node.child["src2"])
                binary = Assembly_node("Binary", {
                    "op": binop,
                    "src": right,
                    "dst": dst
                })

                return [mov, binary]
        case "Instructions":
            new_instructions = []

            for instr in node.child:
                outcome = attack_to_assembly_ast(instr)

                if type(outcome) is list:
                    for entry in outcome:
                        new_instructions.append(entry)
                else:
                    new_instructions.append(attack_to_assembly_ast(instr))
            
            new_node = Assembly_node("Instructions", new_instructions)

            return new_node
        case ("Constant", x):
            return Assembly_node(("Imm", x))
        case "Variable":
            ps = Assembly_node("Pseudo", attack_to_assembly_ast(node.child))
            return ps
        case "Complement":
            return Assembly_node("Not")
        case "Negate":
            return Assembly_node("Neg")
        case "Multiply":
            return Assembly_node("Mult")
        case "Unary":
            mov = Assembly_node("Mov", {
                "src": attack_to_assembly_ast(node.child["src"]),
                "dst": attack_to_assembly_ast(node.child["dst"])
            })

            operate = Assembly_node("Unary", {
                "op": attack_to_assembly_ast(node.child["op"]),
                "dst": attack_to_assembly_ast(node.child["dst"])
            })

            return [mov, operate]
        case "Return":
            val = attack_to_assembly_ast(node.child)

            reg = Assembly_node(("Register","%eax"))

            mov = Assembly_node("Mov", {
                "src": val,
                "dst": reg
            })

            ret = Assembly_node("Ret")
            
            return [mov, ret]
        case "Function":
            func = Assembly_node("Function", {
                "name": attack_to_assembly_ast(node.child["name"]),
                "instructions": attack_to_assembly_ast(node.child["instructions"])
            })

            return func
        case _:
            if node.child:
                if type(node.child) is ATTACK_node:
                    child = attack_to_assembly_ast(node.child)
                    parent = Assembly_node(node.ident, child)
                else:
                    raise ValueError(f"Child of {node} is not expected type")
            else:
                parent = Assembly_node(node.ident)
            
            return parent
    
    raise SyntaxError(f"Unknown node in tree: {node}")

# for all the instructions in this tree, replace the pseudo-registers
def replace_pseudo_registers(ast: Assembly_node):
    if ast.ident == "Program":
        # assuming I will later implement multiple functions in a program as a list
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

# replace the pseudo-registers given in the list of instructions
def replace_pseudo(instructions: list[Assembly_node]):
    global allocate_offset

    offset = 0
    mappings = {}

    for instr in instructions:
        if instr.child and type(instr.child) is dict:
            # consider the binaries
            if "src1" in instr.child and instr.child["src1"].ident == "Pseudo":
                pseudo_ident = instr.child["src1"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = f"-{offset}"

                reg = Assembly_node(("Stack", mappings[pseudo_ident]))

                instr.child["src1"] = reg
            
            if "src2" in instr.child and instr.child["src2"].ident == "Pseudo":
                pseudo_ident = instr.child["src2"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = f"-{offset}"

                reg = Assembly_node(("Stack", mappings[pseudo_ident]))

                instr.child["src2"] = reg

            # consider the unaries
            if "src" in instr.child and instr.child["src"].ident == "Pseudo":
                pseudo_ident = instr.child["src"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = f"-{offset}"

                reg = Assembly_node(("Stack", mappings[pseudo_ident]))

                instr.child["src"] = reg
            
            if "dst" in instr.child and instr.child["dst"].ident == "Pseudo":
                pseudo_ident = instr.child["dst"].child.ident[1]

                if pseudo_ident not in mappings:
                    offset += 4
                    mappings[pseudo_ident] = f"-{offset}"

                reg = Assembly_node(("Stack", mappings[pseudo_ident]))

                instr.child["dst"] = reg

    allocate_offset = offset

# for all the instructions in this tree, fix them if needed
def fix_instructions(ast: Assembly_node):
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

# fix the instructions in this list if needed
def fix(instructions: list[Assembly_node]):
    amount = Assembly_node(("Imm", allocate_offset))
    new_instruction = Assembly_node("AllocateStack", amount)

    instructions.insert(0, new_instruction)
    
    i = 0

    while i < len(instructions):
        instr = instructions[i]
        print(instr)

        if instr.ident == "Unary" and instr.child["op"].ident == "Div" and instr.child["dst"].ident[0] == "Imm":
            imm = instr.child["dst"].ident[1]

            reg = Assembly_node(("Register", "%r10d"))
            mov = Assembly_node("Mov", {
                "src": Assembly_node(("Imm", imm)),
                "dst": reg
            })

            div = Assembly_node("Unary", {
                "op": Assembly_node("Div"),
                "dst": reg
            })

            instructions[i] = mov
            instructions.insert(i+1, div)

        if instr.child and type(instr.child) is dict:
            if instr.ident == "Binary" and instr.child["op"].ident == "Mult" and instr.child["dst"].ident[0] == "Stack":
                reg = Assembly_node(("Register", "%r11d"))
                movToScratch = Assembly_node("Mov", {
                    "src": instr.child["dst"],
                    "dst": reg
                })

                mult = Assembly_node("Binary", {
                    "op": Assembly_node("Mult"),
                    "src": instr.child["src"],
                    "dst": reg
                })

                movBack = Assembly_node("Mov", {
                    "src": reg,
                    "dst": instr.child["dst"]
                })

                instructions[i] = movToScratch
                instructions.insert(i+1, mult)
                instructions.insert(i+2, movBack)
            elif "src" in instr.child and "dst" in instr.child:
                if instr.child["src"].ident[0] == "Stack" and instr.child["dst"].ident[0] == "Stack":
                    r10d = Assembly_node(("Register", "%r10d"))
                    
                    instr1 = Assembly_node("Mov", {
                        "src": instr.child["src"],
                        "dst": r10d
                    })

                    binop = {
                        "src": r10d,
                        "dst": instr.child["dst"]
                    }

                    if instr.ident == "Binary":
                        binop["op"] = instr.child["op"]

                    instr2 = Assembly_node(instr.ident, binop)

                    instructions[i] = instr1
                    instructions.insert(i+1, instr2)
        i += 1