from astnode.attack_node import ATTACK_node
from astnode.risc_node import RISC_node

# based on my work in x86_converter.py

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
            
            newinst = []

            for instr in node.child["instructions"]:
                outcome = attack_to_risc_ast(instr)

                if type(outcome) is list:
                    for entry in outcome:
                        newinst.append(RISC_node("Instruction", entry))

                else:
                    newinst.append(RISC_node("Instruction", outcome))

            return RISC_node("Function", {
                "name": name,
                "instructions": newinst
            })
        case ("Identifier", _):
            return RISC_node(node.ident)
        case "Instruction":
            return attack_to_risc_ast(node.child)
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
                # cheeky balatro reference
                chips = attack_to_risc_ast(node.child["src1"])
                mult = attack_to_risc_ast(node.child["src2"])
                #print(chips)

                chips_reg = RISC_node(("Register", "a3"))
                mult_reg = RISC_node(("Register", "a4"))
                result_reg = RISC_node(("Register", "a2"))
                const_five = RISC_node(("Register", "t0"))
                quintuple_chips_reg = RISC_node(("Register", "t1"))

                # prologue
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

                load_five = RISC_node("Load", {
                    "src": RISC_node(("Imm", 5)),
                    "dst": const_five
                })

                load_quintuple_chips = RISC_node("Load", {
                    "src": chips,
                    "dst": quintuple_chips_reg
                })

                make_quintuple_chips_1 = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": quintuple_chips_reg,
                    "src2": chips_reg,
                    "dst": quintuple_chips_reg
                })
                make_quintuple_chips_2 = make_quintuple_chips_1
                make_quintuple_chips_3 = make_quintuple_chips_1
                make_quintuple_chips_4 = make_quintuple_chips_1

                # quintuple speed loop
                uniq_quint = RISC_node(("Identifier", create_uniq_ident() + 'q'))
                ident_quint = uniq_quint
                end_quint = RISC_node(("Identifier", f"end{uniq_quint.ident[1]}"))

                branch_quint = RISC_node("Branch", {
                    "cond": RISC_node("LtU"),
                    "src1": mult_reg,
                    "src2": const_five,
                    "branch": end_quint
                })

                add_chips_quint = RISC_node("Binary", {
                    "op": RISC_node("Add"),
                    "src1": result_reg,
                    "src2": quintuple_chips_reg,
                    "dst": result_reg
                })

                sub_mult_quint = RISC_node("Binary", {
                    "op": RISC_node("Sub"),
                    "src1": mult_reg,
                    "src2": const_five,
                    "dst": mult_reg
                })

                jump_loop_quint = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_quint
                })
                
                # loop
                uniq = RISC_node(("Identifier", create_uniq_ident()))
                ident_loop = uniq
                end_loop = RISC_node(("Identifier", f"end{uniq.ident[1]}"))
                
                branch = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": mult_reg,
                    "branch": end_loop
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

                jump_loop = RISC_node("Branch", {
                    "cond": RISC_node("Eq"),
                    "src1": RISC_node(("Register", "x0")),
                    "src2": RISC_node(("Register", "x0")),
                    "branch": ident_loop
                })

                store_back = RISC_node("Store", {
                    "src": result_reg,
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return [load_chips, load_mult, load_zero, load_five, load_quintuple_chips, make_quintuple_chips_1, make_quintuple_chips_2, make_quintuple_chips_3, make_quintuple_chips_4,
                        ident_quint, branch_quint, add_chips_quint, sub_mult_quint, jump_loop_quint, end_quint,
                        ident_loop, branch, add_chips, sub_mult, jump_loop, end_loop,
                        store_back]
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

            diff = RISC_node(("Register", "a7"))
            zero = RISC_node(("Register", "x0"))

            dst = attack_to_risc_ast(node.child["dst"])

            one = RISC_node(("Imm", 1))
            reg_one = RISC_node(("Register", "t0"))
            load_one = RISC_node("Load", {
                "src": one,
                "dst": reg_one
            })
            match op:
                case 'Equal':
                    opcode = 'Eq'

                    setcond = RISC_node("SetLessThanU", {
                        "src1": diff,
                        "src2": reg_one,
                        "dst": dst
                    })
                case 'NotEqual':
                    opcode = 'Ne'

                    setcond = RISC_node("SetLessThanU", {
                        "src1": diff,
                        "src2": reg_one,
                        "dst": dst
                    })

                    xori = RISC_node("Binary", {
                        "op": RISC_node("Xor"),
                        "src1": dst,
                        "src2": one,
                        "dst": dst
                    })
                case 'GreaterThan':
                    opcode = 'Gt'

                    setcond = RISC_node("SetLessThan", {
                        "src1": zero,
                        "src2": diff,
                        "dst": dst
                    })
                case 'GreaterOrEqual':
                    opcode = 'Ge'

                    setcond = RISC_node("SetLessThan", {
                        "src1": diff,
                        "src2": zero,
                        "dst": dst
                    })

                    xori = RISC_node("Binary", {
                        "op": RISC_node("Xor"),
                        "src1": dst,
                        "src2": one,
                        "dst": dst
                    })
                case 'LessThan':
                    opcode = 'Lt'
                    
                    setcond = RISC_node("SetLessThan", {
                        "src1": diff,
                        "src2": zero,
                        "dst": dst
                    })
                case 'LessOrEqual':
                    opcode = 'Le'

                    setcond = RISC_node("SetLessThan", {
                        "src1": zero,
                        "src2": diff,
                        "dst": dst
                    })

                    xori = RISC_node("Binary", {
                        "op": RISC_node("Xor"),
                        "src1": dst,
                        "src2": one,
                        "dst": dst
                    })
                case _:
                    opcode = None

            if opcode:
                cmp = RISC_node("Binary", {
                    "op": RISC_node("Sub"),
                    "src1": attack_to_risc_ast(node.child["src1"]),
                    "src2": attack_to_risc_ast(node.child["src2"]),
                    "dst": diff
                })

                try:
                    return [cmp, load_one, setcond, xori]
                except NameError:
                    return [cmp, load_one, setcond]
            else: 
                bin = RISC_node("Binary", {
                    "op": attack_to_risc_ast(node.child["op"]),
                    "src1": attack_to_risc_ast(node.child["src1"]),
                    "src2": attack_to_risc_ast(node.child["src2"]),
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return bin

        case "Unary":
            if node.child["op"].ident == "Not":
                load_one = RISC_node("Load", {
                    "src": RISC_node(("Imm", 1)),
                    "dst": RISC_node(("Register", "t0"))
                })
                
                setless = RISC_node("SetLessThanU", {
                    "src1": attack_to_risc_ast(node.child["src"]),
                    "src2": RISC_node(("Register", "t0")),
                    "dst": attack_to_risc_ast(node.child["dst"])
                })

                return [load_one, setless]
            else:
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
        case "Copy":
            return RISC_node("Mov")
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
        case "JumpIfZero":
            return RISC_node("Branch", {
                "cond": RISC_node("Eq"),
                "src1": RISC_node(("Register", "x0")),
                "src2": attack_to_risc_ast(node.child["cond"]),
                "branch": attack_to_risc_ast(node.child["label"])
            })
        case "JumpIfNotZero":
            return RISC_node("Branch", {
                "cond": RISC_node("Ne"),
                "src1": RISC_node(("Register", "x0")),
                "src2": attack_to_risc_ast(node.child["cond"]),
                "branch": attack_to_risc_ast(node.child["label"])
            })
        case "Jump":
            return RISC_node("Branch", {
                "cond": RISC_node("Eq"),
                "src1": RISC_node(("Register", "x0")),
                "src2": RISC_node(("Register", "x0")),
                "branch": attack_to_risc_ast(node.child)
            })
        case "Equal":
            return RISC_node("Eq")
        case "NotEqual":
            return RISC_node("Ne")
        case "GreaterThan":
            return RISC_node("Gt")
        case "GreaterOrEqual":
            return RISC_node("Ge")
        case "LessThan":
            return RISC_node("Lt")
        case "LessOrEqual":
            return RISC_node("Le")

def replace_pseudo_registers(ast: RISC_node):
    if ast.ident == "Program":
        if type(ast.child) is list:
            for func in ast.child:
                replace_pseudo_registers(func)
        else:
            replace_pseudo_registers(ast.child)
    elif ast.ident == "Function":
        replace_pseudo(ast.child["instructions"])
    else:
        raise ValueError(f"Replace function called on {ast}")

def replace_pseudo(instructions: list[RISC_node]):
    global allocate_offset

    offset = 0
    mappings = {}

    unwrapped_instructions = []
    for instr in instructions:
        unwrapped_instructions.append(instr.child)

    for inst in unwrapped_instructions:
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
        fix(ast.child["instructions"])
    else:
        raise ValueError(f"fix_instructions called on {ast}")

def fix(instructions: list[RISC_node]):
    unwrapped = [instr.child for instr in instructions]

    # formerly AllocateStack
    if allocate_offset > 0:
        amount = RISC_node(("Imm", -allocate_offset))
        sp = RISC_node(("Register", "sp"))
        new_inst = RISC_node("Binary", {
            "op": RISC_node("Add"),
            "src1": sp,
            "src2": amount,
            "dst": sp
        })

        unwrapped.insert(0, new_inst)

    i = 0
    while i < len(unwrapped):
        instr = unwrapped[i]
        print(instr)
        
        if type(instr.child) is not dict:
            i += 1
            continue

        keep_away = ['Load', 'Store']

        if instr.ident in keep_away:
            i += 1
            continue

        rs1_scratch = RISC_node(("Register", "t3"))
        operand_scratch = rs1_scratch
        rs2_scratch = RISC_node(("Register", "t4"))
        dst_scratch = RISC_node(("Register", "t5"))

        if "src1" in instr.child:
            src1 = instr.child["src1"]
            if src1.ident[0] == "Imm" or src1.ident[0] == "Stack":
                load_src1 = RISC_node("Load", {
                    "src": src1,
                    "dst": rs1_scratch
                })

                unwrapped[i].child["src1"] = rs1_scratch
                unwrapped.insert(i, load_src1)
                i += 1
                continue

        accepted_imms = ['Add', 'Xor']

        if "src2" in instr.child:
            src2 = instr.child["src2"]
            if (src2.ident[0] == "Imm" and instr.child["op"].ident not in accepted_imms) or src2.ident[0] == "Stack":
                load_src2 = RISC_node("Load", {
                    "src": src2,
                    "dst": rs2_scratch
                })

                unwrapped[i].child["src2"] = rs2_scratch
                unwrapped.insert(i, load_src2)
                i += 1
                continue

        if "src" in instr.child:
            src = instr.child["src"]
            if instr.child["src"].ident[0] == "Stack" or src.ident[0] == "Imm":
                load_src = RISC_node("Load", {
                    "src": src,
                    "dst": operand_scratch
                })
                
                unwrapped[i].child["src"] = operand_scratch
                unwrapped.insert(i, load_src)
                i += 1
                continue

        if "dst" in instr.child:
            dst = instr.child["dst"]
            if dst.ident[0] == "Stack":
                store_dst = RISC_node("Store", {
                    "src": dst_scratch,
                    "dst": dst
                })

                unwrapped[i].child["dst"] = dst_scratch
                unwrapped.insert(i+1, store_dst)
                i += 2
                continue
        
        i += 1

    # Deallocate stack at the end
    if allocate_offset > 0:
        amount = RISC_node(("Imm", allocate_offset))
        sp = RISC_node(("Register", "sp"))

        new_inst = RISC_node("Binary", {
            "op": RISC_node("Add"),
            "src1": sp,
            "src2": amount,
            "dst": sp
        })

        unwrapped.insert(-3, new_inst) # insert before actual return
        unwrapped.insert(-1, new_inst) # insert before extra return
    
    instructions.clear()
    instructions.extend([RISC_node("Instruction", instr) for instr in unwrapped])