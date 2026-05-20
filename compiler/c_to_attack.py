from ASTNode import C_node, ATTACK_node

# generate attack ast (ATTACK: A Temporary Three Address Code Kompiler)

tmp_var_idx = 0

def make_tmp():
    global tmp_var_idx

    s = str(tmp_var_idx) + ".tmp"
    tmp_var_idx += 1
    return s

# NO NESTING, so must be sequential
# Constant, Variable, Unary
def exp_to_attack(exp_node : C_node, instruc):
    if exp_node.child:
        match exp_node.ident:
            case "Return":
                r = ATTACK_node("Return")
                exp = exp_to_attack(exp_node.child, instruc)
                r.child = exp

                instruc.append(r)
                return r
            case "Expression":
                return exp_to_attack(exp_node.child, instruc)
            case "Unary":
                un = ATTACK_node("Unary")

                op = exp_to_attack(exp_node.child["op"], instruc)

                src = exp_to_attack(exp_node.child["inner_exp"], instruc)

                dst = ATTACK_node("Variable")
                dst_ident = ATTACK_node(("Identifier", make_tmp()))
                dst.child = dst_ident

                un.child = {
                    "op": op,
                    "src": src,
                    "dst": dst
                }

                instruc.append(un)
                return dst
            case "Complement":
                return ATTACK_node("Complement")
            case "Negate":
                return ATTACK_node("Negate")
            case _:
                raise ValueError(f"Given invalid expression node: {exp_node}")
    else:
        return ATTACK_node(exp_node.ident)

    #print(f"I am returning nothing because I am {exp_node}")

def c_to_attack(node : C_node):
    match node.ident:
        case "Function":
            func = ATTACK_node("Function")

            insts = ATTACK_node("Instructions")
            insts.child = []

            exp_to_attack(node.child["body"], insts.child)

            func.child = {
                "name": node.child["name"],
                "instructions": insts
            }
            return func
        case _:
            parent = ATTACK_node(node.ident)
            
            if node.child:
                child = c_to_attack(node.child)
                parent.child = child

            return parent
