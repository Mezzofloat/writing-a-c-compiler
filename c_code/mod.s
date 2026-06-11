.globl main
main:
	addi sp, sp, -4
	li a3, 4
	li a4, 2
	li a2, 0
	li t6, 0
	bge a3, x0, .L1
	neg a3, a3
	li t6, 1
.L1:
	blt a3, a4, end.L1
	sub a3, a3, a4
	li t4, 1
	add a2, a2, t4
	beq x0, x0, .L1
end.L1:
	beq x0, t6, .L2
	neg a3, a3
.L2:
	sw a3, 0(sp)
	lw a0, 0(sp)
	addi sp, sp, 4
	ret
	.section .note.GNU-stack,"",@progbits
