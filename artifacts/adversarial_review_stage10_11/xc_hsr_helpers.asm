.text+0x5db60 file=0x5dba0 27bdffe0 addiu $sp, $sp, -0x20
.text+0x5db64 file=0x5dba4 afb20018 sw $s2, 0x18($sp)
.text+0x5db68 file=0x5dba8 afb10014 sw $s1, 0x14($sp)
.text+0x5db6c file=0x5dbac afb00010 sw $s0, 0x10($sp)
.text+0x5db70 file=0x5dbb0 afbf001c sw $ra, 0x1c($sp)
.text+0x5db74 file=0x5dbb4 8f830018 lw $v1, 0x18($gp)
.text+0x5db78 file=0x5dbb8 3c100000 lui $s0, 0 ;  .bss+0x0 type=5
.text+0x5db7c file=0x5dbbc 3c110000 lui $s1, 0 ;  .bss+0x0 type=5
.text+0x5db80 file=0x5dbc0 3c120000 lui $s2, 0 ;  .bss+0x0 type=5
.text+0x5db84 file=0x5dbc4 af800018 sw $zero, 0x18($gp)
.text+0x5db88 file=0x5dbc8 ae2349b0 sw $v1, 0x49b0($s1) ;  .bss+0x0 type=6
.text+0x5db8c file=0x5dbcc ae0049b8 sw $zero, 0x49b8($s0) ;  .bss+0x0 type=6
.text+0x5db90 file=0x5dbd0 0c000000 jal 0 ; filp_open SHN_UNDEF+0x0 type=4
.text+0x5db94 file=0x5dbd4 ae4049b4 sw $zero, 0x49b4($s2) ;  .bss+0x0 type=6
.text+0x5db98 file=0x5dbd8 8e2449b0 lw $a0, 0x49b0($s1) ;  .bss+0x0 type=6
.text+0x5db9c file=0x5dbdc 2c43f001 sltiu $v1, $v0, -0xfff
.text+0x5dba0 file=0x5dbe0 ae0249b8 sw $v0, 0x49b8($s0) ;  .bss+0x0 type=6
.text+0x5dba4 file=0x5dbe4 14600003 bnez $v1, 0x5dbb4
.text+0x5dba8 file=0x5dbe8 af840018 sw $a0, 0x18($gp)
.text+0x5dbac file=0x5dbec ae4249b4 sw $v0, 0x49b4($s2) ;  .bss+0x0 type=6
.text+0x5dbb0 file=0x5dbf0 00001021 move $v0, $zero
.text+0x5dbb4 file=0x5dbf4 8fbf001c lw $ra, 0x1c($sp)
.text+0x5dbb8 file=0x5dbf8 8fb20018 lw $s2, 0x18($sp)
.text+0x5dbbc file=0x5dbfc 8fb10014 lw $s1, 0x14($sp)
.text+0x5dbc0 file=0x5dc00 8fb00010 lw $s0, 0x10($sp)
.text+0x5dbc4 file=0x5dc04 03e00008 jr $ra
.text+0x5dbc8 file=0x5dc08 27bd0020 addiu $sp, $sp, 0x20
.text+0x5dbcc file=0x5dc0c 27bdffe0 addiu $sp, $sp, -0x20
.text+0x5dbd0 file=0x5dc10 afbf001c sw $ra, 0x1c($sp)
.text+0x5dbd4 file=0x5dc14 afb10018 sw $s1, 0x18($sp)
.text+0x5dbd8 file=0x5dc18 afb00014 sw $s0, 0x14($sp)
.text+0x5dbdc file=0x5dc1c 8f820018 lw $v0, 0x18($gp)
.text+0x5dbe0 file=0x5dc20 3c100000 lui $s0, 0 ;  .bss+0x0 type=5
.text+0x5dbe4 file=0x5dc24 3c110000 lui $s1, 0 ;  .bss+0x0 type=5
.text+0x5dbe8 file=0x5dc28 3c030000 lui $v1, 0 ;  .bss+0x0 type=5
.text+0x5dbec file=0x5dc2c af800018 sw $zero, 0x18($gp)
.text+0x5dbf0 file=0x5dc30 24870020 addiu $a3, $a0, 0x20
.text+0x5dbf4 file=0x5dc34 ac654934 sw $a1, 0x4934($v1) ;  .bss+0x0 type=6
.text+0x5dbf8 file=0x5dc38 ae004930 sw $zero, 0x4930($s0) ;  .bss+0x0 type=6
.text+0x5dbfc file=0x5dc3c 0c000000 jal 0 ; vfs_read SHN_UNDEF+0x0 type=4
.text+0x5dc00 file=0x5dc40 ae22492c sw $v0, 0x492c($s1) ;  .bss+0x0 type=6
.text+0x5dc04 file=0x5dc44 8e23492c lw $v1, 0x492c($s1) ;  .bss+0x0 type=6
.text+0x5dc08 file=0x5dc48 ae024930 sw $v0, 0x4930($s0) ;  .bss+0x0 type=6
.text+0x5dc0c file=0x5dc4c af830018 sw $v1, 0x18($gp)
.text+0x5dc10 file=0x5dc50 8fbf001c lw $ra, 0x1c($sp)
.text+0x5dc14 file=0x5dc54 8fb10018 lw $s1, 0x18($sp)
.text+0x5dc18 file=0x5dc58 8fb00014 lw $s0, 0x14($sp)
.text+0x5dc1c file=0x5dc5c 03e00008 jr $ra
.text+0x5dc20 file=0x5dc60 27bd0020 addiu $sp, $sp, 0x20
.text+0x5dc24 file=0x5dc64 27bdffd0 addiu $sp, $sp, -0x30
.text+0x5dc28 file=0x5dc68 24020001 addiu $v0, $zero, 1
.text+0x5dc2c file=0x5dc6c afb3001c sw $s3, 0x1c($sp)
.text+0x5dc30 file=0x5dc70 afb10014 sw $s1, 0x14($sp)
.text+0x5dc34 file=0x5dc74 afb00010 sw $s0, 0x10($sp)
.text+0x5dc38 file=0x5dc78 3c110000 lui $s1, 0 ;  .bss+0x0 type=5
.text+0x5dc3c file=0x5dc7c 3c100000 lui $s0, 0 ;  .bss+0x0 type=5
.text+0x5dc40 file=0x5dc80 3c130000 lui $s3, 0 ;  .bss+0x0 type=5
.text+0x5dc44 file=0x5dc84 afb20018 sw $s2, 0x18($sp)
.text+0x5dc48 file=0x5dc88 afbf002c sw $ra, 0x2c($sp)
.text+0x5dc4c file=0x5dc8c afb60028 sw $s6, 0x28($sp)
.text+0x5dc50 file=0x5dc90 afb50024 sw $s5, 0x24($sp)
.text+0x5dc54 file=0x5dc94 afb40020 sw $s4, 0x20($sp)
.text+0x5dc58 file=0x5dc98 00a09021 move $s2, $a1
.text+0x5dc5c file=0x5dc9c ae0247c4 sw $v0, 0x47c4($s0) ;  .bss+0x0 type=6
.text+0x5dc60 file=0x5dca0 ae2047c0 sw $zero, 0x47c0($s1) ;  .bss+0x0 type=6
.text+0x5dc64 file=0x5dca4 10a00008 beqz $a1, 0x5dc88
.text+0x5dc68 file=0x5dca8 ae6047bc sw $zero, 0x47bc($s3) ;  .bss+0x0 type=6
.text+0x5dc6c file=0x5dcac 10800006 beqz $a0, 0x5dc88
.text+0x5dc70 file=0x5dcb0 00c0a021 move $s4, $a2
.text+0x5dc74 file=0x5dcb4 24050101 addiu $a1, $zero, 0x101
.text+0x5dc78 file=0x5dcb8 0c0176d8 jal 0x5db60 ;  .text+0x0 type=4
.text+0x5dc7c file=0x5dcbc 240601ff addiu $a2, $zero, 0x1ff
.text+0x5dc80 file=0x5dcc0 14400003 bnez $v0, 0x5dc90
.text+0x5dc84 file=0x5dcc4 ae2247c0 sw $v0, 0x47c0($s1) ;  .bss+0x0 type=6
.text+0x5dc88 file=0x5dcc8 0801773d j 0x5dcf4 ;  .text+0x0 type=4
.text+0x5dc8c file=0x5dccc ae0047c4 sw $zero, 0x47c4($s0) ;  .bss+0x0 type=6
.text+0x5dc90 file=0x5dcd0 8f880018 lw $t0, 0x18($gp)
.text+0x5dc94 file=0x5dcd4 00402021 move $a0, $v0
.text+0x5dc98 file=0x5dcd8 3c150000 lui $s5, 0 ;  .bss+0x0 type=5
.text+0x5dc9c file=0x5dcdc 3c160000 lui $s6, 0 ;  .bss+0x0 type=5
.text+0x5dca0 file=0x5dce0 24470020 addiu $a3, $v0, 0x20
.text+0x5dca4 file=0x5dce4 af800018 sw $zero, 0x18($gp)
.text+0x5dca8 file=0x5dce8 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5dcac file=0x5dcec 02402821 move $a1, $s2
.text+0x5dcb0 file=0x5dcf0 02803021 move $a2, $s4
.text+0x5dcb4 file=0x5dcf4 ac5247b8 sw $s2, 0x47b8($v0) ;  .bss+0x0 type=6
.text+0x5dcb8 file=0x5dcf8 aea047b4 sw $zero, 0x47b4($s5) ;  .bss+0x0 type=6
.text+0x5dcbc file=0x5dcfc 0c000000 jal 0 ; vfs_write SHN_UNDEF+0x0 type=4
.text+0x5dcc0 file=0x5dd00 aec847b0 sw $t0, 0x47b0($s6) ;  .bss+0x0 type=6
.text+0x5dcc4 file=0x5dd04 8ec347b0 lw $v1, 0x47b0($s6) ;  .bss+0x0 type=6
.text+0x5dcc8 file=0x5dd08 aea247b4 sw $v0, 0x47b4($s5) ;  .bss+0x0 type=6
.text+0x5dccc file=0x5dd0c ae6247bc sw $v0, 0x47bc($s3) ;  .bss+0x0 type=6
.text+0x5dcd0 file=0x5dd10 af830018 sw $v1, 0x18($gp)
.text+0x5dcd4 file=0x5dd14 12820002 beq $s4, $v0, 0x5dce0
.text+0x5dcd8 file=0x5dd18 8e2447c0 lw $a0, 0x47c0($s1) ;  .bss+0x0 type=6
.text+0x5dcdc file=0x5dd1c ae0047c4 sw $zero, 0x47c4($s0) ;  .bss+0x0 type=6
.text+0x5dce0 file=0x5dd20 10800005 beqz $a0, 0x5dcf8
.text+0x5dce4 file=0x5dd24 8fbf002c lw $ra, 0x2c($sp)
.text+0x5dce8 file=0x5dd28 0c000000 jal 0 ; filp_close SHN_UNDEF+0x0 type=4
.text+0x5dcec file=0x5dd2c 00002821 move $a1, $zero
.text+0x5dcf0 file=0x5dd30 ae2047c0 sw $zero, 0x47c0($s1) ;  .bss+0x0 type=6
.text+0x5dcf4 file=0x5dd34 8fbf002c lw $ra, 0x2c($sp)
.text+0x5dcf8 file=0x5dd38 8e0247c4 lw $v0, 0x47c4($s0) ;  .bss+0x0 type=6
.text+0x5dcfc file=0x5dd3c 8fb60028 lw $s6, 0x28($sp)
.text+0x5dd00 file=0x5dd40 8fb50024 lw $s5, 0x24($sp)
.text+0x5dd04 file=0x5dd44 8fb40020 lw $s4, 0x20($sp)
.text+0x5dd08 file=0x5dd48 8fb3001c lw $s3, 0x1c($sp)
.text+0x5dd0c file=0x5dd4c 8fb20018 lw $s2, 0x18($sp)
.text+0x5dd10 file=0x5dd50 8fb10014 lw $s1, 0x14($sp)
.text+0x5dd14 file=0x5dd54 8fb00010 lw $s0, 0x10($sp)
.text+0x5dd18 file=0x5dd58 03e00008 jr $ra
.text+0x5dd1c file=0x5dd5c 27bd0030 addiu $sp, $sp, 0x30
.text+0x5dd20 file=0x5dd60 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5dd24 file=0x5dd64 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5dd28 file=0x5dd68 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5dd2c file=0x5dd6c ad2047a8 sw $zero, 0x47a8($t1) ;  .bss+0x0 type=6
.text+0x5dd30 file=0x5dd70 24420c50 addiu $v0, $v0, 0xc50 ;  .data+0x0 type=6
.text+0x5dd34 file=0x5dd74 00001821 move $v1, $zero
.text+0x5dd38 file=0x5dd78 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5dd3c file=0x5dd7c 24070013 addiu $a3, $zero, 0x13
.text+0x5dd40 file=0x5dd80 30640003 andi $a0, $v1, 3
.text+0x5dd44 file=0x5dd84 00883021 addu $a2, $a0, $t0
.text+0x5dd48 file=0x5dd88 80440000 lb $a0, ($v0)
.text+0x5dd4c file=0x5dd8c 14800003 bnez $a0, 0x5dd5c
.text+0x5dd50 file=0x5dd90 24650001 addiu $a1, $v1, 1
.text+0x5dd54 file=0x5dd94 0801775e j 0x5dd78 ;  .text+0x0 type=4
.text+0x5dd58 file=0x5dd98 ad2347a8 sw $v1, 0x47a8($t1) ;  .bss+0x0 type=6
.text+0x5dd5c file=0x5dd9c 90c60000 lbu $a2, ($a2)
.text+0x5dd60 file=0x5dda0 24420001 addiu $v0, $v0, 1
.text+0x5dd64 file=0x5dda4 00a01821 move $v1, $a1
.text+0x5dd68 file=0x5dda8 00862026 xor $a0, $a0, $a2
.text+0x5dd6c file=0x5ddac 14a7fff4 bne $a1, $a3, 0x5dd40
.text+0x5dd70 file=0x5ddb0 a044ffff sb $a0, -1($v0)
.text+0x5dd74 file=0x5ddb4 ad2747a8 sw $a3, 0x47a8($t1) ;  .bss+0x0 type=6
.text+0x5dd78 file=0x5ddb8 24030001 addiu $v1, $zero, 1
.text+0x5dd7c file=0x5ddbc 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5dd80 file=0x5ddc0 ac4347ac sw $v1, 0x47ac($v0) ;  .bss+0x0 type=6
.text+0x5dd84 file=0x5ddc4 03e00008 jr $ra
.text+0x5dd88 file=0x5ddc8 00001021 move $v0, $zero
.text+0x5dd8c file=0x5ddcc 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5dd90 file=0x5ddd0 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5dd94 file=0x5ddd4 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5dd98 file=0x5ddd8 ad2049a0 sw $zero, 0x49a0($t1) ;  .bss+0x0 type=6
.text+0x5dd9c file=0x5dddc 24420d7c addiu $v0, $v0, 0xd7c ;  .data+0x0 type=6
.text+0x5dda0 file=0x5dde0 00001821 move $v1, $zero
.text+0x5dda4 file=0x5dde4 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5dda8 file=0x5dde8 2407000d addiu $a3, $zero, 0xd
.text+0x5ddac file=0x5ddec 30640003 andi $a0, $v1, 3
.text+0x5ddb0 file=0x5ddf0 00883021 addu $a2, $a0, $t0
.text+0x5ddb4 file=0x5ddf4 80440000 lb $a0, ($v0)
.text+0x5ddb8 file=0x5ddf8 14800003 bnez $a0, 0x5ddc8
.text+0x5ddbc file=0x5ddfc 24650001 addiu $a1, $v1, 1
.text+0x5ddc0 file=0x5de00 08017779 j 0x5dde4 ;  .text+0x0 type=4
.text+0x5ddc4 file=0x5de04 ad2349a0 sw $v1, 0x49a0($t1) ;  .bss+0x0 type=6
.text+0x5ddc8 file=0x5de08 90c60000 lbu $a2, ($a2)
.text+0x5ddcc file=0x5de0c 24420001 addiu $v0, $v0, 1
.text+0x5ddd0 file=0x5de10 00a01821 move $v1, $a1
.text+0x5ddd4 file=0x5de14 00862026 xor $a0, $a0, $a2
.text+0x5ddd8 file=0x5de18 14a7fff4 bne $a1, $a3, 0x5ddac
.text+0x5dddc file=0x5de1c a044ffff sb $a0, -1($v0)
.text+0x5dde0 file=0x5de20 ad2749a0 sw $a3, 0x49a0($t1) ;  .bss+0x0 type=6
.text+0x5dde4 file=0x5de24 24030001 addiu $v1, $zero, 1
.text+0x5dde8 file=0x5de28 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5ddec file=0x5de2c ac4349a4 sw $v1, 0x49a4($v0) ;  .bss+0x0 type=6
.text+0x5ddf0 file=0x5de30 03e00008 jr $ra
.text+0x5ddf4 file=0x5de34 00001021 move $v0, $zero
.text+0x5ddf8 file=0x5de38 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5ddfc file=0x5de3c 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5de00 file=0x5de40 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5de04 file=0x5de44 ad204808 sw $zero, 0x4808($t1) ;  .bss+0x0 type=6
.text+0x5de08 file=0x5de48 24420d44 addiu $v0, $v0, 0xd44 ;  .data+0x0 type=6
.text+0x5de0c file=0x5de4c 00001821 move $v1, $zero
.text+0x5de10 file=0x5de50 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5de14 file=0x5de54 2407000e addiu $a3, $zero, 0xe
.text+0x5de18 file=0x5de58 30640003 andi $a0, $v1, 3
.text+0x5de1c file=0x5de5c 00883021 addu $a2, $a0, $t0
.text+0x5de20 file=0x5de60 80440000 lb $a0, ($v0)
.text+0x5de24 file=0x5de64 14800003 bnez $a0, 0x5de34
.text+0x5de28 file=0x5de68 24650001 addiu $a1, $v1, 1
.text+0x5de2c file=0x5de6c 08017794 j 0x5de50 ;  .text+0x0 type=4
.text+0x5de30 file=0x5de70 ad234808 sw $v1, 0x4808($t1) ;  .bss+0x0 type=6
.text+0x5de34 file=0x5de74 90c60000 lbu $a2, ($a2)
.text+0x5de38 file=0x5de78 24420001 addiu $v0, $v0, 1
.text+0x5de3c file=0x5de7c 00a01821 move $v1, $a1
.text+0x5de40 file=0x5de80 00862026 xor $a0, $a0, $a2
.text+0x5de44 file=0x5de84 14a7fff4 bne $a1, $a3, 0x5de18
.text+0x5de48 file=0x5de88 a044ffff sb $a0, -1($v0)
.text+0x5de4c file=0x5de8c ad274808 sw $a3, 0x4808($t1) ;  .bss+0x0 type=6
.text+0x5de50 file=0x5de90 24030001 addiu $v1, $zero, 1
.text+0x5de54 file=0x5de94 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5de58 file=0x5de98 ac43480c sw $v1, 0x480c($v0) ;  .bss+0x0 type=6
.text+0x5de5c file=0x5de9c 03e00008 jr $ra
.text+0x5de60 file=0x5dea0 00001021 move $v0, $zero
.text+0x5de64 file=0x5dea4 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5de68 file=0x5dea8 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5de6c file=0x5deac 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5de70 file=0x5deb0 ad204810 sw $zero, 0x4810($t1) ;  .bss+0x0 type=6
.text+0x5de74 file=0x5deb4 24420d54 addiu $v0, $v0, 0xd54 ;  .data+0x0 type=6
.text+0x5de78 file=0x5deb8 00001821 move $v1, $zero
.text+0x5de7c file=0x5debc 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5de80 file=0x5dec0 2407000d addiu $a3, $zero, 0xd
.text+0x5de84 file=0x5dec4 30640003 andi $a0, $v1, 3
.text+0x5de88 file=0x5dec8 00883021 addu $a2, $a0, $t0
.text+0x5de8c file=0x5decc 80440000 lb $a0, ($v0)
.text+0x5de90 file=0x5ded0 14800003 bnez $a0, 0x5dea0
.text+0x5de94 file=0x5ded4 24650001 addiu $a1, $v1, 1
.text+0x5de98 file=0x5ded8 080177af j 0x5debc ;  .text+0x0 type=4
.text+0x5de9c file=0x5dedc ad234810 sw $v1, 0x4810($t1) ;  .bss+0x0 type=6
.text+0x5dea0 file=0x5dee0 90c60000 lbu $a2, ($a2)
.text+0x5dea4 file=0x5dee4 24420001 addiu $v0, $v0, 1
.text+0x5dea8 file=0x5dee8 00a01821 move $v1, $a1
.text+0x5deac file=0x5deec 00862026 xor $a0, $a0, $a2
.text+0x5deb0 file=0x5def0 14a7fff4 bne $a1, $a3, 0x5de84
.text+0x5deb4 file=0x5def4 a044ffff sb $a0, -1($v0)
.text+0x5deb8 file=0x5def8 ad274810 sw $a3, 0x4810($t1) ;  .bss+0x0 type=6
.text+0x5debc file=0x5defc 24030001 addiu $v1, $zero, 1
.text+0x5dec0 file=0x5df00 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5dec4 file=0x5df04 ac434814 sw $v1, 0x4814($v0) ;  .bss+0x0 type=6
.text+0x5dec8 file=0x5df08 03e00008 jr $ra
.text+0x5decc file=0x5df0c 00001021 move $v0, $zero
.text+0x5ded0 file=0x5df10 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5ded4 file=0x5df14 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5ded8 file=0x5df18 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5dedc file=0x5df1c ad2047e0 sw $zero, 0x47e0($t1) ;  .bss+0x0 type=6
.text+0x5dee0 file=0x5df20 24420cd0 addiu $v0, $v0, 0xcd0 ;  .data+0x0 type=6
.text+0x5dee4 file=0x5df24 00001821 move $v1, $zero
.text+0x5dee8 file=0x5df28 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5deec file=0x5df2c 2407000b addiu $a3, $zero, 0xb
.text+0x5def0 file=0x5df30 30640003 andi $a0, $v1, 3
.text+0x5def4 file=0x5df34 00883021 addu $a2, $a0, $t0
.text+0x5def8 file=0x5df38 80440000 lb $a0, ($v0)
.text+0x5defc file=0x5df3c 14800003 bnez $a0, 0x5df0c
.text+0x5df00 file=0x5df40 24650001 addiu $a1, $v1, 1
.text+0x5df04 file=0x5df44 080177ca j 0x5df28 ;  .text+0x0 type=4
.text+0x5df08 file=0x5df48 ad2347e0 sw $v1, 0x47e0($t1) ;  .bss+0x0 type=6
.text+0x5df0c file=0x5df4c 90c60000 lbu $a2, ($a2)
.text+0x5df10 file=0x5df50 24420001 addiu $v0, $v0, 1
.text+0x5df14 file=0x5df54 00a01821 move $v1, $a1
.text+0x5df18 file=0x5df58 00862026 xor $a0, $a0, $a2
.text+0x5df1c file=0x5df5c 14a7fff4 bne $a1, $a3, 0x5def0
.text+0x5df20 file=0x5df60 a044ffff sb $a0, -1($v0)
.text+0x5df24 file=0x5df64 ad2747e0 sw $a3, 0x47e0($t1) ;  .bss+0x0 type=6
.text+0x5df28 file=0x5df68 24030001 addiu $v1, $zero, 1
.text+0x5df2c file=0x5df6c 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5df30 file=0x5df70 ac4347e4 sw $v1, 0x47e4($v0) ;  .bss+0x0 type=6
.text+0x5df34 file=0x5df74 03e00008 jr $ra
.text+0x5df38 file=0x5df78 00001021 move $v0, $zero
.text+0x5df3c file=0x5df7c 3c090000 lui $t1, 0 ;  .bss+0x0 type=5
.text+0x5df40 file=0x5df80 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x5df44 file=0x5df84 3c080001 lui $t0, 1 ;  .rodata+0x0 type=5
.text+0x5df48 file=0x5df88 ad2049a8 sw $zero, 0x49a8($t1) ;  .bss+0x0 type=6
.text+0x5df4c file=0x5df8c 24420d8c addiu $v0, $v0, 0xd8c ;  .data+0x0 type=6
.text+0x5df50 file=0x5df90 00001821 move $v1, $zero
.text+0x5df54 file=0x5df94 250882a8 addiu $t0, $t0, -0x7d58 ;  .rodata+0x0 type=6
.text+0x5df58 file=0x5df98 24070011 addiu $a3, $zero, 0x11
.text+0x5df5c file=0x5df9c 30640003 andi $a0, $v1, 3
.text+0x5df60 file=0x5dfa0 00883021 addu $a2, $a0, $t0
.text+0x5df64 file=0x5dfa4 80440000 lb $a0, ($v0)
.text+0x5df68 file=0x5dfa8 14800003 bnez $a0, 0x5df78
.text+0x5df6c file=0x5dfac 24650001 addiu $a1, $v1, 1
.text+0x5df70 file=0x5dfb0 080177e5 j 0x5df94 ;  .text+0x0 type=4
.text+0x5df74 file=0x5dfb4 ad2349a8 sw $v1, 0x49a8($t1) ;  .bss+0x0 type=6
.text+0x5df78 file=0x5dfb8 90c60000 lbu $a2, ($a2)
.text+0x5df7c file=0x5dfbc 24420001 addiu $v0, $v0, 1
.text+0x5df80 file=0x5dfc0 00a01821 move $v1, $a1
.text+0x5df84 file=0x5dfc4 00862026 xor $a0, $a0, $a2
.text+0x5df88 file=0x5dfc8 14a7fff4 bne $a1, $a3, 0x5df5c
.text+0x5df8c file=0x5dfcc a044ffff sb $a0, -1($v0)
.text+0x5df90 file=0x5dfd0 ad2749a8 sw $a3, 0x49a8($t1) ;  .bss+0x0 type=6
.text+0x5df94 file=0x5dfd4 24030001 addiu $v1, $zero, 1
.text+0x5df98 file=0x5dfd8 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5df9c file=0x5dfdc ac4349ac sw $v1, 0x49ac($v0) ;  .bss+0x0 type=6
.text+0x5dfa0 file=0x5dfe0 03e00008 jr $ra
.text+0x5dfa4 file=0x5dfe4 00001021 move $v0, $zero
.text+0x5dfa8 file=0x5dfe8 00042027 nor $a0, $zero, $a0
.text+0x5dfac file=0x5dfec 308a0007 andi $t2, $a0, 7
.text+0x5dfb0 file=0x5dff0 3c070000 lui $a3, 0 ;  .bss+0x0 type=5
.text+0x5dfb4 file=0x5dff4 3c060000 lui $a2, 0 ;  .bss+0x0 type=5
.text+0x5dfb8 file=0x5dff8 24020007 addiu $v0, $zero, 7
.text+0x5dfbc file=0x5dffc a0e04a04 sb $zero, 0x4a04($a3) ;  .bss+0x0 type=6
.text+0x5dfc0 file=0x5e000 acc24a00 sw $v0, 0x4a00($a2) ;  .bss+0x0 type=6
.text+0x5dfc4 file=0x5e004 7c052c20 seb $a1, $a1
.text+0x5dfc8 file=0x5e008 000a5400 sll $t2, $t2, 0x10
.text+0x5dfcc file=0x5e00c 24030007 addiu $v1, $zero, 7
.text+0x5dfd0 file=0x5e010 24090001 addiu $t1, $zero, 1
.text+0x5dfd4 file=0x5e014 3c04bf00 lui $a0, 0xbf00
.text+0x5dfd8 file=0x5e018 00691004 sllv $v0, $t1, $v1
.text+0x5dfdc file=0x5e01c 00a21024 and $v0, $a1, $v0
.text+0x5dfe0 file=0x5e020 7c021420 seb $v0, $v0
.text+0x5dfe4 file=0x5e024 0002102b sltu $v0, $zero, $v0
.text+0x5dfe8 file=0x5e028 01421025 or $v0, $t2, $v0
.text+0x5dfec file=0x5e02c 34430100 ori $v1, $v0, 0x100
.text+0x5dff0 file=0x5e030 ac820008 sw $v0, 8($a0)
.text+0x5dff4 file=0x5e034 ac830008 sw $v1, 8($a0)
.text+0x5dff8 file=0x5e038 8c82000c lw $v0, 0xc($a0)
.text+0x5dffc file=0x5e03c 8cc34a00 lw $v1, 0x4a00($a2) ;  .bss+0x0 type=6
.text+0x5e000 file=0x5e040 90e84a04 lbu $t0, 0x4a04($a3) ;  .bss+0x0 type=6
.text+0x5e004 file=0x5e044 30420001 andi $v0, $v0, 1
.text+0x5e008 file=0x5e048 00621004 sllv $v0, $v0, $v1
.text+0x5e00c file=0x5e04c 00481025 or $v0, $v0, $t0
.text+0x5e010 file=0x5e050 2463ffff addiu $v1, $v1, -1
.text+0x5e014 file=0x5e054 304200ff andi $v0, $v0, 0xff
.text+0x5e018 file=0x5e058 a0e24a04 sb $v0, 0x4a04($a3) ;  .bss+0x0 type=6
.text+0x5e01c file=0x5e05c 0461ffee bgez $v1, 0x5dfd8
.text+0x5e020 file=0x5e060 acc34a00 sw $v1, 0x4a00($a2) ;  .bss+0x0 type=6
.text+0x5e024 file=0x5e064 03e00008 jr $ra
.text+0x5e028 file=0x5e068 00000000 nop 
.text+0x5e02c file=0x5e06c 27bdffd0 addiu $sp, $sp, -0x30
.text+0x5e030 file=0x5e070 afb10014 sw $s1, 0x14($sp)
.text+0x5e034 file=0x5e074 3c110000 lui $s1, 0 ;  .bss+0x0 type=5
.text+0x5e038 file=0x5e078 afb60028 sw $s6, 0x28($sp)
.text+0x5e03c file=0x5e07c afb50024 sw $s5, 0x24($sp)
.text+0x5e040 file=0x5e080 afb40020 sw $s4, 0x20($sp)
.text+0x5e044 file=0x5e084 afb3001c sw $s3, 0x1c($sp)
.text+0x5e048 file=0x5e088 afb20018 sw $s2, 0x18($sp)
.text+0x5e04c file=0x5e08c afb00010 sw $s0, 0x10($sp)
.text+0x5e050 file=0x5e090 afbf002c sw $ra, 0x2c($sp)
.text+0x5e054 file=0x5e094 00a0b021 move $s6, $a1
.text+0x5e058 file=0x5e098 00c0a821 move $s5, $a2
.text+0x5e05c file=0x5e09c 00e0a021 move $s4, $a3
.text+0x5e060 file=0x5e0a0 8fb30040 lw $s3, 0x40($sp)
.text+0x5e064 file=0x5e0a4 00809021 move $s2, $a0
.text+0x5e068 file=0x5e0a8 ae204a08 sw $zero, 0x4a08($s1) ;  .bss+0x0 type=6
.text+0x5e06c file=0x5e0ac 08017821 j 0x5e084 ;  .text+0x0 type=4
.text+0x5e070 file=0x5e0b0 00008021 move $s0, $zero
.text+0x5e074 file=0x5e0b4 90450000 lbu $a1, ($v0)
.text+0x5e078 file=0x5e0b8 0c0177ea jal 0x5dfa8 ;  .text+0x0 type=4
.text+0x5e07c file=0x5e0bc 26100001 addiu $s0, $s0, 1
.text+0x5e080 file=0x5e0c0 ae304a08 sw $s0, 0x4a08($s1) ;  .bss+0x0 type=6
.text+0x5e084 file=0x5e0c4 02d01021 addu $v0, $s6, $s0
.text+0x5e088 file=0x5e0c8 1615fffa bne $s0, $s5, 0x5e074
.text+0x5e08c file=0x5e0cc 02402021 move $a0, $s2
.text+0x5e090 file=0x5e0d0 ae204a08 sw $zero, 0x4a08($s1) ;  .bss+0x0 type=6
.text+0x5e094 file=0x5e0d4 0801782e j 0x5e0b8 ;  .text+0x0 type=4
.text+0x5e098 file=0x5e0d8 00008021 move $s0, $zero
.text+0x5e09c file=0x5e0dc 0c0177ea jal 0x5dfa8 ;  .text+0x0 type=4
.text+0x5e0a0 file=0x5e0e0 00000000 nop 
.text+0x5e0a4 file=0x5e0e4 02901821 addu $v1, $s4, $s0
.text+0x5e0a8 file=0x5e0e8 26100001 addiu $s0, $s0, 1
.text+0x5e0ac file=0x5e0ec a0620000 sb $v0, ($v1)
.text+0x5e0b0 file=0x5e0f0 ae304a08 sw $s0, 0x4a08($s1) ;  .bss+0x0 type=6
.text+0x5e0b4 file=0x5e0f4 02402021 move $a0, $s2
.text+0x5e0b8 file=0x5e0f8 1613fff8 bne $s0, $s3, 0x5e09c
.text+0x5e0bc file=0x5e0fc 00002821 move $a1, $zero
.text+0x5e0c0 file=0x5e100 8fbf002c lw $ra, 0x2c($sp)
.text+0x5e0c4 file=0x5e104 8fb60028 lw $s6, 0x28($sp)
.text+0x5e0c8 file=0x5e108 8fb50024 lw $s5, 0x24($sp)
.text+0x5e0cc file=0x5e10c 8fb40020 lw $s4, 0x20($sp)
.text+0x5e0d0 file=0x5e110 8fb3001c lw $s3, 0x1c($sp)
.text+0x5e0d4 file=0x5e114 8fb20018 lw $s2, 0x18($sp)
.text+0x5e0d8 file=0x5e118 8fb10014 lw $s1, 0x14($sp)
.text+0x5e0dc file=0x5e11c 8fb00010 lw $s0, 0x10($sp)
.text+0x5e0e0 file=0x5e120 03e00008 jr $ra
.text+0x5e0e4 file=0x5e124 27bd0030 addiu $sp, $sp, 0x30
.text+0x5e0e8 file=0x5e128 3c020000 lui $v0, 0 ;  .bss+0x0 type=5
.text+0x5e0ec file=0x5e12c 24454a18 addiu $a1, $v0, 0x4a18 ;  .bss+0x0 type=6
.text+0x5e0f0 file=0x5e130 8ca30020 lw $v1, 0x20($a1)
.text+0x5e0f4 file=0x5e134 14600004 bnez $v1, 0x5e108
.text+0x5e0f8 file=0x5e138 ac404a18 sw $zero, 0x4a18($v0) ;  .bss+0x0 type=6
.text+0x5e0fc file=0x5e13c 24020001 addiu $v0, $zero, 1