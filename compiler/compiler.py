#!/usr/bin/env python3
from enum import Enum
import argparse
import sys
import os
import re

class ASTNode:
    def __init__(self, ident):
        self.ident = ident
        self.child = None

    def __str__(self):
        def tabbify(string: str) -> str:
            # for each newline but the last, add a tab after it
            newstr = ""

            for i in range(len(string)):
                newstr += string[i]
                if string[i] == "\n" and i != len(string) - 2:
                    newstr += "\t"
            
            return newstr
        
        def print_list(lst: list) -> str:
            s = ["[\n"]
            for item in lst:
                s.append(str(item) + ",\n")
            s.append("]")

            return "".join(s)
        
        s = []

        # print only the value, not the type
        if type(self.ident) is tuple:
            s.append(self.ident[1])
        else:
            s.append(self.ident)

        # only adds if there are children
        if self.child:
            s.append("(\n")

            # consider the dictionaries
            if type(self.child) is dict:
                for child in self.child:
                    s.append(f"{child}=")
                    if type(self.child[child]) is list:
                        s.append(print_list(self.child[child]))
                    else:
                        s.append(f"{str(self.child[child])}\n")
            # consider the lists
            elif type(self.child) is list:
                s.append(print_list(self.child))
            else: 
                s.append(str(self.child))

            s.append("\n)")

        return tabbify("".join(s))

class C_node(ASTNode):
    pass

class Assembly_node(ASTNode):
    pass

parser = argparse.ArgumentParser()
parser.add_argument('path', help="Path to the file to compile")
parser.add_argument('--lex', action="store_true")
parser.add_argument('--parse', action="store_true")
parser.add_argument('--codegen', action="store_true")
parser.add_argument('-S', action="store_true")

args = parser.parse_args()
if len(args.path) < 1 or not args.path.endswith('.c'):
    exit(1)

preprocessed = args.path[:-2] + '.i'
assembly = args.path[:-2] + '.s'
executable = args.path[:-2]

# preprocess source file
os.system(f"gcc -E -P {args.path} -o {preprocessed}")
#print("\nCommand prompt executed\n")

# lex path.i
if not os.path.exists(preprocessed):
    raise RuntimeError("File is unavailable")

with open(preprocessed, 'r') as file:
    content = file.read()

tokens = []
keywords = ["int", "void", "return"]
token_matchers = [r"[a-zA-Z_]\w*\b", r"[0-9]+\b", r"\(", r"\)", r"{", r"}", r";"]
token_types = ["ident", "constant", "int", "void", "return", "(", ")", "{", "}", ";"]
while content != "":
    # trim whitespace
    whitespace = re.match(r"\s+", content)
    if whitespace:
        content = content[len(whitespace[0]):]
    else:
        startMatch = False
        for matcher in token_matchers:
            m = re.match(matcher, content)
            if m:
                startMatch = True
                if matcher == r"[a-zA-Z_]\w*\b":
                    if m[0] in keywords:
                        tokens.append((m[0]))
                    else:
                        tokens.append(("Identifier", m[0]))
                elif matcher == r"[0-9]+\b":
                    tokens.append(("Constant", m[0]))
                else:
                    tokens.append((m[0]))
                content = content[len(m[0]):]
                break

        if not startMatch:
            raise ValueError
        
#print(tokens)

if args.lex:
    print('stopping at lex')
    exit(0)

# parse tokens[]

# For both C and Assembly, a node with multiple args will use a dict, so an arg with a list (such as instructions) is free to use lists

token_idx = 0

def expect(keyword: str):
    global token_idx

    if (tokens[token_idx] != keyword):
        raise SyntaxError(f"Expected {keyword} but got {tokens[token_idx]}")
    else:
        token_idx += 1

def parse_program() -> C_node:
    func = parse_function()
    node = C_node("Program")
    node.child = func
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

C_ast = parse_program()
#print(C_ast)

if token_idx < len(tokens):
    print("did not account for every token")
    raise SyntaxError("Too many tokens")

if args.parse:
    print('stopping at parse')
    exit(0)

# generate assembly ast
# traverse the tree given in C_ast
def convert_to_assembly_ast(node: C_node) -> Assembly_node:
    if type(node.ident) is tuple:
        return Assembly_node(node.ident)

    match node.ident:
        case "Program":
            func = convert_to_assembly_ast(node.child)

            n = Assembly_node("Program")
            n.child = func
            return n
        case "Function":
            instructions = convert_to_assembly_ast(node.child["body"])

            n = Assembly_node("Function")
            n.child = {
                "name": node.child["name"],
                "instructions": instructions
            }
            return n
        case "Return":
            exp = convert_to_assembly_ast(node.child)

            reg = Assembly_node(("Reg", "%eax"))

            mov = Assembly_node("Mov")
            mov.child = {
                "src": exp,
                "dst": reg
            }

            ret = Assembly_node("Ret")

            n = Assembly_node("Instructions")
            n.child = [mov, ret]

            return n
        case "Expression":
            imm = Assembly_node("Imm")

            num = convert_to_assembly_ast(node.child)
            imm.child = num
            return imm
    
    raise SyntaxError(f"Unknown node in tree: {str(node)}")

Assembly_ast = convert_to_assembly_ast(C_ast)
#print(Assembly_ast)

if args.codegen:
    print('stopping at codegen')
    exit(0)

# emit the code for each node in the tree

def emit_code(node: Assembly_node) -> str:
    if type(node.ident) is tuple:
        return str(node.ident[1])
    
    match node.ident:
        case "Program":
            s = "\t.file	\"return_2.c\"\n\t.text\n\t.globl	main\n\t.type	main, @function\n"
            s += emit_code(node.child)
            s += "\t.section .note.GNU-stack,\"\",@progbits"
            return s
        case "Function":
            s = emit_code(node.child["name"]) + ":\n"
            s += emit_code(node.child["instructions"])
            return s
        case "Instructions":
            s = ""
            for inst in node.child:
                s += "\t" + emit_code(inst) + "\n"
            return s
        case "Mov":
            s = f"movl\t{emit_code(node.child["src"])}, {emit_code(node.child["dst"])}"
            return s
        case "Ret":
            return "ret"
        case "Imm":
            return f"${emit_code(node.child)}"


with open(assembly, "a") as f:
    print(emit_code(Assembly_ast), file=f)

# assemble and link
os.system(f"gcc {assembly} -o {executable}")