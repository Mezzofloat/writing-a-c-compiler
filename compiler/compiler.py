#!/usr/bin/env python3
import argparse
import os

from lexer import lex
from parser import parse_program
from attack_code_generator import c_to_attack

import risc_converter
import risc_emitter
import x86_converter
import x86_emitter

argparser = argparse.ArgumentParser()
argparser.add_argument('path', help="Path to the file to compile")
argparser.add_argument('--lex', action="store_true")
argparser.add_argument('--parse', action="store_true")
argparser.add_argument('--codegen', action="store_true")
argparser.add_argument('--tacky', action='store_true')
argparser.add_argument('-S', action="store_true")

argparser.add_argument('--assembly-lang', '-l', choices=['risc-v', 'x86'])

args = argparser.parse_args()
if len(args.path) < 1 or not args.path.endswith('.c'):
    exit(1)

preprocessed = args.path[:-2] + '.i'
assembly = args.path[:-2] + '.s'
executable = args.path[:-2]

# preprocess source file
os.system(f"gcc -E -P {args.path} -o {preprocessed}")

if not os.path.exists(preprocessed):
    raise RuntimeError("File is unavailable")

with open(preprocessed, 'r') as file:
    file_contents = file.read()

# lex path.i
tokens = lex(file_contents)

if args.lex:
    print(tokens)
    print('stopping at lex')
    exit(0)

# parse tokens[]
C_ast = parse_program(tokens)
print("\nC_ast:")
print(C_ast)

if args.parse:
    print('stopping at parse')
    exit(0)

# convert the C AST generated earlier to an ATTACK AST
ATTACK_ast = c_to_attack(C_ast)
print("\nATTACK_ast:")
print(ATTACK_ast)

# --tacky is required by the books' tests i'm using
if args.tacky:
    print('stopping at attack gen')
    exit(0)

# this is where the table splits, risc-v and x86 have different ASTs
if args.assembly_lang == "risc-v":
    prefix = "/common/users/shared/cs211_s26_5678/rv32gc-ilp32/bin/riscv32-unknown-linux-gnu-"
    print("compiling for risc-v")

    convert = risc_converter.attack_to_risc_ast
    add_stacks = risc_converter.replace_pseudo_registers
    fix_insts = risc_converter.fix_instructions

    emit_code = risc_emitter.emit_risc
else:
    prefix = ""
    print("compiling for x86")

    convert = x86_converter.attack_to_x86_ast
    add_stacks = x86_converter.replace_pseudo_registers
    fix_insts = x86_converter.fix_instructions

    emit_code = x86_emitter.emit_x86

# generate and fix assembly ast based on whether it's for risc-v or x86
Assembly_ast = convert(ATTACK_ast)
print("First Assembly_ast:")
print(Assembly_ast)

add_stacks(Assembly_ast)
print("Non-pseudo ast:")
print(Assembly_ast)

fix_insts(Assembly_ast)
print("Fixed-instructions ast:")
print(Assembly_ast)

if args.codegen:
    print('stopping at codegen')
    exit(0)

# emit the assembly code for each node in the tree
with open(assembly, "w") as f:
    print(emit_code(Assembly_ast), file=f)

# assemble and link
os.system(f"{prefix}gcc {assembly} -o {executable}")