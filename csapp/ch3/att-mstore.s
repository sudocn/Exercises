	.file	"mstore.c"
	.text
	.globl	multstore
	.type	multstore, @function
multstore:
.LFB0:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	movq	%rdx, %rbx
	call	mult2
        movabsq $0x0011223344556677, %rax
        movb    $-1, %al
        movw    $-1, %ax
        movl    $-1, %eax
        cltq

        movabsq $0x0011223344556677, %rax
        movq    $-1, %rax

        #movb    $0xF, (%ebx)
        #movl    %rax, (%rsp)
        #movw    (%rax), 4(%rsp)
        #movb    %al, %sl
        #movq    %rax, $0x123
        #movl    %eax, %rdx
        #movb    %si, 8(%rbp)

	# problem 3.6, p.228
        movq    $0xbaadbeef55aa, %rdx
	movq	$17, %rbx
	
        leaq    9(%rdx), %rax
	leaq	(%rdx,%rbx), %rax
	leaq	(%rdx,%rbx,4), %rax
	leaq	2(%rbx,%rbx,8), %rax
	leaq	0xE(,%rdx,4), %rax
	leaq	6(%rbx,%rdx,8), %rax

        xorq    %rcx, %rcx
        movq    $0, %rcx
        subq    %rcx, %rcx
        xorl    %ecx, %ecx
        movl    $0, %ecx

	movq	%rax, (%rbx)
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE0:
	.size	multstore, .-multstore
	.ident	"GCC: (Ubuntu 4.8.4-2ubuntu1~14.04.3) 4.8.4"
	.section	.note.GNU-stack,"",@progbits
