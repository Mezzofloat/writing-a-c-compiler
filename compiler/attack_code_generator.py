from ASTNode import C_node, ATTACK_node

# generate attack ast (ATTACK: A Temporary Three Address Code Kompiler)

tmp_var_idx = 0

def make_tmp():
    global tmp_var_idx

    s = '.Ltmp.' + str(tmp_var_idx)
    tmp_var_idx += 1
    return s

def make_branch_label():
    global tmp_var_idx

    s = '.Lbrn.' + str(tmp_var_idx)
    tmp_var_idx += 1
    return s

# NO NESTING, so must be sequential
# Constant, Variable, Unary
def exp_to_attack(exp_node : C_node, instruc):
    match exp_node.ident:
        case "Return":
            exp = exp_to_attack(exp_node.child, instruc)
            r = ATTACK_node("Return", exp)

            instruc.append(r)
            return r
        case "Unary":
            op = exp_to_attack(exp_node.child["op"], instruc)
            src = exp_to_attack(exp_node.child["inner_exp"], instruc)

            dst_ident = ATTACK_node(("Identifier", make_tmp()))
            dst = ATTACK_node("Variable", dst_ident)

            un = ATTACK_node("Unary", {
                "op": op,
                "src": src,
                "dst": dst
            })

            instruc.append(un)
            return dst
        case "Binary":
            op = exp_to_attack(exp_node.child["op"], instruc)

            if not op: # op is && or ||
                if exp_node.child["op"].ident == "And":
                    condition = "JumpIfZero"
                    calc_result = 1
                elif exp_node.child["op"].ident == "Or":
                    condition = "JumpIfNotZero"
                    calc_result = 0
                else:
                    raise ValueError("Invalid operation that returned null")

                left = exp_to_attack(exp_node.child["left"], instruc)

                false_label = ATTACK_node(("Identifier", make_branch_label()))
                check_left = ATTACK_node(condition, {
                    "cond": left,
                    "label": false_label
                })
                instruc.append(check_left)

                right = exp_to_attack(exp_node.child["right"], instruc)

                check_right = ATTACK_node(condition, {
                    "cond": right,
                    "label": false_label
                })

                dst_ident = ATTACK_node(("Identifier", make_tmp()))
                dst = ATTACK_node("Variable", dst_ident)

                result_calculated = ATTACK_node("Unary", {
                    "op": ATTACK_node("Copy"),
                    "src": ATTACK_node(("Constant", calc_result)),
                    "dst": dst
                })

                end_label = ATTACK_node(("Identifier", make_branch_label()))

                jump_to_end = ATTACK_node("Jump", end_label)

                result_shorted = ATTACK_node("Unary", {
                    "op": ATTACK_node("Copy"),
                    "src": ATTACK_node(("Constant", 1-calc_result)),
                    "dst": dst
                })

                instruc.extend([check_right, result_calculated, jump_to_end, false_label, result_shorted, end_label])

                return dst
            else:
                left = exp_to_attack(exp_node.child["left"], instruc)
                right = exp_to_attack(exp_node.child["right"], instruc)

                dst_ident = ATTACK_node(("Identifier", make_tmp()))
                dst = ATTACK_node("Variable", dst_ident)

                bin = ATTACK_node("Binary", {
                    "op": op,
                    "src1": left,
                    "src2": right,
                    "dst": dst
                })

                instruc.append(bin)
                return dst
        case "Equal" | "NotEqual" | "LessThan" | "LessOrEqual" | "GreaterThan" | "GreaterOrEqual" | "Not" | "Complement" | "Negate" | "Add" | "Sub" | "Multiply" | "Divide" | "Modulus" | ("Constant", _):
            return ATTACK_node(exp_node.ident)
        case "And" | "Or" :
            return None
        case _:
            raise ValueError(f"Given invalid expression node: {exp_node}")

    #print(f"I am returning nothing because I am {exp_node}")

def c_to_attack(node : C_node):
    match node.ident:
        case "Function":

            insts = ATTACK_node("Instructions", [])

            exp_to_attack(node.child["body"], insts.child)

            func = ATTACK_node("Function", {
                "name": node.child["name"],
                "instructions": insts
            })
            return func
        case _:
            if node.child:
                child = c_to_attack(node.child)
                parent = ATTACK_node(node.ident, child)
            else:
                parent = ATTACK_node(node.ident)

            return parent
