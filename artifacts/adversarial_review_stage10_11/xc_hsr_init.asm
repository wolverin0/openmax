.text+0x8cb00 file=0x8cb40 14400003 bnez $v0, 0x8cb10
.text+0x8cb04 file=0x8cb44 3c110000 lui $s1, 0 ;  .data+0x0 type=5
.text+0x8cb08 file=0x8cb48 0c017763 jal 0x5dd8c ;  .text+0x0 type=4
.text+0x8cb0c file=0x8cb4c 00000000 nop 
.text+0x8cb10 file=0x8cb50 26240d7c addiu $a0, $s1, 0xd7c ;  .data+0x0 type=6
.text+0x8cb14 file=0x8cb54 0c019534 jal 0x654d0 ;  .text+0x0 type=4
.text+0x8cb18 file=0x8cb58 00002821 move $a1, $zero
.text+0x8cb1c file=0x8cb5c 8e0349ac lw $v1, 0x49ac($s0) ;  .bss+0x0 type=6
.text+0x8cb20 file=0x8cb60 3042f0f0 andi $v0, $v0, 0xf0f0
.text+0x8cb24 file=0x8cb64 00028103 sra $s0, $v0, 4
.text+0x8cb28 file=0x8cb68 14600003 bnez $v1, 0x8cb38
.text+0x8cb2c file=0x8cb6c 3a100e05 xori $s0, $s0, 0xe05
.text+0x8cb30 file=0x8cb70 0c0177cf jal 0x5df3c ;  .text+0x0 type=4
.text+0x8cb34 file=0x8cb74 00000000 nop 
.text+0x8cb38 file=0x8cb78 8e6249a4 lw $v0, 0x49a4($s3) ;  .bss+0x0 type=6
.text+0x8cb3c file=0x8cb7c 14400004 bnez $v0, 0x8cb50
.text+0x8cb40 file=0x8cb80 26240d7c addiu $a0, $s1, 0xd7c ;  .data+0x0 type=6
.text+0x8cb44 file=0x8cb84 0c017763 jal 0x5dd8c ;  .text+0x0 type=4
.text+0x8cb48 file=0x8cb88 00000000 nop 
.text+0x8cb4c file=0x8cb8c 26240d7c addiu $a0, $s1, 0xd7c ;  .data+0x0 type=6
.text+0x8cb50 file=0x8cb90 0c019534 jal 0x654d0 ;  .text+0x0 type=4
.text+0x8cb54 file=0x8cb94 00002821 move $a1, $zero
.text+0x8cb58 file=0x8cb98 30420f0f andi $v0, $v0, 0xf0f
.text+0x8cb5c file=0x8cb9c 00021100 sll $v0, $v0, 4
.text+0x8cb60 file=0x8cba0 38422020 xori $v0, $v0, 0x2020
.text+0x8cb64 file=0x8cba4 00508021 addu $s0, $v0, $s0
.text+0x8cb68 file=0x8cba8 1600ffc3 bnez $s0, 0x8ca78
.text+0x8cb6c file=0x8cbac 00003021 move $a2, $zero
.text+0x8cb70 file=0x8cbb0 08023354 j 0x8cd50 ;  .text+0x0 type=4
.text+0x8cb74 file=0x8cbb4 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cb78 file=0x8cbb8 00402821 move $a1, $v0
.text+0x8cb7c file=0x8cbbc 00002021 move $a0, $zero
.text+0x8cb80 file=0x8cbc0 080232e6 j 0x8cb98 ;  .text+0x0 type=4
.text+0x8cb84 file=0x8cbc4 00001821 move $v1, $zero
.text+0x8cb88 file=0x8cbc8 94a70000 lhu $a3, ($a1)
.text+0x8cb8c file=0x8cbcc 24a50002 addiu $a1, $a1, 2
.text+0x8cb90 file=0x8cbd0 00671826 xor $v1, $v1, $a3
.text+0x8cb94 file=0x8cbd4 3084ffff andi $a0, $a0, 0xffff
.text+0x8cb98 file=0x8cbd8 1486fffb bne $a0, $a2, 0x8cb88
.text+0x8cb9c file=0x8cbdc 24840001 addiu $a0, $a0, 1
.text+0x8cba0 file=0x8cbe0 3404ffff ori $a0, $zero, 0xffff
.text+0x8cba4 file=0x8cbe4 146400a4 bne $v1, $a0, 0x8ce38
.text+0x8cba8 file=0x8cbe8 02002021 move $a0, $s0
.text+0x8cbac file=0x8cbec 080233af j 0x8cebc ;  .text+0x0 type=4
.text+0x8cbb0 file=0x8cbf0 9051000c lbu $s1, 0xc($v0)
.text+0x8cbb4 file=0x8cbf4 94a80000 lhu $t0, ($a1)
.text+0x8cbb8 file=0x8cbf8 24a50002 addiu $a1, $a1, 2
.text+0x8cbbc file=0x8cbfc 00681826 xor $v1, $v1, $t0
.text+0x8cbc0 file=0x8cc00 3084ffff andi $a0, $a0, 0xffff
.text+0x8cbc4 file=0x8cc04 1486fffb bne $a0, $a2, 0x8cbb4
.text+0x8cbc8 file=0x8cc08 24840001 addiu $a0, $a0, 1
.text+0x8cbcc file=0x8cc0c 3404ffff ori $a0, $zero, 0xffff
.text+0x8cbd0 file=0x8cc10 146400a3 bne $v1, $a0, 0x8ce60
.text+0x8cbd4 file=0x8cc14 00000000 nop 
.text+0x8cbd8 file=0x8cc18 080233ad j 0x8ceb4 ;  .text+0x0 type=4
.text+0x8cbdc file=0x8cc1c 00e01021 move $v0, $a3
.text+0x8cbe0 file=0x8cc20 94a90000 lhu $t1, ($a1)
.text+0x8cbe4 file=0x8cc24 24a50002 addiu $a1, $a1, 2
.text+0x8cbe8 file=0x8cc28 00691826 xor $v1, $v1, $t1
.text+0x8cbec file=0x8cc2c 3084ffff andi $a0, $a0, 0xffff
.text+0x8cbf0 file=0x8cc30 1488fffb bne $a0, $t0, 0x8cbe0
.text+0x8cbf4 file=0x8cc34 24840001 addiu $a0, $a0, 1
.text+0x8cbf8 file=0x8cc38 3404ffff ori $a0, $zero, 0xffff
.text+0x8cbfc file=0x8cc3c 146400a2 bne $v1, $a0, 0x8ce88
.text+0x8cc00 file=0x8cc40 00000000 nop 
.text+0x8cc04 file=0x8cc44 080233ad j 0x8ceb4 ;  .text+0x0 type=4
.text+0x8cc08 file=0x8cc48 00c01021 move $v0, $a2
.text+0x8cc0c file=0x8cc4c 2403005a addiu $v1, $zero, 0x5a
.text+0x8cc10 file=0x8cc50 1483000c bne $a0, $v1, 0x8cc44
.text+0x8cc14 file=0x8cc54 93a30011 lbu $v1, 0x11($sp)
.text+0x8cc18 file=0x8cc58 93a80012 lbu $t0, 0x12($sp)
.text+0x8cc1c file=0x8cc5c 9203010e lbu $v1, 0x10e($s0)
.text+0x8cc20 file=0x8cc60 15030008 bne $t0, $v1, 0x8cc44
.text+0x8cc24 file=0x8cc64 93a30011 lbu $v1, 0x11($sp)
.text+0x8cc28 file=0x8cc68 93a80010 lbu $t0, 0x10($sp)
.text+0x8cc2c file=0x8cc6c 9203010c lbu $v1, 0x10c($s0)
.text+0x8cc30 file=0x8cc70 15030004 bne $t0, $v1, 0x8cc44
.text+0x8cc34 file=0x8cc74 93a30011 lbu $v1, 0x11($sp)
.text+0x8cc38 file=0x8cc78 9208010d lbu $t0, 0x10d($s0)
.text+0x8cc3c file=0x8cc7c 1103009a beq $t0, $v1, 0x8cea8
.text+0x8cc40 file=0x8cc80 00000000 nop 
.text+0x8cc44 file=0x8cc84 9207008d lbu $a3, 0x8d($s0)
.text+0x8cc48 file=0x8cc88 14e3000e bne $a3, $v1, 0x8cc84
.text+0x8cc4c file=0x8cc8c 00053827 nor $a3, $zero, $a1
.text+0x8cc50 file=0x8cc90 30e700ff andi $a3, $a3, 0xff
.text+0x8cc54 file=0x8cc94 1487000b bne $a0, $a3, 0x8cc84
.text+0x8cc58 file=0x8cc98 00044027 nor $t0, $zero, $a0
.text+0x8cc5c file=0x8cc9c 310800ff andi $t0, $t0, 0xff
.text+0x8cc60 file=0x8cca0 240700a5 addiu $a3, $zero, 0xa5
.text+0x8cc64 file=0x8cca4 15070007 bne $t0, $a3, 0x8cc84
.text+0x8cc68 file=0x8cca8 93a80010 lbu $t0, 0x10($sp)
.text+0x8cc6c file=0x8ccac 9207008c lbu $a3, 0x8c($s0)
.text+0x8cc70 file=0x8ccb0 15070004 bne $t0, $a3, 0x8cc84
.text+0x8cc74 file=0x8ccb4 93a80012 lbu $t0, 0x12($sp)
.text+0x8cc78 file=0x8ccb8 9207008e lbu $a3, 0x8e($s0)
.text+0x8cc7c file=0x8ccbc 1107008c beq $t0, $a3, 0x8ceb0
.text+0x8cc80 file=0x8ccc0 00000000 nop 
.text+0x8cc84 file=0x8ccc4 9206020d lbu $a2, 0x20d($s0)
.text+0x8cc88 file=0x8ccc8 14c3000c bne $a2, $v1, 0x8ccbc
.text+0x8cc8c file=0x8cccc 93a60010 lbu $a2, 0x10($sp)
.text+0x8cc90 file=0x8ccd0 9203020c lbu $v1, 0x20c($s0)
.text+0x8cc94 file=0x8ccd4 14c30009 bne $a2, $v1, 0x8ccbc
.text+0x8cc98 file=0x8ccd8 240300ff addiu $v1, $zero, 0xff
.text+0x8cc9c file=0x8ccdc 00651823 subu $v1, $v1, $a1
.text+0x8cca0 file=0x8cce0 14830006 bne $a0, $v1, 0x8ccbc
.text+0x8cca4 file=0x8cce4 240300a5 addiu $v1, $zero, 0xa5
.text+0x8cca8 file=0x8cce8 14a30004 bne $a1, $v1, 0x8ccbc
.text+0x8ccac file=0x8ccec 93a30012 lbu $v1, 0x12($sp)
.text+0x8ccb0 file=0x8ccf0 9204020e lbu $a0, 0x20e($s0)
.text+0x8ccb4 file=0x8ccf4 10830080 beq $a0, $v1, 0x8ceb8
.text+0x8ccb8 file=0x8ccf8 02002021 move $a0, $s0
.text+0x8ccbc file=0x8ccfc 2402ffff addiu $v0, $zero, -1
.text+0x8ccc0 file=0x8cd00 ae02020c sw $v0, 0x20c($s0)
.text+0x8ccc4 file=0x8cd04 0c000000 jal 0 ; kfree SHN_UNDEF+0x0 type=4
.text+0x8ccc8 file=0x8cd08 02002021 move $a0, $s0
.text+0x8cccc file=0x8cd0c 08023354 j 0x8cd50 ;  .text+0x0 type=4
.text+0x8ccd0 file=0x8cd10 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8ccd4 file=0x8cd14 1473001e bne $v1, $s3, 0x8cd50
.text+0x8ccd8 file=0x8cd18 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8ccdc file=0x8cd1c 93a20016 lbu $v0, 0x16($sp)
.text+0x8cce0 file=0x8cd20 1450001a bne $v0, $s0, 0x8cd4c
.text+0x8cce4 file=0x8cd24 00000000 nop 
.text+0x8cce8 file=0x8cd28 1480000f bnez $a0, 0x8cd28
.text+0x8ccec file=0x8cd2c 24040027 addiu $a0, $zero, 0x27
.text+0x8ccf0 file=0x8cd30 14640006 bne $v1, $a0, 0x8cd0c
.text+0x8ccf4 file=0x8cd34 00000000 nop 
.text+0x8ccf8 file=0x8cd38 24030022 addiu $v1, $zero, 0x22
.text+0x8ccfc file=0x8cd3c 14430014 bne $v0, $v1, 0x8cd50
.text+0x8cd00 file=0x8cd40 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cd04 file=0x8cd44 080233b8 j 0x8cee0 ;  .text+0x0 type=4
.text+0x8cd08 file=0x8cd48 8fbf0034 lw $ra, 0x34($sp)
.text+0x8cd0c file=0x8cd4c 24040015 addiu $a0, $zero, 0x15
.text+0x8cd10 file=0x8cd50 14640005 bne $v1, $a0, 0x8cd28
.text+0x8cd14 file=0x8cd54 2403006d addiu $v1, $zero, 0x6d
.text+0x8cd18 file=0x8cd58 1443000d bne $v0, $v1, 0x8cd50
.text+0x8cd1c file=0x8cd5c 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cd20 file=0x8cd60 080233b8 j 0x8cee0 ;  .text+0x0 type=4
.text+0x8cd24 file=0x8cd64 8fbf0034 lw $ra, 0x34($sp)
.text+0x8cd28 file=0x8cd68 2402009f addiu $v0, $zero, 0x9f
.text+0x8cd2c file=0x8cd6c 16620008 bne $s3, $v0, 0x8cd50
.text+0x8cd30 file=0x8cd70 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cd34 file=0x8cd74 240200db addiu $v0, $zero, 0xdb
.text+0x8cd38 file=0x8cd78 16020005 bne $s0, $v0, 0x8cd50
.text+0x8cd3c file=0x8cd7c 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cd40 file=0x8cd80 240200dc addiu $v0, $zero, 0xdc
.text+0x8cd44 file=0x8cd84 12220066 beq $s1, $v0, 0x8cee0
.text+0x8cd48 file=0x8cd88 8fbf0034 lw $ra, 0x34($sp)
.text+0x8cd4c file=0x8cd8c 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8cd50 file=0x8cd90 8c440f28 lw $a0, 0xf28($v0) ;  .data+0x0 type=6
.text+0x8cd54 file=0x8cd94 3c03fa1b lui $v1, 0xfa1b
.text+0x8cd58 file=0x8cd98 3463dbab ori $v1, $v1, 0xdbab
.text+0x8cd5c file=0x8cd9c 3c065555 lui $a2, 0x5555
.text+0x8cd60 file=0x8cda0 00831821 addu $v1, $a0, $v1
.text+0x8cd64 file=0x8cda4 24c65556 addiu $a2, $a2, 0x5556
.text+0x8cd68 file=0x8cda8 00660018 mult $v1, $a2
.text+0x8cd6c file=0x8cdac 000317c3 sra $v0, $v1, 0x1f
.text+0x8cd70 file=0x8cdb0 3c130000 lui $s3, 0 ;  .bss+0x0 type=5
.text+0x8cd74 file=0x8cdb4 26737a10 addiu $s3, $s3, 0x7a10 ;  .bss+0x0 type=6
.text+0x8cd78 file=0x8cdb8 3c03000f lui $v1, 0xf
.text+0x8cd7c file=0x8cdbc 3463ffdf ori $v1, $v1, 0xffdf
.text+0x8cd80 file=0x8cdc0 02439024 and $s2, $s2, $v1
.text+0x8cd84 file=0x8cdc4 00122840 sll $a1, $s2, 1
.text+0x8cd88 file=0x8cdc8 3c0305e4 lui $v1, 0x5e4
.text+0x8cd8c file=0x8cdcc 00b29021 addu $s2, $a1, $s2
.text+0x8cd90 file=0x8cdd0 24652455 addiu $a1, $v1, 0x2455
.text+0x8cd94 file=0x8cdd4 02459021 addu $s2, $s2, $a1
.text+0x8cd98 file=0x8cdd8 3c140000 lui $s4, 0 ;  .data+0x0 type=5
.text+0x8cd9c file=0x8cddc 2465245e addiu $a1, $v1, 0x245e
.text+0x8cda0 file=0x8cde0 ae920f24 sw $s2, 0xf24($s4) ;  .data+0x0 type=6
.text+0x8cda4 file=0x8cde4 00003010 mfhi $a2
.text+0x8cda8 file=0x8cde8 00c21023 subu $v0, $a2, $v0
.text+0x8cdac file=0x8cdec 000230c0 sll $a2, $v0, 3
.text+0x8cdb0 file=0x8cdf0 00023940 sll $a3, $v0, 5
.text+0x8cdb4 file=0x8cdf4 00e63023 subu $a2, $a3, $a2
.text+0x8cdb8 file=0x8cdf8 00c21021 addu $v0, $a2, $v0
.text+0x8cdbc file=0x8cdfc 02621021 addu $v0, $s3, $v0
.text+0x8cdc0 file=0x8ce00 90460002 lbu $a2, 2($v0)
.text+0x8cdc4 file=0x8ce04 30c600ef andi $a2, $a2, 0xef
.text+0x8cdc8 file=0x8ce08 14850044 bne $a0, $a1, 0x8cedc
.text+0x8cdcc file=0x8ce0c a0460002 sb $a2, 2($v0)
.text+0x8cdd0 file=0x8ce10 24100004 addiu $s0, $zero, 4
.text+0x8cdd4 file=0x8ce14 24120001 addiu $s2, $zero, 1
.text+0x8cdd8 file=0x8ce18 08023383 j 0x8ce0c ;  .text+0x0 type=4
.text+0x8cddc file=0x8ce1c 24752c23 addiu $s5, $v1, 0x2c23
.text+0x8cde0 file=0x8ce20 2491ffe7 addiu $s1, $a0, -0x19
.text+0x8cde4 file=0x8ce24 02202821 move $a1, $s1
.text+0x8cde8 file=0x8ce28 0c000000 jal 0 ; memcmp SHN_UNDEF+0x0 type=4
.text+0x8cdec file=0x8ce2c 24060019 addiu $a2, $zero, 0x19
.text+0x8cdf0 file=0x8ce30 1440003b bnez $v0, 0x8cee0
.text+0x8cdf4 file=0x8ce34 8fbf0034 lw $ra, 0x34($sp)
.text+0x8cdf8 file=0x8ce38 1612000a bne $s0, $s2, 0x8ce24
.text+0x8cdfc file=0x8ce3c 02202021 move $a0, $s1
.text+0x8ce00 file=0x8ce40 0c018f33 jal 0x63ccc ;  .text+0x0 type=4
.text+0x8ce04 file=0x8ce44 ae950f24 sw $s5, 0xf24($s4) ;  .data+0x0 type=6
.text+0x8ce08 file=0x8ce48 8fb00010 lw $s0, 0x10($sp)
.text+0x8ce0c file=0x8ce4c 001020c0 sll $a0, $s0, 3
.text+0x8ce10 file=0x8ce50 00101140 sll $v0, $s0, 5
.text+0x8ce14 file=0x8ce54 00442023 subu $a0, $v0, $a0
.text+0x8ce18 file=0x8ce58 00902021 addu $a0, $a0, $s0
.text+0x8ce1c file=0x8ce5c 2484ffe7 addiu $a0, $a0, -0x19
.text+0x8ce20 file=0x8ce60 02642021 addu $a0, $s3, $a0
.text+0x8ce24 file=0x8ce64 2610ffff addiu $s0, $s0, -1
.text+0x8ce28 file=0x8ce68 1600ffed bnez $s0, 0x8cde0
.text+0x8ce2c file=0x8ce6c afb00010 sw $s0, 0x10($sp)
.text+0x8ce30 file=0x8ce70 080233b8 j 0x8cee0 ;  .text+0x0 type=4
.text+0x8ce34 file=0x8ce74 8fbf0034 lw $ra, 0x34($sp)
.text+0x8ce38 file=0x8ce78 96030100 lhu $v1, 0x100($s0)
.text+0x8ce3c file=0x8ce7c 2464ffff addiu $a0, $v1, -1
.text+0x8ce40 file=0x8ce80 2c840f00 sltiu $a0, $a0, 0xf00
.text+0x8ce44 file=0x8ce84 10800006 beqz $a0, 0x8ce60
.text+0x8ce48 file=0x8ce88 26070100 addiu $a3, $s0, 0x100
.text+0x8ce4c file=0x8ce8c 00033042 srl $a2, $v1, 1
.text+0x8ce50 file=0x8ce90 00e02821 move $a1, $a3
.text+0x8ce54 file=0x8ce94 00002021 move $a0, $zero
.text+0x8ce58 file=0x8ce98 080232f1 j 0x8cbc4 ;  .text+0x0 type=4
.text+0x8ce5c file=0x8ce9c 00001821 move $v1, $zero
.text+0x8ce60 file=0x8cea0 96030080 lhu $v1, 0x80($s0)
.text+0x8ce64 file=0x8cea4 2464ffff addiu $a0, $v1, -1
.text+0x8ce68 file=0x8cea8 2c840f80 sltiu $a0, $a0, 0xf80
.text+0x8ce6c file=0x8ceac 10800006 beqz $a0, 0x8ce88
.text+0x8ce70 file=0x8ceb0 26060080 addiu $a2, $s0, 0x80
.text+0x8ce74 file=0x8ceb4 00034042 srl $t0, $v1, 1
.text+0x8ce78 file=0x8ceb8 00c02821 move $a1, $a2
.text+0x8ce7c file=0x8cebc 00002021 move $a0, $zero
.text+0x8ce80 file=0x8cec0 080232fc j 0x8cbf0 ;  .text+0x0 type=4
.text+0x8ce84 file=0x8cec4 00001821 move $v1, $zero
.text+0x8ce88 file=0x8cec8 92040001 lbu $a0, 1($s0)
.text+0x8ce8c file=0x8cecc 92050000 lbu $a1, ($s0)
.text+0x8ce90 file=0x8ced0 240300ff addiu $v1, $zero, 0xff
.text+0x8ce94 file=0x8ced4 00641823 subu $v1, $v1, $a0
.text+0x8ce98 file=0x8ced8 1065ff5c beq $v1, $a1, 0x8cc0c
.text+0x8ce9c file=0x8cedc 93a30011 lbu $v1, 0x11($sp)
.text+0x8cea0 file=0x8cee0 08023312 j 0x8cc48 ;  .text+0x0 type=4
.text+0x8cea4 file=0x8cee4 9207008d lbu $a3, 0x8d($s0)
.text+0x8cea8 file=0x8cee8 080233ad j 0x8ceb4 ;  .text+0x0 type=4
.text+0x8ceac file=0x8ceec 00e01021 move $v0, $a3
.text+0x8ceb0 file=0x8cef0 00c01021 move $v0, $a2
.text+0x8ceb4 file=0x8cef4 02002021 move $a0, $s0
.text+0x8ceb8 file=0x8cef8 9051000c lbu $s1, 0xc($v0)
.text+0x8cebc file=0x8cefc 9053000d lbu $s3, 0xd($v0)
.text+0x8cec0 file=0x8cf00 0c000000 jal 0 ; kfree SHN_UNDEF+0x0 type=4
.text+0x8cec4 file=0x8cf04 9050000e lbu $s0, 0xe($v0)
.text+0x8cec8 file=0x8cf08 93a40014 lbu $a0, 0x14($sp)
.text+0x8cecc file=0x8cf0c 1491ffa0 bne $a0, $s1, 0x8cd50
.text+0x8ced0 file=0x8cf10 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x8ced4 file=0x8cf14 08023335 j 0x8ccd4 ;  .text+0x0 type=4
.text+0x8ced8 file=0x8cf18 93a30015 lbu $v1, 0x15($sp)
.text+0x8cedc file=0x8cf1c 8fbf0034 lw $ra, 0x34($sp)
.text+0x8cee0 file=0x8cf20 8fb50030 lw $s5, 0x30($sp)
.text+0x8cee4 file=0x8cf24 8fb4002c lw $s4, 0x2c($sp)
.text+0x8cee8 file=0x8cf28 8fb30028 lw $s3, 0x28($sp)
.text+0x8ceec file=0x8cf2c 8fb20024 lw $s2, 0x24($sp)
.text+0x8cef0 file=0x8cf30 8fb10020 lw $s1, 0x20($sp)
.text+0x8cef4 file=0x8cf34 8fb0001c lw $s0, 0x1c($sp)
.text+0x8cef8 file=0x8cf38 03e00008 jr $ra
.text+0x8cefc file=0x8cf3c 27bd0038 addiu $sp, $sp, 0x38