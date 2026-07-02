from astnode.c_node import C_node

temp_idx = 0
def get_temp(initial):
    global temp_idx
    unique = f"{initial}_{temp_idx}"
    temp_idx += 1
    return unique

variable_map = {}
def resolve_declaration(node):
    name = node.child["name"].ident[1]
    if name in variable_map:
        raise RuntimeError(f"Variable {name} already declared")
    unique = get_temp(name)
    variable_map[name] = unique

    init = node.child["init"]
    newinit = None
    if init is not None:
        newinit = resolve_exp(init)

    return C_node("Declaration", {
        "name": C_node(("Identifier", unique)),
        "init": newinit
    })

def resolve_statement(node):
    if node is None:
        return None

    statement = node.child
    if statement.ident == "Return":
        exp = resolve_exp(statement.child)
        return C_node("Statement", C_node("Return", exp))
    elif statement.ident == "Null":
        return node
    elif statement.ident == "If":
        return C_node("Statement", C_node("If", {
            "cond": resolve_exp(statement.child["cond"]),
            "then": resolve_statement(statement.child["then"]),
            "else": resolve_statement(statement.child["else"])
        }))
    else:
        exp = resolve_exp(statement)
        return C_node("Statement", exp)

def resolve_exp(node):
    match node.ident:
        case "Assignment":
            if node.child["lvalue"].ident != "Var":
                raise RuntimeError("Left-hand side of assignment must be a variable")
            return C_node("Assignment", {
                "lvalue": resolve_exp(node.child["lvalue"]),
                "exp": resolve_exp(node.child["exp"])
            })
        case "Var":
            if node.child.ident[1] not in variable_map:
                raise RuntimeError(f"Variable {node.child.ident[1]} not declared")
            return C_node("Var", C_node(("Identifier", variable_map[node.child.ident[1]])))
        case "Unary":
            return C_node("Unary", {
                "op": node.child["op"],
                "inner_exp": resolve_exp(node.child["inner_exp"])
            })
        case "Binary":
            return C_node("Binary", {
                "op": node.child["op"],
                "left": resolve_exp(node.child["left"]),
                "right": resolve_exp(node.child["right"])
            })
        case ("Constant", _):
            return node
        case "Conditional":
            return C_node("Conditional", {
                "cond": resolve_exp(node.child["cond"]),
                "true": resolve_exp(node.child["true"]),
                "false": resolve_exp(node.child["false"])
            })