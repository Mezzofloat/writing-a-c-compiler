from ASTNode import ATTACK_node, Assembly_node

allocate_offset = 0

# traverse the tree given in attack_ast
def attack_to_assembly_ast(node: ATTACK_node) -> Assembly_node:
    match node.ident:
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

    print(f"Instructions are as follows: {instructions}")
    for instr in instructions:
        if instr.child:
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

    for i in range(len(instructions)):
        instr = instructions[i]

        if instr.child and type(instr.child) is dict:
            if "src" in instr.child and "dst" in instr.child:
                if instr.child["src"].ident[0] == "Stack" and instr.child["dst"].ident[0] == "Stack":
                    r10d = Assembly_node(("Register", "%r10d"))
                    
                    instr1 = Assembly_node(instr.ident)
                    instr1.child = {
                        "src": instr.child["src"],
                        "dst": r10d
                    }

                    instr2 = Assembly_node(instr.ident)
                    instr2.child = {
                        "src": r10d,
                        "dst": instr.child["dst"]
                    }

                    instructions[i] = instr1
                    instructions.insert(i+1, instr2)