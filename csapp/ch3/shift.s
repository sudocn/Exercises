	.file	"shift.c"
	.text
	.globl	shitf_left4_rightn
	.type	shitf_left4_rightn, @function
shitf_left4_rightn:
.LFB0:
	.cfi_startproc
	movq	%rdi, %rax
	salq	$4, %rax
	movl	%esi, %ecx
	sarq	%cl, %rax
	ret
	.cfi_endproc
.LFE0:
	.size	shitf_left4_rightn, .-shitf_left4_rightn
	.ident	"GCC: (Ubuntu 4.8.4-2ubuntu1~14.04.3) 4.8.4"
	.section	.note.GNU-stack,"",@progbits
