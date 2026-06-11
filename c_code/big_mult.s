.globl main
main:
	li t4, -8
	add sp, sp, t4
	li t3, 2
	neg t5, t3
	sw t5, 0(sp)
	li a3, 2
	lw a4, 0(sp)
	li a2, 0
	li t0, 5
	li t1, 2
	add t1, t1, a3
	add t1, t1, a3
	add t1, t1, a3
	add t1, t1, a3
.L2:
	beq x0, a4, end.L2
	add a2, a2, a3
	li t4, -1
	add a4, a4, t4
	beq x0, x0, .L2
end.L2:
	sw a2, 4(sp)
	lw a0, 4(sp)
	addi sp, sp, 8
	ret
	.section .note.GNU-stack,"",@progbits
