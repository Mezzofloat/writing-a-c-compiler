	.globl main
main:
	pushq	%rbp
	movq	%rsp, %rbp
	movl	$0, -4(%rbp)
	movl	-4(%rbp), %eax
	subq	$4, %rsp
	movl	$0, %r11d
	cmpl	$0, %r11d
	movl	$0, -4(%rbp)
	sete	-4(%rbp)
	movl	-4(%rbp), %eax
	movq	%rbp, %rsp
	popq	%rbp
	ret
	.section .note.GNU-stack,"",@progbits
