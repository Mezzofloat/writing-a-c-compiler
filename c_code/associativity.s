.globl main
main:
	addi sp, sp, -8
	li a5, -1
	sw a5, 0(sp)
	li a6, 3
	sw a6, 4(sp)
	lw t0, 0(sp)
	lw t1, 4(sp)
	sub t2, t0, t1
	sw t2, 4(sp)
	lw a0, 4(sp)
	addi sp, sp, 8
	ret
	.section .note.GNU-stack,"",@progbits
