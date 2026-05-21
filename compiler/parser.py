from ASTNode import C_node

token_idx = 0
tokens = []

# For both C and Assembly, a node with multiple args will use a dict, so an arg with a list (such as instructions) is free to use lists as needed

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
    node = C_node("Program")
    node.child = func

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
    statement = parse_statement()
    expect("}")

    node = C_node("Function")
    node.child = {
        "name": ident,
        "body": statement
    }
    return node

def parse_statement() -> C_node:
    global token_idx

    expect("return")
    exp = parse_exp(0)
    expect(";")

    node = C_node("Return")
    node.child = exp
    return node

def parse_factor() -> C_node:
    global token_idx

    next = tokens[token_idx]

    if type(next) is tuple and next[0] == "Constant":
        num = parse_int()
        node = C_node("Expression")
        node.child = num
        return node
    elif next == "~" or next == "-":
        operator = parse_unop()
        inner_exp = parse_factor()

        node = C_node("Unary")
        node.child = {
            "op": operator,
            "inner_exp": inner_exp
        }
        return node
    elif next == "(":
        token_idx += 1
        inner_exp = parse_exp(0)
        expect(")")

        return inner_exp
    
    raise SyntaxError(f"Expected expression but got {tokens[token_idx]}")

bin_precedence = {
    "*": 1,
    "/": 1,
    "%": 1,
    "+": 0,
    "-": 0
}

def parse_exp(min_prec: int) -> C_node:
    left = parse_factor()
    next = tokens[token_idx]
    while next in bin_precedence and bin_precedence[next] >= min_prec:
        operator = parse_binop()
        right = parse_exp(bin_precedence[next] + 1)

        new = C_node("Binary")
        new.child = {
            "op": operator,
            "left": left,
            "right": right
        }

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