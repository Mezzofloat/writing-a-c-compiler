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
    exp = parse_exp()
    expect(";")

    node = C_node("Return")
    node.child = exp
    return node

def parse_exp() -> C_node:
    global token_idx

    next = parse_int()
    node = C_node("Expression")
    node.child = next
    return node

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