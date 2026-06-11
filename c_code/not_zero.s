.globl main
main:
	addi sp, sp, -4
	li a1, 0
	slt t0, a1, t0
	sw t0, 0(sp)
	lw a0, 0(sp)
	addi sp, sp, 4
	ret
	.section .note.GNU-stack,"",@progbits
