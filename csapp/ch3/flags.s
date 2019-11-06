	.file	"flags.c"
	.text
	.globl	flags
	.type	flags, @function
flags:
.LFB0:
	.cfi_startproc
	leal	-123(%rsi,%rdi), %eax

        # 128 - 1 : OF
        pushf
        movb    $0x80, %al
        movb    $0x1, %cl
        subb    %cl, %al
        popf

        # 1 - 128 : CF SF OF
        pushf
        movb    $0x1, %al
        movb    $0x80, %cl
        subb    %cl, %al
        popf

        # CF 
        # unsigned carry : CF ZF
        pushf
        movb    $0xff, %al
        movb    $0x1, %cl
        addb    %cl, %al
        popf

        # unsigned carry (borrow) : CF SF
        pushf
        movb    $0x0, %al
        movb    $0x1, %cl
        subb    %cl, %al
        popf

        # NO carry
        # but overflow: 2 positive get negative : SF OF
        pushf
        movb    $0x7f, %al
        movb    $0x1, %cl
        addb    %cl, %al
        popf

        # NO carry
        # but overflow: 2 negative get positive : OF
        pushf
        movb    $0x80, %al
        movb    $0x1, %cl
        subb    %cl, %al
        popf

        # OF
        # positive overflow : SF OF
        pushf
        movb    $0x40, %al
        movb    $0x40, %cl
        addb    %cl, %al
        popf
        
        # negative overflow, and carry : CF ZF OF 
        pushf
        movb    $0x80, %al
        movb    $0x80, %cl
        addb    %cl, %al
        popf

        # no overflow
        pushf
        movb    $0x40, %al
        movb    $0x1, %cl
        addb    %cl, %al
        popf

        # no overflow : SF
        pushf
        movb    $0x7e, %al
        movb    $0x81, %cl
        addb    %cl, %al
        popf

        # no overflow : SF
        pushf
        movb    $0x80, %al
        movb    $0x1, %cl
        addb    %cl, %al
        popf

        # no overflow, but carry : CF SF
        pushf
        movb    $0xc0, %al
        movb    $0xc0, %cl
        addb    %cl, %al
        popf

	imull	%esi, %edi
	movsbl	%al, %eax
	imull	%edi, %eax
	ret
	.cfi_endproc
.LFE0:
	.size	flags, .-flags
	.ident	"GCC: (Ubuntu 4.8.4-2ubuntu1~14.04.3) 4.8.4"
	.section	.note.GNU-stack,"",@progbits
