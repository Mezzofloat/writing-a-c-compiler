.globl main
main:
	addi sp, sp, -20
	li t3, 2
	li t4, 1
	sub t5, t3, t4
	sw t5, 0(sp)
	lw t4, 0(sp)
	beq x0, t4, .Lbrn.1
	li t4, 1
	beq x0, t4, .Lbrn.1
	li t0, 1
	mv t1, t0
	sw t1, 4(sp)
	beq x0, x0, .Lbrn.3
.Lbrn.1:
	li t0, 0
	mv t1, t0
	sw t1, 4(sp)
.Lbrn.3:
	lw t4, 4(sp)
	bne x0, t4, .Lbrn.4
	li t3, 2
	li t4, 1
	add t5, t3, t4
	sw t5, 8(sp)
	lw t4, 8(sp)
	beq x0, t4, .Lbrn.6
	li t4, 0
	beq x0, t4, .Lbrn.6
	li t0, 1
	mv t1, t0
	sw t1, 12(sp)
	beq x0, x0, .Lbrn.8
.Lbrn.6:
	li t0, 0
	mv t1, t0
	sw t1, 12(sp)
.Lbrn.8:
	lw t4, 12(sp)
	bne x0, t4, .Lbrn.4
	li t0, 0
	mv t1, t0
	sw t1, 16(sp)
	beq x0, x0, .Lbrn.10
.Lbrn.4:
	li t0, 1
	mv t1, t0
	sw t1, 16(sp)
.Lbrn.10:
	lw a0, 16(sp)
	addi sp, sp, 20
	ret
	.section .note.GNU-stack,"",@progbits
