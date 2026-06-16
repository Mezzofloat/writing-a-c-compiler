from astnode.c_node import C_node

token_idx = 0
tokens = []

# For C, ATTACK, and both Assemblies, a node with multiple args will use a dict,
# so an arg with a list (such as instructions) is free to use lists as needed

def expect(keyword: str):
    global token_idx

    if (tokens[token_idx] != keyword):
        raise SyntaxError(f"Expected {keyword} but got {tokens[token_idx]}")
    else:
        token_idx += 1

# creates an abstract syntax tree of C nodes from a list of tokens
def parse_program(token_list) -> C_node:
    global token_idx
    global tokens

    tokens = token_list

    func = parse_function()
    node = C_node("Program", func)

    if token_idx < len(tokens):
        raise SyntaxError("Did not account for every token")
    return node

def parse_function() -> C_node:
    global token_idx

    expect("int")
    ident = parse_identifier()
    expect("(")
    expect("void")
    expect(")")
    expect("{")

    block_items = []
    while tokens[token_idx] != "}":
        block_items.append(parse_block_item())

    expect("}")

    node = C_node("Function", {
        "name": ident,
        "body": block_items
    })
    return node

def parse_block_item() -> C_node:
    global token_idx

    next = tokens[token_idx]

    if next == "int":
        return C_node("BlockItem", parse_declaration())
    else:
        return C_node("BlockItem", parse_statement())

def parse_statement() -> C_node:
    global token_idx

    next = tokens[token_idx]

    if next == "return":
        expect("return")
        exp = parse_exp(0)
        expect(";")

        node = C_node("Return", exp)
        return C_node("Statement", node)
    elif next == ";":
        expect(";")
        null = C_node("Null")
        return C_node("Statement", null)
    else:
        exp = parse_exp(0)
        expect(";")

        return C_node("Statement", exp)    

def parse_declaration() -> C_node:
    global token_idx

    expect("int")
    ident = parse_identifier()

    init = None
    if tokens[token_idx] == "=":
        token_idx += 1
        init = parse_exp(0)
    
    expect(";")

    node = C_node("Declaration", {
        "name": ident,
        "init": init
    })
    return node

def parse_factor() -> C_node:
    global token_idx

    next = tokens[token_idx]

    if type(next) is tuple and next[0] == "Constant":
        return parse_int()
    elif next == "~" or next == "-" or next == "!":
        operator = parse_unop()
        inner_exp = parse_factor()

        node = C_node("Unary", {
            "op": operator,
            "inner_exp": inner_exp
        })
        return node
    elif next == "(":
        token_idx += 1
        inner_exp = parse_exp(0)
        expect(")")

        return inner_exp
    elif type(next) is tuple and next[0] == "Identifier":
        var_ident = parse_identifier()

        return C_node("Var", var_ident)
    
    raise SyntaxError(f"Expected expression but got {tokens[token_idx]}")

bin_precedence = {
    "*": 100,
    "/": 100,
    "%": 100,
    "+": 90,
    "-": 90,
    "<": 70,
    "<=": 70,
    ">": 70,
    ">=": 70,
    "==": 60,
    "!=": 60,
    "&&": 20,
    "||": 10,
    "=": 1
}

def parse_exp(min_prec: int) -> C_node:
    global token_idx

    left = parse_factor()
    next = tokens[token_idx]
    while next in bin_precedence and bin_precedence[next] >= min_prec:
        if next == "=":
            token_idx += 1
            right = parse_exp(1)

            left = C_node("Assignment", {
                "lvalue": left,
                "exp": right
            })
            next = tokens[token_idx]
        else:
            operator = parse_binop()
            right = parse_exp(bin_precedence[next] + 10)

            new = C_node("Binary", {
                "op": operator,
                "left": left,
                "right": right
            })

            left = new
            next = tokens[token_idx]
    
    return left

def parse_unop() -> C_node:
    global token_idx

    next = tokens[token_idx]
    token_idx += 1

    match next:
        case "~":
            return C_node("Complement")
        case "-":
            return C_node("Negate")
        case "!":
            return C_node("Not")
    
    raise SyntaxError(f"Expected unary operator but got {next}")

def parse_binop() -> C_node:
    global token_idx

    next = tokens[token_idx]
    token_idx += 1

    match next:
        case "+":
            return C_node("Add")
        case "-":
            return C_node("Sub")
        case "*":
            return C_node("Multiply")
        case "/":
            return C_node("Divide")
        case "%":
            return C_node("Modulus")
        case "&&":
            return C_node("And")
        case "||":
            return C_node("Or")
        case "==":
            return C_node("Equal")
        case "!=":
            return C_node("NotEqual")
        case "<":
            return C_node("LessThan")
        case "<=":
            return C_node("LessOrEqual")
        case ">":
            return C_node("GreaterThan")
        case ">=":
            return C_node("GreaterOrEqual")
        
    raise SyntaxError(f"Expected binary operator but got {next}")

def parse_identifier() -> C_node:
    global token_idx

    ident = tokens[token_idx]

    if type(ident) is not tuple or ident[0] != "Identifier":
        raise SyntaxError("expected identifier, but got keyword")

    node = C_node(ident)
    token_idx += 1
    return node

def parse_int():
    global token_idx

    i = tokens[token_idx]
    if type(i) is not tuple or i[0] != "Constant":
        raise SyntaxError("expected integer, but got something else")
    node = C_node(i)
    token_idx += 1
    return node