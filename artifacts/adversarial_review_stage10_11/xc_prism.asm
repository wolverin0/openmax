.text+0xac874 file=0xac8b4 27bdffd8 addiu $sp, $sp, -0x28
.text+0xac878 file=0xac8b8 3c050000 lui $a1, 0 ; $LC18 .rodata.str1.4+0x103fc type=5
.text+0xac87c file=0xac8bc 24a50000 addiu $a1, $a1, 0 ; $LC18 .rodata.str1.4+0x103fc type=6
.text+0xac880 file=0xac8c0 afb2001c sw $s2, 0x1c($sp)
.text+0xac884 file=0xac8c4 00809021 move $s2, $a0
.text+0xac888 file=0xac8c8 00002021 move $a0, $zero
.text+0xac88c file=0xac8cc afb10018 sw $s1, 0x18($sp)
.text+0xac890 file=0xac8d0 afb00014 sw $s0, 0x14($sp)
.text+0xac894 file=0xac8d4 afbf0024 sw $ra, 0x24($sp)
.text+0xac898 file=0xac8d8 afb30020 sw $s3, 0x20($sp)
.text+0xac89c file=0xac8dc 00c08821 move $s1, $a2
.text+0xac8a0 file=0xac8e0 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xac8a4 file=0xac8e4 00e08021 move $s0, $a3
.text+0xac8a8 file=0xac8e8 10400061 beqz $v0, 0xaca30
.text+0xac8ac file=0xac8ec 8fbf0024 lw $ra, 0x24($sp)
.text+0xac8b0 file=0xac8f0 16000013 bnez $s0, 0xac900
.text+0xac8b4 file=0xac8f4 2602fffb addiu $v0, $s0, -5
.text+0xac8b8 file=0xac8f8 0c000000 jal 0 ; ieee80211_chan2mode .text+0x160 type=4
.text+0xac8bc file=0xac8fc 02402021 move $a0, $s2
.text+0xac8c0 file=0xac900 2442fff7 addiu $v0, $v0, -9
.text+0xac8c4 file=0xac904 2c43000b sltiu $v1, $v0, 0xb
.text+0xac8c8 file=0xac908 10600052 beqz $v1, 0xaca14
.text+0xac8cc file=0xac90c 2405000a addiu $a1, $zero, 0xa
.text+0xac8d0 file=0xac910 24030001 addiu $v1, $zero, 1
.text+0xac8d4 file=0xac914 00431004 sllv $v0, $v1, $v0
.text+0xac8d8 file=0xac918 304303bf andi $v1, $v0, 0x3bf
.text+0xac8dc file=0xac91c 1460004f bnez $v1, 0xaca1c
.text+0xac8e0 file=0xac920 30420400 andi $v0, $v0, 0x400
.text+0xac8e4 file=0xac924 2403000a addiu $v1, $zero, 0xa
.text+0xac8e8 file=0xac928 24050028 addiu $a1, $zero, 0x28
.text+0xac8ec file=0xac92c 24100050 addiu $s0, $zero, 0x50
.text+0xac8f0 file=0xac930 0062280a movz $a1, $v1, $v0
.text+0xac8f4 file=0xac934 24030014 addiu $v1, $zero, 0x14
.text+0xac8f8 file=0xac938 0802b289 j 0xaca24 ;  .text+0x0 type=4
.text+0xac8fc file=0xac93c 0062800a movz $s0, $v1, $v0
.text+0xac900 file=0xac940 2c42009c sltiu $v0, $v0, 0x9c
.text+0xac904 file=0xac944 14400006 bnez $v0, 0xac920
.text+0xac908 file=0xac948 00000000 nop 
.text+0xac90c file=0xac94c 24100001 addiu $s0, $zero, 1
.text+0xac910 file=0xac950 24110001 addiu $s1, $zero, 1
.text+0xac914 file=0xac954 24120001 addiu $s2, $zero, 1
.text+0xac918 file=0xac958 0802b267 j 0xac99c ;  .text+0x0 type=4
.text+0xac91c file=0xac95c 00009821 move $s3, $zero
.text+0xac920 file=0xac960 00109042 srl $s2, $s0, 1
.text+0xac924 file=0xac964 02519821 addu $s3, $s2, $s1
.text+0xac928 file=0xac968 02329023 subu $s2, $s1, $s2
.text+0xac92c file=0xac96c 2631f830 addiu $s1, $s1, -0x7d0
.text+0xac930 file=0xac970 2e311069 sltiu $s1, $s1, 0x1069
.text+0xac934 file=0xac974 1220fff5 beqz $s1, 0xac90c
.text+0xac938 file=0xac978 02603021 move $a2, $s3
.text+0xac93c file=0xac97c 02402821 move $a1, $s2
.text+0xac940 file=0xac980 02003821 move $a3, $s0
.text+0xac944 file=0xac984 0c02afac jal 0xabeb0 ;  .text+0x0 type=4
.text+0xac948 file=0xac988 24040001 addiu $a0, $zero, 1
.text+0xac94c file=0xac98c 00408821 move $s1, $v0
.text+0xac950 file=0xac990 24040002 addiu $a0, $zero, 2
.text+0xac954 file=0xac994 02402821 move $a1, $s2
.text+0xac958 file=0xac998 02603021 move $a2, $s3
.text+0xac95c file=0xac99c 0c02afac jal 0xabeb0 ;  .text+0x0 type=4
.text+0xac960 file=0xac9a0 02003821 move $a3, $s0
.text+0xac964 file=0xac9a4 12200004 beqz $s1, 0xac978
.text+0xac968 file=0xac9a8 00000000 nop 
.text+0xac96c file=0xac9ac 8e330014 lw $s3, 0x14($s1)
.text+0xac970 file=0xac9b0 0802b260 j 0xac980 ;  .text+0x0 type=4
.text+0xac974 file=0xac9b4 8e320018 lw $s2, 0x18($s1)
.text+0xac978 file=0xac9b8 24120001 addiu $s2, $zero, 1
.text+0xac97c file=0xac9bc 00009821 move $s3, $zero
.text+0xac980 file=0xac9c0 10400004 beqz $v0, 0xac994
.text+0xac984 file=0xac9c4 00000000 nop 
.text+0xac988 file=0xac9c8 8c51001c lw $s1, 0x1c($v0)
.text+0xac98c file=0xac9cc 0802b267 j 0xac99c ;  .text+0x0 type=4
.text+0xac990 file=0xac9d0 8c500020 lw $s0, 0x20($v0)
.text+0xac994 file=0xac9d4 24100001 addiu $s0, $zero, 1
.text+0xac998 file=0xac9d8 24110001 addiu $s1, $zero, 1
.text+0xac99c file=0xac9dc 2404000f addiu $a0, $zero, 0xf
.text+0xac9a0 file=0xac9e0 0c000000 jal 0 ; gpio_line_config SHN_UNDEF+0x0 type=4
.text+0xac9a4 file=0xac9e4 24050001 addiu $a1, $zero, 1
.text+0xac9a8 file=0xac9e8 02602821 move $a1, $s3
.text+0xac9ac file=0xac9ec 0c000000 jal 0 ; gpio_line_set SHN_UNDEF+0x0 type=4
.text+0xac9b0 file=0xac9f0 2404000f addiu $a0, $zero, 0xf
.text+0xac9b4 file=0xac9f4 24040010 addiu $a0, $zero, 0x10
.text+0xac9b8 file=0xac9f8 0c000000 jal 0 ; gpio_line_config SHN_UNDEF+0x0 type=4
.text+0xac9bc file=0xac9fc 24050001 addiu $a1, $zero, 1
.text+0xac9c0 file=0xaca00 02402821 move $a1, $s2
.text+0xac9c4 file=0xaca04 0c000000 jal 0 ; gpio_line_set SHN_UNDEF+0x0 type=4
.text+0xac9c8 file=0xaca08 24040010 addiu $a0, $zero, 0x10
.text+0xac9cc file=0xaca0c 2404000d addiu $a0, $zero, 0xd
.text+0xac9d0 file=0xaca10 0c000000 jal 0 ; gpio_line_config SHN_UNDEF+0x0 type=4
.text+0xac9d4 file=0xaca14 24050001 addiu $a1, $zero, 1
.text+0xac9d8 file=0xaca18 02202821 move $a1, $s1
.text+0xac9dc file=0xaca1c 0c000000 jal 0 ; gpio_line_set SHN_UNDEF+0x0 type=4
.text+0xac9e0 file=0xaca20 2404000d addiu $a0, $zero, 0xd
.text+0xac9e4 file=0xaca24 2404000e addiu $a0, $zero, 0xe
.text+0xac9e8 file=0xaca28 0c000000 jal 0 ; gpio_line_config SHN_UNDEF+0x0 type=4
.text+0xac9ec file=0xaca2c 24050001 addiu $a1, $zero, 1
.text+0xac9f0 file=0xaca30 8fbf0024 lw $ra, 0x24($sp)
.text+0xac9f4 file=0xaca34 8fb30020 lw $s3, 0x20($sp)
.text+0xac9f8 file=0xaca38 8fb2001c lw $s2, 0x1c($sp)
.text+0xac9fc file=0xaca3c 8fb10018 lw $s1, 0x18($sp)
.text+0xaca00 file=0xaca40 02002821 move $a1, $s0
.text+0xaca04 file=0xaca44 8fb00014 lw $s0, 0x14($sp)
.text+0xaca08 file=0xaca48 2404000e addiu $a0, $zero, 0xe
.text+0xaca0c file=0xaca4c 08000000 j 0 ; gpio_line_set SHN_UNDEF+0x0 type=4
.text+0xaca10 file=0xaca50 27bd0028 addiu $sp, $sp, 0x28
.text+0xaca14 file=0xaca54 0802b289 j 0xaca24 ;  .text+0x0 type=4
.text+0xaca18 file=0xaca58 24100014 addiu $s0, $zero, 0x14
.text+0xaca1c file=0xaca5c 24050014 addiu $a1, $zero, 0x14
.text+0xaca20 file=0xaca60 24100028 addiu $s0, $zero, 0x28
.text+0xaca24 file=0xaca64 00b19821 addu $s3, $a1, $s1
.text+0xaca28 file=0xaca68 0802b24b j 0xac92c ;  .text+0x0 type=4
.text+0xaca2c file=0xaca6c 02259023 subu $s2, $s1, $a1
.text+0xaca30 file=0xaca70 8fb30020 lw $s3, 0x20($sp)
.text+0xaca34 file=0xaca74 8fb2001c lw $s2, 0x1c($sp)
.text+0xaca38 file=0xaca78 8fb10018 lw $s1, 0x18($sp)
.text+0xaca3c file=0xaca7c 8fb00014 lw $s0, 0x14($sp)
.text+0xaca40 file=0xaca80 03e00008 jr $ra
.text+0xaca44 file=0xaca84 27bd0028 addiu $sp, $sp, 0x28
.text+0xaca48 file=0xaca88 27bdffd0 addiu $sp, $sp, -0x30
.text+0xaca4c file=0xaca8c afbf002c sw $ra, 0x2c($sp)
.text+0xaca50 file=0xaca90 afb60028 sw $s6, 0x28($sp)
.text+0xaca54 file=0xaca94 afb50024 sw $s5, 0x24($sp)
.text+0xaca58 file=0xaca98 afb40020 sw $s4, 0x20($sp)
.text+0xaca5c file=0xaca9c 00a0a821 move $s5, $a1
.text+0xaca60 file=0xacaa0 afb3001c sw $s3, 0x1c($sp)
.text+0xaca64 file=0xacaa4 afb20018 sw $s2, 0x18($sp)
.text+0xaca68 file=0xacaa8 00e09821 move $s3, $a3
.text+0xaca6c file=0xacaac afb10014 sw $s1, 0x14($sp)
.text+0xaca70 file=0xacab0 afb00010 sw $s0, 0x10($sp)
.text+0xaca74 file=0xacab4 00c08821 move $s1, $a2
.text+0xaca78 file=0xacab8 93b4004b lbu $s4, 0x4b($sp)
.text+0xaca7c file=0xacabc 0c000000 jal 0 ; wmi_unified_get_scn .text+0xc3598 type=4
.text+0xaca80 file=0xacac0 93b6004f lbu $s6, 0x4f($sp)
.text+0xaca84 file=0xacac4 00409021 move $s2, $v0
.text+0xaca88 file=0xacac8 8fa20044 lw $v0, 0x44($sp)
.text+0xaca8c file=0xacacc 02202021 move $a0, $s1
.text+0xaca90 file=0xacad0 8c5000c8 lw $s0, 0xc8($v0)
.text+0xaca94 file=0xacad4 ae150018 sw $s5, 0x18($s0)
.text+0xaca98 file=0xacad8 0c000000 jal 0 ; ieee80211_chan2mode .text+0x160 type=4
.text+0xaca9c file=0xacadc ae130000 sw $s3, ($s0)
.text+0xacaa0 file=0xacae0 00022080 sll $a0, $v0, 2
.text+0xacaa4 file=0xacae4 00401821 move $v1, $v0
.text+0xacaa8 file=0xacae8 3c020001 lui $v0, 1 ;  .rodata+0x0 type=5
.text+0xacaac file=0xacaec 2442cd4c addiu $v0, $v0, -0x32b4 ;  .rodata+0x0 type=6
.text+0xacab0 file=0xacaf0 8e05000c lw $a1, 0xc($s0)