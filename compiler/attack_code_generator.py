from astnode.c_node import C_node
from astnode.attack_node import ATTACK_node

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
        case "Var":
            return ATTACK_node("Variable", exp_node.child)
        case "Assignment":
            result = exp_to_attack(exp_node.child["exp"], instruc)
            variable = exp_to_attack(exp_node.child["lvalue"], instruc)
            instruc.append(ATTACK_node("Unary", {
                "op": ATTACK_node("Copy"),
                "src": result,
                "dst": variable
            }))
            return variable
        case "Conditional":
            cond = exp_to_attack(exp_node.child["cond"], instruc)
            e2_label = ATTACK_node(("Identifier", make_branch_label()))
            end_label = ATTACK_node(("Identifier", make_branch_label()))
            
            jump_if_zero = ATTACK_node("JumpIfZero", {
                "cond": cond,
                "label": e2_label
            })
            instruc.append(jump_if_zero)

            result = ATTACK_node("Variable", ATTACK_node(("Identifier", make_tmp())))

            e1 = exp_to_attack(exp_node.child["true"], instruc)
            copy_e1 = ATTACK_node("Unary", {
                "op": ATTACK_node("Copy"),
                "src": e1,
                "dst": result
            })
            instruc.append(copy_e1)

            jump_to_end = ATTACK_node("Jump", end_label)
            instruc.append(jump_to_end)
            
            instruc.append(e2_label)

            e2 = exp_to_attack(exp_node.child["false"], instruc)
            copy_e2 = ATTACK_node("Unary", {
                "op": ATTACK_node("Copy"),
                "src": e2,
                "dst": result
            })
            instruc.append(copy_e2)

            instruc.append(end_label)
            return result
        case _:
            raise ValueError(f"Given invalid expression node: {exp_node}")

    #print(f"I am returning nothing because I am {exp_node}")

def statement_to_attack(statement_node : C_node, instruc):
    statement = statement_node.child
    print(statement.ident)
    if statement.ident == "If":
        cond = exp_to_attack(statement.child["cond"], instruc)
        
        end_label = ATTACK_node(("Identifier", make_branch_label()))
        if statement.child["else"]:
            else_label = ATTACK_node(("Identifier", make_branch_label()))
        else:
            else_label = end_label

        jump_if_zero = ATTACK_node("JumpIfZero", {
            "cond": cond,
            "label": else_label
        })
        
        instruc.append(jump_if_zero)

        statement_to_attack(statement.child["then"], instruc)
        jump_to_end = ATTACK_node("Jump", end_label)
        instruc.append(jump_to_end)

        if statement.child["else"]:
            instruc.append(else_label)
            statement_to_attack(statement.child["else"], instruc)
        instruc.append(end_label)

    elif statement.ident != "Null":
        exp_to_attack(statement, instruc)

def c_to_attack(node : C_node):
    match node.ident:
        case "Function":
            insts = []

            for block_item in node.child["body"]:
                block_child = block_item.child
                if block_child.ident == "Statement":
                    statement_to_attack(block_child, insts)
                elif block_child.ident == "Declaration":
                    if block_child.child["init"]:
                        assignment = C_node("Assignment", {
                            "lvalue": C_node("Var", block_child.child["name"]),
                            "exp": block_child.child["init"]
                        })
                        exp_to_attack(assignment, insts)

            newinsts = []

            for inst in insts:
                newinsts.append(ATTACK_node("Instruction", inst))
            
            return_zero = ATTACK_node("Return", ATTACK_node(("Constant", 0)))
            newinsts.append(ATTACK_node("Instruction", return_zero))

            func = ATTACK_node("Function", {
                "name": node.child["name"],
                "instructions": newinsts
            })
            return func
        case _:
            if node.child:
                child = c_to_attack(node.child)
                parent = ATTACK_node(node.ident, child)
            else:
                parent = ATTACK_node(node.ident)

            return parent
