VA=0x8000c8ac file=0xa8ac 27bdffe8 addiu $sp, $sp, -0x18
VA=0x8000c8b0 file=0xa8b0 30e20003 andi $v0, $a3, 3
VA=0x8000c8b4 file=0xa8b4 00804021 move $t0, $a0
VA=0x8000c8b8 file=0xa8b8 10400007 beqz $v0, 0x8000c8d8
VA=0x8000c8bc file=0xa8bc afbf0014 sw $ra, 0x14($sp)
VA=0x8000c8c0 file=0xa8c0 3c048025 lui $a0, 0x8025
VA=0x8000c8c4 file=0xa8c4 2484763c addiu $a0, $a0, 0x763c
VA=0x8000c8c8 file=0xa8c8 0c0860f5 jal 0x802183d4
VA=0x8000c8cc file=0xa8cc 2505000c addiu $a1, $t0, 0xc
VA=0x8000c8d0 file=0xa8d0 08003270 j 0x8000c9c0
VA=0x8000c8d4 file=0xa8d4 2402fff8 addiu $v0, $zero, -8
VA=0x8000c8d8 file=0xa8d8 24a20004 addiu $v0, $a1, 4
VA=0x8000c8dc file=0xa8dc 00e21026 xor $v0, $a3, $v0
VA=0x8000c8e0 file=0xa8e0 3c03f000 lui $v1, 0xf000
VA=0x8000c8e4 file=0xa8e4 00431024 and $v0, $v0, $v1
VA=0x8000c8e8 file=0xa8e8 1040002c beqz $v0, 0x8000c99c
VA=0x8000c8ec file=0xa8ec 3c03e000 lui $v1, 0xe000
VA=0x8000c8f0 file=0xa8f0 00063080 sll $a2, $a2, 2
VA=0x8000c8f4 file=0xa8f4 00a31824 and $v1, $a1, $v1
VA=0x8000c8f8 file=0xa8f8 3c028000 lui $v0, 0x8000
VA=0x8000c8fc file=0xa8fc 1462000a bne $v1, $v0, 0x8000c928
VA=0x8000c900 file=0xa900 00e63021 addu $a2, $a3, $a2
VA=0x8000c904 file=0xa904 8c8200f0 lw $v0, 0xf0($a0)
VA=0x8000c908 file=0xa908 8c8700e8 lw $a3, 0xe8($a0)
VA=0x8000c90c file=0xa90c 30c38000 andi $v1, $a2, 0x8000
VA=0x8000c910 file=0xa910 24440010 addiu $a0, $v0, 0x10
VA=0x8000c914 file=0xa914 00e23821 addu $a3, $a3, $v0
VA=0x8000c918 file=0xa918 1460000a bnez $v1, 0x8000c944
VA=0x8000c91c file=0xa91c ad0400f0 sw $a0, 0xf0($t0)
VA=0x8000c920 file=0xa920 08003254 j 0x8000c950
VA=0x8000c924 file=0xa924 00061c02 srl $v1, $a2, 0x10
VA=0x8000c928 file=0xa928 8c8200f4 lw $v0, 0xf4($a0)
VA=0x8000c92c file=0xa92c 8c8700ec lw $a3, 0xec($a0)
VA=0x8000c930 file=0xa930 30c38000 andi $v1, $a2, 0x8000
VA=0x8000c934 file=0xa934 24440010 addiu $a0, $v0, 0x10
VA=0x8000c938 file=0xa938 00e23821 addu $a3, $a3, $v0
VA=0x8000c93c file=0xa93c 10600003 beqz $v1, 0x8000c94c
VA=0x8000c940 file=0xa940 ad0400f4 sw $a0, 0xf4($t0)
VA=0x8000c944 file=0xa944 3c020001 lui $v0, 1
VA=0x8000c948 file=0xa948 00c23021 addu $a2, $a2, $v0
VA=0x8000c94c file=0xa94c 00061c02 srl $v1, $a2, 0x10
VA=0x8000c950 file=0xa950 3c023c19 lui $v0, 0x3c19
VA=0x8000c954 file=0xa954 00621025 or $v0, $v1, $v0
VA=0x8000c958 file=0xa958 30c6ffff andi $a2, $a2, 0xffff
VA=0x8000c95c file=0xa95c 3c032739 lui $v1, 0x2739
VA=0x8000c960 file=0xa960 ace20000 sw $v0, ($a3)
VA=0x8000c964 file=0xa964 3c020320 lui $v0, 0x320
VA=0x8000c968 file=0xa968 00c33025 or $a2, $a2, $v1
VA=0x8000c96c file=0xa96c 24420008 addiu $v0, $v0, 8
VA=0x8000c970 file=0xa970 ace60004 sw $a2, 4($a3)
VA=0x8000c974 file=0xa974 ace20008 sw $v0, 8($a3)
VA=0x8000c978 file=0xa978 ace0000c sw $zero, 0xc($a3)
VA=0x8000c97c file=0xa97c 14e00007 bnez $a3, 0x8000c99c
VA=0x8000c980 file=0xa980 00003021 move $a2, $zero
VA=0x8000c984 file=0xa984 3c048025 lui $a0, 0x8025
VA=0x8000c988 file=0xa988 24847670 addiu $a0, $a0, 0x7670
VA=0x8000c98c file=0xa98c 0c0860f5 jal 0x802183d4
VA=0x8000c990 file=0xa990 2505000c addiu $a1, $t0, 0xc
VA=0x8000c994 file=0xa994 08003270 j 0x8000c9c0
VA=0x8000c998 file=0xa998 2402fff8 addiu $v0, $zero, -8
VA=0x8000c99c file=0xa99c 8ca30000 lw $v1, ($a1)
VA=0x8000c9a0 file=0xa9a0 00073882 srl $a3, $a3, 2
VA=0x8000c9a4 file=0xa9a4 00e63021 addu $a2, $a3, $a2
VA=0x8000c9a8 file=0xa9a8 3c02fc00 lui $v0, 0xfc00
VA=0x8000c9ac file=0xa9ac 00621024 and $v0, $v1, $v0
VA=0x8000c9b0 file=0xa9b0 7cc6c800 ext $a2, $a2, 0, 0x1a
VA=0x8000c9b4 file=0xa9b4 00c23025 or $a2, $a2, $v0
VA=0x8000c9b8 file=0xa9b8 aca60000 sw $a2, ($a1)
VA=0x8000c9bc file=0xa9bc 00001021 move $v0, $zero
VA=0x8000c9c0 file=0xa9c0 8fbf0014 lw $ra, 0x14($sp)
VA=0x8000c9c4 file=0xa9c4 03e00008 jr $ra
VA=0x8000c9c8 file=0xa9c8 27bd0018 addiu $sp, $sp, 0x18
VA=0x8000c9cc file=0xa9cc 8ca20000 lw $v0, ($a1)
VA=0x8000c9d0 file=0xa9d0 00c03821 move $a3, $a2
VA=0x8000c9d4 file=0xa9d4 0800322b j 0x8000c8ac
VA=0x8000c9d8 file=0xa9d8 7c46c800 ext $a2, $v0, 0, 0x1a
VA=0x8000c9dc file=0xa9dc 00c03821 move $a3, $a2
VA=0x8000c9e0 file=0xa9e0 0800322b j 0x8000c8ac
VA=0x8000c9e4 file=0xa9e4 00003021 move $a2, $zero
VA=0x8000c9e8 file=0xa9e8 27bdffc0 addiu $sp, $sp, -0x40
VA=0x8000c9ec file=0xa9ec afb20020 sw $s2, 0x20($sp)
VA=0x8000c9f0 file=0xa9f0 000790c0 sll $s2, $a3, 3
VA=0x8000c9f4 file=0xa9f4 00073940 sll $a3, $a3, 5
VA=0x8000c9f8 file=0xa9f8 02479021 addu $s2, $s2, $a3
VA=0x8000c9fc file=0xa9fc afbe0038 sw $fp, 0x38($sp)
VA=0x8000ca00 file=0xaa00 afb70034 sw $s7, 0x34($sp)
VA=0x8000ca04 file=0xaa04 afb60030 sw $s6, 0x30($sp)
VA=0x8000ca08 file=0xaa08 afb5002c sw $s5, 0x2c($sp)
VA=0x8000ca0c file=0xaa0c afb40028 sw $s4, 0x28($sp)