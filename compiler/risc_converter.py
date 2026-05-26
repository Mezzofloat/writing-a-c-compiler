from ASTNode import ATTACK_node, RISC_node

# based on my work in assembly_converter.py

allocate_offset = 0

uniq_ident = 0
def create_uniq_ident():
    global uniq_ident
    uniq_ident += 1
    return f".L{uniq_ident}"

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
        
        case "Binary":
            op = node.child["op"].ident

            if op == "Multiply":
                uniq = RISC_node(("Identifier", create_uniq_ident()))
                ident_loop = uniq

                # cheeky balatro reference
                chips = attack_to_risc_ast(node.child["src1"])
                mult = attack_to_risc_ast(node.child["src2"])
                #print(chips)

                chips_reg = RISC_node(("Register", "a3"))
                mult_reg = RISC_node(("Register", "a4"))
                result_reg = RISC_node(("Register", "a2"))

                load_chips = RISC_node("Load", {
                    "src": chips,
                    "dst": chips_reg
                })

                load_mult = RISC_node("Load", {
                    "src": mult,
                    "dst": mult_reg
                })

                load_zero = RISC_node("Load", {
                    "src": RISC_node(("Imm", '0')),
                    "dst": result_reg
                })

                add_chips = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": result_reg,
                    "src2": chips_reg,
                    "dst": result_reg
                })

                sub_mult = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": mult_reg,
                    "src2": RISC_node(("Imm", -1)),
                    "dst": mult_reg
                })

                store_back = RISC_node("Store", {
                    "src": result_reg,
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                end_loop = RISC_node(("Identifier", f"end{uniq.ident[1]}"))

                branch = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": mult_reg,
                    "branch": end_loop
                })

                jump_loop = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                return [load_chips, load_mult, load_zero, ident_loop, branch, add_chips, sub_mult, jump_loop, end_loop, store_back]
            elif op == "Divide":
                dividend_reg = RISC_node(("Register", "a3"))
                divisor_reg = RISC_node(("Register", "a4"))
                result_reg = RISC_node(("Register", "a2"))

                load_dividend = RISC_node("Load", {
                    "src": attack_to_risc_ast(node.child["src1"]),
                    "dst": dividend_reg
                })

                load_divisor = RISC_node("Load", {
                    "src": attack_to_risc_ast(node.child["src2"]),
                    "dst": divisor_reg
                })

                load_zero = RISC_node("Load", {
                    "src": RISC_node(("Imm", 0)),
                    "dst": result_reg
                })

                load_zero_t6 = RISC_node("Load", {
                    "src": RISC_node(("Imm", 0)),
                    "dst": RISC_node(("Register", "t6"))
                })

                loop = create_uniq_ident()

                ident_loop = RISC_node(("Identifier", loop))
                end_loop = RISC_node(("Identifier", f"end{loop}"))

                branch_if_neg = RISC_node("Branch", {
                    "cond": RISC_node("Ge"),
                    "src1": dividend_reg,
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                negate_dividend = RISC_node("Unary", {
                    "op": RISC_node("Neg"),
                    "src": dividend_reg,
                    "dst": dividend_reg
                })

                checksum = RISC_node("Load", {
                    "src": RISC_node(("Imm", 1)),
                    "dst": RISC_node(("Register", "t6"))
                })

                branch = RISC_node("Branch", {
                    "cond": RISC_node("Lt"),
                    "src1": dividend_reg,
                    "src2": divisor_reg,
                    "branch": end_loop
                })

                sub_dividend = RISC_node("Binary", {
                    "op": RISC_node("Sub"),
                    "src1": dividend_reg,
                    "src2": divisor_reg,
                    "dst": dividend_reg
                })

                add_to_result = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": result_reg,
                    "src2": RISC_node(("Imm", 1)),
                    "dst": result_reg
                })

                jump_loop = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                skip_negate = RISC_node(("Identifier", create_uniq_ident()))

                branch_if_checksum = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "t6")),
                    "branch": skip_negate
                })

                negate_result = RISC_node("Unary", {
                    "op": RISC_node("Neg"),
                    "src": result_reg,
                    "dst": result_reg
                })

                store_back = RISC_node("Store", {
                    "src": result_reg,
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return [load_dividend, load_divisor, load_zero, load_zero_t6, branch_if_neg,
                        negate_dividend, checksum, ident_loop,
                        branch, sub_dividend, add_to_result, jump_loop,
                        end_loop, branch_if_checksum, negate_result, skip_negate, store_back]
            elif op == "Modulus":
                dividend_reg = RISC_node(("Register", "a3"))
                divisor_reg = RISC_node(("Register", "a4"))
                result_reg = RISC_node(("Register", "a2"))

                load_dividend = RISC_node("Load", {
                    "src": attack_to_risc_ast(node.child["src1"]),
                    "dst": dividend_reg
                })

                load_divisor = RISC_node("Load", {
                    "src": attack_to_risc_ast(node.child["src2"]),
                    "dst": divisor_reg
                })

                load_zero = RISC_node("Load", {
                    "src": RISC_node(("Imm", 0)),
                    "dst": result_reg
                })

                load_zero_t6 = RISC_node("Load", {
                    "src": RISC_node(("Imm", 0)),
                    "dst": RISC_node(("Register", "t6"))
                })

                loop = create_uniq_ident()

                ident_loop = RISC_node(("Identifier", loop))
                end_loop = RISC_node(("Identifier", f"end{loop}"))

                branch_if_neg = RISC_node("Branch", {
                    "cond": RISC_node("Ge"),
                    "src1": dividend_reg,
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                negate_dividend = RISC_node("Unary", {
                    "op": RISC_node("Neg"),
                    "src": dividend_reg,
                    "dst": dividend_reg
                })

                checksum = RISC_node("Load", {
                    "src": RISC_node(("Imm", 1)),
                    "dst": RISC_node(("Register", "t6"))
                })

                branch = RISC_node("Branch", {
                    "cond": RISC_node("Lt"),
                    "src1": dividend_reg,
                    "src2": divisor_reg,
                    "branch": end_loop
                })

                sub_dividend = RISC_node("Binary", {
                    "op": RISC_node("Sub"),
                    "src1": dividend_reg,
                    "src2": divisor_reg,
                    "dst": dividend_reg
                })

                add_to_result = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": result_reg,
                    "src2": RISC_node(("Imm", 1)),
                    "dst": result_reg
                })

                jump_loop = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                skip_negate = RISC_node(("Identifier", create_uniq_ident()))

                branch_if_checksum = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "t6")),
                    "branch": skip_negate
                })

                negate_result = RISC_node("Unary", {
                    "op": RISC_node("Neg"),
                    "src": dividend_reg,
                    "dst": dividend_reg
                })

                store_back = RISC_node("Store", {
                    "src": dividend_reg,
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return [load_dividend, load_divisor, load_zero, load_zero_t6, branch_if_neg,
                        negate_dividend, checksum, ident_loop,
                        branch, sub_dividend, add_to_result, jump_loop,
                        end_loop, branch_if_checksum, negate_result, skip_negate, store_back]

            else: 
                bin = RISC_node("Binary", {
                    "op": attack_to_risc_ast(node.child["op"]),
                    "src1": attack_to_risc_ast(node.child["src1"]),
                    "src2": attack_to_risc_ast(node.child["src2"]),
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return bin

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
        case "Add" | "Sub":
            return RISC_node(node.ident)
        case "Multiply":
            pass
        case "Divide":
            pass
        case "Modulus":
            pass # roughly the same as Divide


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
            # consider the binaries
            if "src1" in inst.child and inst.child["src1"].ident == "Pseudo":
                pseudo_ident = inst.child["src1"].child.ident[1]

                if pseudo_ident not in mappings:
                    mappings[pseudo_ident] = f"-{offset}"
                    offset += 4

                reg = RISC_node(("Stack", mappings[pseudo_ident]))

                inst.child["src1"] = reg
            
            if "src2" in inst.child and inst.child["src2"].ident == "Pseudo":
                pseudo_ident = inst.child["src2"].child.ident[1]

                if pseudo_ident not in mappings:
                    mappings[pseudo_ident] = f"-{offset}"
                    offset += 4

                reg = RISC_node(("Stack", mappings[pseudo_ident]))

                inst.child["src2"] = reg

            # consider the unaries
            if "src" in inst.child and inst.child["src"].ident == "Pseudo":
                pseudo_ident = inst.child["src"].child.ident[1]

                if pseudo_ident not in mappings:
                    mappings[pseudo_ident] = f"-{offset}"
                    offset += 4

                reg = RISC_node(("Stack", mappings[pseudo_ident]))

                inst.child["src"] = reg
            if "dst" in inst.child and inst.child["dst"].ident == "Pseudo":
                pseudo_ident = inst.child["dst"].child.ident[1]

                if pseudo_ident not in mappings:
                    mappings[pseudo_ident] = offset
                    offset += 4

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
    if allocate_offset > 0:
        amount = RISC_node(("Imm", allocate_offset))
        new_inst = RISC_node("AllocateStack", amount)

        instructions.insert(0, new_inst)

    i = 0
    while i < len(instructions):
        instr = instructions[i]

        if instr.ident == "Binary":
            op = instr.child["op"]
            src1 = instr.child["src1"]
            src2 = instr.child["src2"]
            dst = instr.child["dst"]

            src1_reg = RISC_node(("Register", "t3"))
            src2_reg = RISC_node(("Register", "t4"))
            dst_reg = RISC_node(("Register", "t5"))

            corrected_bin = []

            if src1.ident[0] == "Imm" or src1.ident[0] == "Stack":
                load_src1 = RISC_node("Load", {
                    "src": src1,
                    "dst": src1_reg
                })
                left = src1_reg

                corrected_bin.append(load_src1)
            else:
                left = src1

            if src2.ident[0] == "Imm" or src2.ident[0] == "Stack":
                load_src2 = RISC_node("Load", {
                    "src": src2,
                    "dst": src2_reg
                })
                right = src2_reg
                corrected_bin.append(load_src2)
            else:
                right = src2

            if dst.ident[0] == "Imm" or dst.ident[0] == "Stack":
                store_dst = RISC_node("Store", {
                    "src": dst_reg,
                    "dst": dst
                })
                result = dst_reg
            else:
                store_dst = None
                result = dst

            instructions[i] = RISC_node("Binary", {
                "op": op,
                "src1": left,
                "src2": right,
                "dst": result
            })

            if store_dst is not None:
                instructions.insert(i+1, store_dst)

            instructions[i:i] = corrected_bin

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
                if instr in instructions:
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
                if instr in instructions:
                    instructions.remove(instr)

                i += 1
                continue
        
        i += 1

"""
if instr.child["src1"].ident[0] == "Imm" and instr.child["src2"].ident[0] == "Imm":
                a = int(instr.child["src1"].ident[1])
                b = int(instr.child["src2"].ident[1])

                if instr.child["op"].ident == "Add":
                    imm = a + b
                elif instr.child["op"].ident == "Sub":
                    imm = a - b

                if instr.child["dst"].ident[0] == "Stack":
                    dst = RISC_node(("Register", "a5"))
                    store = RISC_node("Store", {
                        "src": dst,
                        "dst": instr.child["dst"]
                    })
                else:
                    dst = instr.child["dst"]

                li = RISC_node("Load", {
                    "src": RISC_node(("Imm", imm)),
                    "dst": dst
                })

                instructions.insert(i, li)
                if store is not None:
                    instructions.insert(i+1, store)

                if instr in instructions:
                    instructions.remove(instr)

                i += 1
                continue
            
            elif instr.child["op"].ident == "Sub" and instr.child["src1"].ident[0] == "Imm":
                instructions.insert(i, RISC_node("Load", {
                    "src": RISC_node(("Imm", instr.child["src1"].ident[1])),
                    "dst": instr.child["dst"]
                }))

                instructions.insert(i+1, RISC_node("Binary", {
                    "op": RISC_node("Sub"),
                    "src1": instr.child["dst"],
                    "src2": instr.child["src1"],
                    "dst": instr.child["dst"]
                }))

                if instr in instructions:
                    instructions.remove(instr)
                
                continue

            elif instr.child["src1"].ident[0] == "Imm":
                if instr.child["op"] != "Sub":
                    instructions[i] = RISC_node("Binary", {
                        "op": instr.child["op"],
                        "src1": instr.child["src2"],
                        "src2": instr.child["src1"],
                        "dst": instr.child["dst"]
                    })
                    continue

            if instr.child["op"].ident == "Sub" and instr.child["src2"].ident[0] == "Imm":
                if instr.child["dst"].ident[0] == "Stack":
                    load_dst = RISC_node(("Register", "a6"))
                    store = RISC_node("Store", {
                        "src": RISC_node(("Register", "a6")),
                        "dst": instr.child["dst"]
                    })
                else:
                    load_dst = instr.child["dst"]
                    store = None

                instructions.insert(i, RISC_node("Load", {
                    "src": RISC_node(("Imm", instr.child["src2"].ident[1])),
                    "dst": load_dst
                }))

                if store is not None:
                    instructions.insert(i+1, store)

                    instructions.insert(i+2, RISC_node("Binary", {
                        "op": RISC_node("Sub"),
                        "src1": instr.child["src1"],
                        "src2": instr.child["dst"],
                        "dst": instr.child["dst"]
                    }))
                else:
                    instructions.insert(i+1, RISC_node("Binary", {
                        "op": RISC_node("Sub"),
                        "src1": instr.child["src1"],
                        "src2": instr.child["dst"],
                        "dst": instr.child["dst"]
                    }))

                if instr in instructions:
                    instructions.remove(instr)
                
                continue

            if instr.child["src1"].ident[0] == "Stack":
                print(str(instr) + ' had src1 be a stack')
                t0 = RISC_node(("Register", "t0"))

                load = RISC_node("Load", {
                    "src": instr.child["src1"],
                    "dst": t0
                })

                newbin = RISC_node("Binary", {
                    "op": instr.child["op"],
                    "src1": t0,
                    "src2": instr.child["src2"],
                    "dst": instr.child["dst"]
                })

                instructions.insert(i, load)
                instructions.insert(i+1, newbin)
                if instr in instructions:
                    instructions.remove(instr)

                i += 1
                continue
                
            if instr.child["src2"].ident[0] == "Stack":
                print(str(instr) + ' had src2 be a stack')
                t1 = RISC_node(("Register", "t1"))

                load = RISC_node("Load", {
                    "src": instr.child["src2"],
                    "dst": t1
                })

                newbin = RISC_node("Binary", {
                    "op": instr.child["op"],
                    "src1": instr.child["src1"],
                    "src2": t1,
                    "dst": instr.child["dst"]
                })

                instructions.insert(i, load)
                instructions.insert(i+1, newbin)
                if instr in instructions:
                    instructions.remove(instr)

                i += 1
                continue

            if instr.child["dst"].ident[0] == "Stack":
                t2 = RISC_node(("Register", "t2"))

                newbin = RISC_node("Binary", {
                    "op": instr.child["op"],
                    "src1": instr.child["src1"],
                    "src2": instr.child["src2"],
                    "dst": t2
                })
                
                store = RISC_node("Store", {
                    "src": t2,
                    "dst": instr.child["dst"]
                })

                instructions.insert(i, newbin)
                instructions.insert(i+1, store)
                if instr in instructions:
                    instructions.remove(instr)

                i += 1
                continue
"""