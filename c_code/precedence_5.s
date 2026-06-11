.globl main
main:
	addi sp, sp, -24
	li t3, 0
	li t4, 0
	sub a7, t3, t4
	li t0, 1
	sltu t0, a7, t0
	sw t0, 0(sp)
	lw t4, 0(sp)
	beq x0, t4, .Lbrn.1
	li t3, 2
	li t4, 1
	add t5, t3, t4
	sw t5, 4(sp)
	lw t3, 4(sp)
	li t4, 1
	sub a7, t3, t4
	li t0, 1
	slt t0, t0, a7
	sw t0, 8(sp)
	li t3, 3
	lw t4, 8(sp)
	sub a7, t3, t4
	li t0, 1
	sltu t0, a7, t0
	sw t0, 12(sp)
	lw t4, 12(sp)
	beq x0, t4, .Lbrn.1
	li t0, 1
	mv t1, t0
	sw t1, 16(sp)
	beq x0, x0, .Lbrn.6
.Lbrn.1:
	li t0, 0
	mv t1, t0
	sw t1, 16(sp)
.Lbrn.6:
	lw t3, 16(sp)
	li t4, 1
	add t5, t3, t4
	sw t5, 20(sp)
	lw a0, 20(sp)
	addi sp, sp, 24
	ret
	.section .note.GNU-stack,"",@progbits
