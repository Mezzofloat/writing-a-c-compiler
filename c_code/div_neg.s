.globl main
main:
	addi sp, sp, -8
	li t0, 12
	neg t0, t0
	sw t0, 0(sp)
	lw a3, 0(sp)
	li a4, 5
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
	neg a2, a2
.L2:
	sw a2, 4(sp)
	lw a0, 4(sp)
	addi sp, sp, 8
	ret
	.section .note.GNU-stack,"",@progbits
