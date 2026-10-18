.text+0x65790 file=0x657d0 3c0305e4 lui $v1, 0x5e4
.text+0x65794 file=0x657d4 00c52821 addu $a1, $a2, $a1
.text+0x65798 file=0x657d8 24662455 addiu $a2, $v1, 0x2455
.text+0x6579c file=0x657dc 00a62821 addu $a1, $a1, $a2
.text+0x657a0 file=0x657e0 3c150000 lui $s5, 0 ;  .data+0x0 type=5
.text+0x657a4 file=0x657e4 aea50f24 sw $a1, 0xf24($s5) ;  .data+0x0 type=6
.text+0x657a8 file=0x657e8 3c140000 lui $s4, 0 ;  .bss+0x0 type=5
.text+0x657ac file=0x657ec 26947a10 addiu $s4, $s4, 0x7a10 ;  .bss+0x0 type=6
.text+0x657b0 file=0x657f0 2466245e addiu $a2, $v1, 0x245e
.text+0x657b4 file=0x657f4 00003810 mfhi $a3
.text+0x657b8 file=0x657f8 00e21023 subu $v0, $a3, $v0
.text+0x657bc file=0x657fc 000228c0 sll $a1, $v0, 3
.text+0x657c0 file=0x65800 00023940 sll $a3, $v0, 5
.text+0x657c4 file=0x65804 00e52823 subu $a1, $a3, $a1
.text+0x657c8 file=0x65808 00a21021 addu $v0, $a1, $v0
.text+0x657cc file=0x6580c 02821021 addu $v0, $s4, $v0
.text+0x657d0 file=0x65810 90450008 lbu $a1, 8($v0)
.text+0x657d4 file=0x65814 30a500fe andi $a1, $a1, 0xfe
.text+0x657d8 file=0x65818 10860004 beq $a0, $a2, 0x657ec
.text+0x657dc file=0x6581c a0450008 sb $a1, 8($v0)
.text+0x657e0 file=0x65820 ae4046a4 sw $zero, 0x46a4($s2) ;  .bss+0x0 type=6
.text+0x657e4 file=0x65824 08019616 j 0x65858 ;  .text+0x0 type=4
.text+0x657e8 file=0x65828 00001021 move $v0, $zero
.text+0x657ec file=0x6582c 24100004 addiu $s0, $zero, 4
.text+0x657f0 file=0x65830 24130001 addiu $s3, $zero, 1
.text+0x657f4 file=0x65834 08019608 j 0x65820 ;  .text+0x0 type=4
.text+0x657f8 file=0x65838 24762c23 addiu $s6, $v1, 0x2c23
.text+0x657fc file=0x6583c 0c000000 jal 0 ; memcmp SHN_UNDEF+0x0 type=4
.text+0x65800 file=0x65840 00000000 nop 
.text+0x65804 file=0x65844 1440fff6 bnez $v0, 0x657e0
.text+0x65808 file=0x65848 00000000 nop 
.text+0x6580c file=0x6584c 1613000a bne $s0, $s3, 0x65838
.text+0x65810 file=0x65850 02202021 move $a0, $s1
.text+0x65814 file=0x65854 0c018f33 jal 0x63ccc ;  .text+0x0 type=4
.text+0x65818 file=0x65858 aeb60f24 sw $s6, 0xf24($s5) ;  .data+0x0 type=6
.text+0x6581c file=0x6585c 8fb00010 lw $s0, 0x10($sp)
.text+0x65820 file=0x65860 001020c0 sll $a0, $s0, 3
.text+0x65824 file=0x65864 00101140 sll $v0, $s0, 5
.text+0x65828 file=0x65868 00442023 subu $a0, $v0, $a0
.text+0x6582c file=0x6586c 00902021 addu $a0, $a0, $s0
.text+0x65830 file=0x65870 2484ffe7 addiu $a0, $a0, -0x19
.text+0x65834 file=0x65874 02842021 addu $a0, $s4, $a0
.text+0x65838 file=0x65878 2491ffe7 addiu $s1, $a0, -0x19
.text+0x6583c file=0x6587c 2610ffff addiu $s0, $s0, -1
.text+0x65840 file=0x65880 02202821 move $a1, $s1
.text+0x65844 file=0x65884 24060019 addiu $a2, $zero, 0x19
.text+0x65848 file=0x65888 1600ffec bnez $s0, 0x657fc
.text+0x6584c file=0x6588c afb00010 sw $s0, 0x10($sp)
.text+0x65850 file=0x65890 080195f9 j 0x657e4 ;  .text+0x0 type=4
.text+0x65854 file=0x65894 ae4046a4 sw $zero, 0x46a4($s2) ;  .bss+0x0 type=6
.text+0x65858 file=0x65898 8fbf0034 lw $ra, 0x34($sp)
.text+0x6585c file=0x6589c 8fb60030 lw $s6, 0x30($sp)
.text+0x65860 file=0x658a0 8fb5002c lw $s5, 0x2c($sp)
.text+0x65864 file=0x658a4 8fb40028 lw $s4, 0x28($sp)
.text+0x65868 file=0x658a8 8fb30024 lw $s3, 0x24($sp)
.text+0x6586c file=0x658ac 8fb20020 lw $s2, 0x20($sp)
.text+0x65870 file=0x658b0 8fb1001c lw $s1, 0x1c($sp)
.text+0x65874 file=0x658b4 8fb00018 lw $s0, 0x18($sp)
.text+0x65878 file=0x658b8 03e00008 jr $ra
.text+0x6587c file=0x658bc 27bd0038 addiu $sp, $sp, 0x38
.text+0x65880 file=0x658c0 27bdffe0 addiu $sp, $sp, -0x20
.text+0x65884 file=0x658c4 afb10018 sw $s1, 0x18($sp)
.text+0x65888 file=0x658c8 afb00014 sw $s0, 0x14($sp)
.text+0x6588c file=0x658cc afbf001c sw $ra, 0x1c($sp)
.text+0x65890 file=0x658d0 00808021 move $s0, $a0
.text+0x65894 file=0x658d4 0c000000 jal 0 ; ath_flash_spi_down SHN_UNDEF+0x0 type=4
.text+0x65898 file=0x658d8 00a08821 move $s1, $a1
.text+0x6589c file=0x658dc 41636000 di $v1
.text+0x658a0 file=0x658e0 30630001 andi $v1, $v1, 1
.text+0x658a4 file=0x658e4 000000c0 ehb 
.text+0x658a8 file=0x658e8 3c02a000 lui $v0, 0xa000
.text+0x658ac file=0x658ec 7e25e000 ext $a1, $s1, 0, 0x1d
.text+0x658b0 file=0x658f0 00a22825 or $a1, $a1, $v0
.text+0x658b4 file=0x658f4 88a20000 lwl $v0, ($a1)
.text+0x658b8 file=0x658f8 98a20003 lwr $v0, 3($a1)
.text+0x658bc file=0x658fc aa020000 swl $v0, ($s0)
.text+0x658c0 file=0x65900 ba020003 swr $v0, 3($s0)
.text+0x658c4 file=0x65904 10600002 beqz $v1, 0x658d0
.text+0x658c8 file=0x65908 41606000 di 
.text+0x658cc file=0x6590c 41606020 ei 
.text+0x658d0 file=0x65910 000000c0 ehb 
.text+0x658d4 file=0x65914 8fbf001c lw $ra, 0x1c($sp)
.text+0x658d8 file=0x65918 8fb10018 lw $s1, 0x18($sp)
.text+0x658dc file=0x6591c 8fb00014 lw $s0, 0x14($sp)
.text+0x658e0 file=0x65920 08000000 j 0 ; ath_flash_spi_up SHN_UNDEF+0x0 type=4
.text+0x658e4 file=0x65924 27bd0020 addiu $sp, $sp, 0x20
.text+0x658e8 file=0x65928 27bdffe0 addiu $sp, $sp, -0x20
.text+0x658ec file=0x6592c 3c051806 lui $a1, 0x1806
.text+0x658f0 file=0x65930 27a40010 addiu $a0, $sp, 0x10
.text+0x658f4 file=0x65934 24a50090 addiu $a1, $a1, 0x90
.text+0x658f8 file=0x65938 afbf001c sw $ra, 0x1c($sp)
.text+0x658fc file=0x6593c 0c019620 jal 0x65880 ;  .text+0x0 type=4
.text+0x65900 file=0x65940 afa00010 sw $zero, 0x10($sp)
.text+0x65904 file=0x65944 8fbf001c lw $ra, 0x1c($sp)
.text+0x65908 file=0x65948 97a20012 lhu $v0, 0x12($sp)
.text+0x6590c file=0x6594c 03e00008 jr $ra
.text+0x65910 file=0x65950 27bd0020 addiu $sp, $sp, 0x20
.text+0x65914 file=0x65954 27bdffc8 addiu $sp, $sp, -0x38
.text+0x65918 file=0x65958 afbf0034 sw $ra, 0x34($sp)
.text+0x6591c file=0x6595c afb50030 sw $s5, 0x30($sp)
.text+0x65920 file=0x65960 afb4002c sw $s4, 0x2c($sp)
.text+0x65924 file=0x65964 afb30028 sw $s3, 0x28($sp)
.text+0x65928 file=0x65968 afb20024 sw $s2, 0x24($sp)
.text+0x6592c file=0x6596c afb10020 sw $s1, 0x20($sp)
.text+0x65930 file=0x65970 0c01963a jal 0x658e8 ;  .text+0x0 type=4
.text+0x65934 file=0x65974 afb0001c sw $s0, 0x1c($sp)
.text+0x65938 file=0x65978 3043eff0 andi $v1, $v0, 0xeff0
.text+0x6593c file=0x6597c 24040110 addiu $a0, $zero, 0x110
.text+0x65940 file=0x65980 1464007f bne $v1, $a0, 0x65b40
.text+0x65944 file=0x65984 3044fff0 andi $a0, $v0, 0xfff0
.text+0x65948 file=0x65988 080196d5 j 0x65b54 ;  .text+0x0 type=4
.text+0x6594c file=0x6598c 3c05b810 lui $a1, 0xb810
.text+0x65950 file=0x65990 3042dff0 andi $v0, $v0, 0xdff0
.text+0x65954 file=0x65994 1445008c bne $v0, $a1, 0x65b88
.text+0x65958 file=0x65998 24021130 addiu $v0, $zero, 0x1130
.text+0x6595c file=0x6599c 080196db j 0x65b6c ;  .text+0x0 type=4
.text+0x65960 file=0x659a0 3c100000 lui $s0, 0 ;  .bss+0x0 type=5
.text+0x65964 file=0x659a4 8c450100 lw $a1, 0x100($v0)
.text+0x65968 file=0x659a8 10a00009 beqz $a1, 0x65990
.text+0x6596c file=0x659ac 27a40010 addiu $a0, $sp, 0x10
.text+0x65970 file=0x659b0 24a54020 addiu $a1, $a1, 0x4020
.text+0x65974 file=0x659b4 0c019620 jal 0x65880 ;  .text+0x0 type=4
.text+0x65978 file=0x659b8 afa00010 sw $zero, 0x10($sp)
.text+0x6597c file=0x659bc 8fa20010 lw $v0, 0x10($sp)
.text+0x65980 file=0x659c0 3c03001c lui $v1, 0x1c
.text+0x65984 file=0x659c4 246304ff addiu $v1, $v1, 0x4ff
.text+0x65988 file=0x659c8 144300b5 bne $v0, $v1, 0x65c60
.text+0x6598c file=0x659cc 00000000 nop 
.text+0x65990 file=0x659d0 0c01963a jal 0x658e8 ;  .text+0x0 type=4
.text+0x65994 file=0x659d4 00000000 nop 
.text+0x65998 file=0x659d8 08019719 j 0x65c64 ;  .text+0x0 type=4
.text+0x6599c file=0x659dc 8fbf0034 lw $ra, 0x34($sp)
.text+0x659a0 file=0x659e0 240200c0 addiu $v0, $zero, 0xc0
.text+0x659a4 file=0x659e4 108200a6 beq $a0, $v0, 0x65c40
.text+0x659a8 file=0x659e8 24020100 addiu $v0, $zero, 0x100
.text+0x659ac file=0x659ec 14620081 bne $v1, $v0, 0x65bb4