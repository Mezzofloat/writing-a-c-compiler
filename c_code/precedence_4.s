.globl main
main:
	addi sp, sp, -8
	li t3, 2
	li t4, 2
	sub a7, t3, t4
	li t0, 1
	sltu t0, a7, t0
	sw t0, 0(sp)
	lw t4, 0(sp)
	bne x0, t4, .Lbrn.1
	li t4, 0
	bne x0, t4, .Lbrn.1
	li t0, 0
	mv t1, t0
	sw t1, 4(sp)
	beq x0, x0, .Lbrn.3
.Lbrn.1:
	li t0, 1
	mv t1, t0
	sw t1, 4(sp)
.Lbrn.3:
	lw a0, 4(sp)
	addi sp, sp, 8
	ret
	.section .note.GNU-stack,"",@progbits
