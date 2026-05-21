#!/usr/bin/env python3

from assembly_converter import attack_to_assembly_ast, replace_pseudo_registers, fix_instructions
from attack_code_generator import c_to_attack
from code_emitter import emit_code
from parser import parse_program
from lexer import lex
import argparse
import sys
import os

argparser = argparse.ArgumentParser()
argparser.add_argument('path', help="Path to the file to compile")
argparser.add_argument('--lex', action="store_true")
argparser.add_argument('--parse', action="store_true")
argparser.add_argument('--codegen', action="store_true")
argparser.add_argument('--tacky', action='store_true')
argparser.add_argument('-S', action="store_true")

args = argparser.parse_args()
if len(args.path) < 1 or not args.path.endswith('.c'):
    exit(1)

preprocessed = args.path[:-2] + '.i'
assembly = args.path[:-2] + '.s'
executable = args.path[:-2]

# preprocess source file
os.system(f"gcc -E -P {args.path} -o {preprocessed}")
#print("\nCommand prompt executed\n")

if not os.path.exists(preprocessed):
    raise RuntimeError("File is unavailable")

with open(preprocessed, 'r') as file:
    file_contents = file.read()

# lex path.i
tokens = lex(file_contents)
        
#print(tokens)

if args.lex:
    print('stopping at lex')
    exit(0)

# parse tokens[]

C_ast = parse_program(tokens)
print("C_ast:")
print(C_ast)

if args.parse:
    print('stopping at parse')
    exit(0)

#exp_to_attack(C_ast.child.child["body"])
ATTACK_ast = c_to_attack(C_ast)
print("ATTACK_ast:")
print(ATTACK_ast)

# --tacky is required by the books' tests i'm using
if args.tacky:
    print('stopping at attack gen')
    exit(0)

# generate assembly ast
Assembly_ast = attack_to_assembly_ast(ATTACK_ast)
print("First Assembly_ast:")
print(Assembly_ast)

replace_pseudo_registers(Assembly_ast)
print("Non-pseudo ast:")
print(Assembly_ast)

fix_instructions(Assembly_ast)
print("Fixed-instructions ast:\n")
print(Assembly_ast)

if args.codegen:
    print('stopping at codegen')
    exit(0)

# emit the code for each node in the tree

with open(assembly, "w") as f:
    print(emit_code(Assembly_ast), file=f)

# assemble and link
os.system(f"gcc {assembly} -o {executable}")