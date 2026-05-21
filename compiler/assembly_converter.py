from ASTNode import ATTACK_node, Assembly_node

allocate_offset = 0

# traverse the tree given in attack_ast
def attack_to_assembly_ast(node: ATTACK_node) -> Assembly_node:
    match node.ident:
        case "Binary":
            if node.child["op"].ident == "Divide":
                mov = Assembly_node("Mov")
                src1 = attack_to_assembly_ast(node.child["src1"])
                src2 = attack_to_assembly_ast(node.child["src2"])
                reg = Assembly_node(("Register", "%eax"))
                mov.child = {
                    "src": src1,
                    "dst": reg
                }

                cdq = Assembly_node("Sext")

                idiv = Assembly_node("Unary")
                idiv.child = {
                    "op": Assembly_node("Div"),
                    "dst": src2
                }

                movback = Assembly_node("Mov")
                result = Assembly_node(("Register", "%eax"))
                movback.child = {
                    "src": result,
                    "dst": attack_to_assembly_ast(node.child["dst"])
                }

                return [mov, cdq, idiv, movback]
            elif node.child["op"].ident == "Modulus":
                mov = Assembly_node("Mov")
                src1 = attack_to_assembly_ast(node.child["src1"])
                src2 = attack_to_assembly_ast(node.child["src2"])
                reg = Assembly_node(("Register", "%eax"))
                mov.child = {
                    "src": src1,
                    "dst": reg
                }

                cdq = Assembly_node("Sext")

                idiv = Assembly_node("Unary")
                idiv.child = {
                    "op": Assembly_node("Div"),
                    "dst": src2
                }

                movback = Assembly_node("Mov")
                result = Assembly_node(("Register", "%edx"))
                movback.child = {
                    "src": result,
                    "dst": attack_to_assembly_ast(node.child["dst"])
                }

                return [mov, cdq, idiv, movback]
            else:
                mov = Assembly_node("Mov")
                left = attack_to_assembly_ast(node.child["src1"])
                dst = attack_to_assembly_ast(node.child["dst"])
                mov.child = {
                    "src": left,
                    "dst": dst
                }

                binary = Assembly_node("Binary")
                binop = attack_to_assembly_ast(node.child["op"])
                right = attack_to_assembly_ast(node.child["src2"])
                binary.child = {
                    "op": binop,
                    "src": right,
                    "dst": dst
                }

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
            
            new_node = Assembly_node("Instructions")
            new_node.child = new_instructions

            return new_node
        case ("Constant", x):
            return Assembly_node(("Imm", x))
        case "Variable":
            ps = Assembly_node("Pseudo")
            ps.child = attack_to_assembly_ast(node.child)
            return ps
        case "Complement":
            return Assembly_node("Not")
        case "Negate":
            return Assembly_node("Neg")
        case "Multiply":
            return Assembly_node("Mult")
        case "Unary":
            mov = Assembly_node("Mov")
            mov.child = {
                "src": attack_to_assembly_ast(node.child["src"]),
                "dst": attack_to_assembly_ast(node.child["dst"])
            }

            operate = Assembly_node("Unary")
            operate.child = {
                "op": attack_to_assembly_ast(node.child["op"]),
                "dst": attack_to_assembly_ast(node.child["dst"])
            }

            return [mov, operate]
        case "Return":
            val = attack_to_assembly_ast(node.child)

            reg = Assembly_node(("Register","%eax"))

            mov = Assembly_node("Mov")
            mov.child = {
                "src": val,
                "dst": reg
            }

            ret = Assembly_node("Ret")
            
            return [mov, ret]
        case "Function":
            func = Assembly_node("Function")

            func.child = {
                "name": node.child["name"],
                "instructions": attack_to_assembly_ast(node.child["instructions"])
            }

            return func
        case _:
            parent = Assembly_node(node.ident)

            if node.child:
                if type(node.child) is ATTACK_node:
                    child = attack_to_assembly_ast(node.child)
                    parent.child = child
                else:
                    raise ValueError(f"Child of {node} is not expected type")
            
            return parent
    
    raise SyntaxError(f"Unknown node in tree: {node}")

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

def fix_instructions(instructions: list[Assembly_node]):
    new_instruction = Assembly_node("AllocateStack")
    amount = Assembly_node(("Imm", allocate_offset))
    new_instruction.child = amount

    instructions.insert(0, new_instruction)
    
    i = 0

    while i < len(instructions):
        instr = instructions[i]
        print(instr)

        if instr.ident == "Unary" and instr.child["op"].ident == "Div" and instr.child["dst"].ident[0] == "Imm":
            imm = instr.child["dst"].ident[1]

            mov = Assembly_node("Mov")
            reg = Assembly_node(("Register", "%r10d"))
            mov.child = {
                "src": Assembly_node(("Imm", imm)),
                "dst": reg
            }

            div = Assembly_node("Unary")
            div.child = {
                "op": Assembly_node("Div"),
                "dst": reg
            }

            instructions[i] = mov
            instructions.insert(i+1, div)

        if instr.child and type(instr.child) is dict:
            if instr.ident == "Binary" and instr.child["op"].ident == "Mult" and instr.child["dst"].ident[0] == "Stack":
                movToScratch = Assembly_node("Mov")
                reg = Assembly_node(("Register", "%r11d"))
                movToScratch.child = {
                    "src": instr.child["dst"],
                    "dst": reg
                }

                mult = Assembly_node("Binary")
                mult.child = {
                    "op": Assembly_node("Mult"),
                    "src": instr.child["src"],
                    "dst": reg
                }

                movBack = Assembly_node("Mov")
                movBack.child = {
                    "src": reg,
                    "dst": instr.child["dst"]
                }

                instructions[i] = movToScratch
                instructions.insert(i+1, mult)
                instructions.insert(i+2, movBack)
            elif "src" in instr.child and "dst" in instr.child:
                if instr.child["src"].ident[0] == "Stack" and instr.child["dst"].ident[0] == "Stack":
                    r10d = Assembly_node(("Register", "%r10d"))
                    
                    instr1 = Assembly_node("Mov")
                    instr1.child = {
                        "src": instr.child["src"],
                        "dst": r10d
                    }

                    instr2 = Assembly_node(instr.ident)
                    instr2.child = {
                        "src": r10d,
                        "dst": instr.child["dst"]
                    }

                    if instr.ident == "Binary":
                        instr2.child["op"] = instr.child["op"]

                    instructions[i] = instr1
                    instructions.insert(i+1, instr2)
        i += 1