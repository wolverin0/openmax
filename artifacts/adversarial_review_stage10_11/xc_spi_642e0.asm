.text+0x642e0 file=0x64320 27bd0238 addiu $sp, $sp, 0x238
.text+0x642e4 file=0x64324 27bdffc0 addiu $sp, $sp, -0x40
.text+0x642e8 file=0x64328 00a7282b sltu $a1, $a1, $a3
.text+0x642ec file=0x6432c afb40028 sw $s4, 0x28($sp)
.text+0x642f0 file=0x64330 afb30024 sw $s3, 0x24($sp)
.text+0x642f4 file=0x64334 afb1001c sw $s1, 0x1c($sp)
.text+0x642f8 file=0x64338 afbf003c sw $ra, 0x3c($sp)
.text+0x642fc file=0x6433c afbe0038 sw $fp, 0x38($sp)
.text+0x64300 file=0x64340 afb70034 sw $s7, 0x34($sp)
.text+0x64304 file=0x64344 afb60030 sw $s6, 0x30($sp)
.text+0x64308 file=0x64348 afb5002c sw $s5, 0x2c($sp)
.text+0x6430c file=0x6434c afb20020 sw $s2, 0x20($sp)
.text+0x64310 file=0x64350 afb00018 sw $s0, 0x18($sp)
.text+0x64314 file=0x64354 00e08821 move $s1, $a3
.text+0x64318 file=0x64358 0080a021 move $s4, $a0
.text+0x6431c file=0x6435c 10a0003c beqz $a1, 0x64410
.text+0x64320 file=0x64360 00c09821 move $s3, $a2
.text+0x64324 file=0x64364 3c020000 lui $v0, 0 ;  .data+0x0 type=5
.text+0x64328 file=0x64368 8c430f28 lw $v1, 0xf28($v0) ;  .data+0x0 type=6
.text+0x6432c file=0x6436c 3c04fa1b lui $a0, 0xfa1b
.text+0x64330 file=0x64370 3484dbab ori $a0, $a0, 0xdbab
.text+0x64334 file=0x64374 3c065555 lui $a2, 0x5555
.text+0x64338 file=0x64378 00642021 addu $a0, $v1, $a0
.text+0x6433c file=0x6437c 24c65556 addiu $a2, $a2, 0x5556
.text+0x64340 file=0x64380 00860018 mult $a0, $a2
.text+0x64344 file=0x64384 000417c3 sra $v0, $a0, 0x1f
.text+0x64348 file=0x64388 3c04000f lui $a0, 0xf
.text+0x6434c file=0x6438c 27a50010 addiu $a1, $sp, 0x10
.text+0x64350 file=0x64390 3484ffdf ori $a0, $a0, 0xffdf
.text+0x64354 file=0x64394 00a42024 and $a0, $a1, $a0
.text+0x64358 file=0x64398 3c1705e4 lui $s7, 0x5e4
.text+0x6435c file=0x6439c 00042840 sll $a1, $a0, 1
.text+0x64360 file=0x643a0 00a42021 addu $a0, $a1, $a0
.text+0x64364 file=0x643a4 26e52455 addiu $a1, $s7, 0x2455
.text+0x64368 file=0x643a8 00852021 addu $a0, $a0, $a1
.text+0x6436c file=0x643ac 3c160000 lui $s6, 0 ;  .data+0x0 type=5
.text+0x64370 file=0x643b0 aec40f24 sw $a0, 0xf24($s6) ;  .data+0x0 type=6
.text+0x64374 file=0x643b4 3c150000 lui $s5, 0 ;  .bss+0x0 type=5
.text+0x64378 file=0x643b8 26b57a10 addiu $s5, $s5, 0x7a10 ;  .bss+0x0 type=6
.text+0x6437c file=0x643bc 26e5245e addiu $a1, $s7, 0x245e
.text+0x64380 file=0x643c0 00003010 mfhi $a2
.text+0x64384 file=0x643c4 00c21023 subu $v0, $a2, $v0
.text+0x64388 file=0x643c8 000220c0 sll $a0, $v0, 3
.text+0x6438c file=0x643cc 00023140 sll $a2, $v0, 5
.text+0x64390 file=0x643d0 00c42023 subu $a0, $a2, $a0
.text+0x64394 file=0x643d4 00821021 addu $v0, $a0, $v0
.text+0x64398 file=0x643d8 02a21021 addu $v0, $s5, $v0
.text+0x6439c file=0x643dc 90440005 lbu $a0, 5($v0)
.text+0x643a0 file=0x643e0 308400fe andi $a0, $a0, 0xfe
.text+0x643a4 file=0x643e4 1465001a bne $v1, $a1, 0x64410
.text+0x643a8 file=0x643e8 a0440005 sb $a0, 5($v0)
.text+0x643ac file=0x643ec 24100004 addiu $s0, $zero, 4
.text+0x643b0 file=0x643f0 24120001 addiu $s2, $zero, 1
.text+0x643b4 file=0x643f4 080190f8 j 0x643e0 ;  .text+0x0 type=4
.text+0x643b8 file=0x643f8 26f72c23 addiu $s7, $s7, 0x2c23
.text+0x643bc file=0x643fc 0c000000 jal 0 ; memcmp SHN_UNDEF+0x0 type=4
.text+0x643c0 file=0x64400 00000000 nop 
.text+0x643c4 file=0x64404 14400012 bnez $v0, 0x64410
.text+0x643c8 file=0x64408 00000000 nop 
.text+0x643cc file=0x6440c 1612000a bne $s0, $s2, 0x643f8
.text+0x643d0 file=0x64410 03c02021 move $a0, $fp
.text+0x643d4 file=0x64414 0c018f33 jal 0x63ccc ;  .text+0x0 type=4
.text+0x643d8 file=0x64418 aed70f24 sw $s7, 0xf24($s6) ;  .data+0x0 type=6
.text+0x643dc file=0x6441c 8fb00010 lw $s0, 0x10($sp)
.text+0x643e0 file=0x64420 001020c0 sll $a0, $s0, 3
.text+0x643e4 file=0x64424 00101140 sll $v0, $s0, 5
.text+0x643e8 file=0x64428 00442023 subu $a0, $v0, $a0
.text+0x643ec file=0x6442c 00902021 addu $a0, $a0, $s0
.text+0x643f0 file=0x64430 2484ffe7 addiu $a0, $a0, -0x19
.text+0x643f4 file=0x64434 02a42021 addu $a0, $s5, $a0
.text+0x643f8 file=0x64438 249effe7 addiu $fp, $a0, -0x19
.text+0x643fc file=0x6443c 2610ffff addiu $s0, $s0, -1
.text+0x64400 file=0x64440 03c02821 move $a1, $fp
.text+0x64404 file=0x64444 24060019 addiu $a2, $zero, 0x19
.text+0x64408 file=0x64448 1600ffec bnez $s0, 0x643bc
.text+0x6440c file=0x6444c afb00010 sw $s0, 0x10($sp)
.text+0x64410 file=0x64450 0c000000 jal 0 ; ath_flash_spi_down SHN_UNDEF+0x0 type=4
.text+0x64414 file=0x64454 00000000 nop 
.text+0x64418 file=0x64458 41706000 di $s0
.text+0x6441c file=0x6445c 32100001 andi $s0, $s0, 1
.text+0x64420 file=0x64460 000000c0 ehb 
.text+0x64424 file=0x64464 3c05bfff lui $a1, 0xbfff
.text+0x64428 file=0x64468 02802021 move $a0, $s4
.text+0x6442c file=0x6446c 02652821 addu $a1, $s3, $a1
.text+0x64430 file=0x64470 0c000000 jal 0 ; memcpy SHN_UNDEF+0x0 type=4
.text+0x64434 file=0x64474 02203021 move $a2, $s1
.text+0x64438 file=0x64478 12000002 beqz $s0, 0x64444
.text+0x6443c file=0x6447c 41606000 di 
.text+0x64440 file=0x64480 41606020 ei 
.text+0x64444 file=0x64484 000000c0 ehb 
.text+0x64448 file=0x64488 0c000000 jal 0 ; ath_flash_spi_up SHN_UNDEF+0x0 type=4
.text+0x6444c file=0x6448c 00000000 nop 
.text+0x64450 file=0x64490 8fbf003c lw $ra, 0x3c($sp)
.text+0x64454 file=0x64494 8fbe0038 lw $fp, 0x38($sp)
.text+0x64458 file=0x64498 8fb70034 lw $s7, 0x34($sp)
.text+0x6445c file=0x6449c 8fb60030 lw $s6, 0x30($sp)
.text+0x64460 file=0x644a0 8fb5002c lw $s5, 0x2c($sp)
.text+0x64464 file=0x644a4 8fb40028 lw $s4, 0x28($sp)
.text+0x64468 file=0x644a8 8fb30024 lw $s3, 0x24($sp)
.text+0x6446c file=0x644ac 8fb20020 lw $s2, 0x20($sp)
.text+0x64470 file=0x644b0 8fb1001c lw $s1, 0x1c($sp)
.text+0x64474 file=0x644b4 8fb00018 lw $s0, 0x18($sp)
.text+0x64478 file=0x644b8 03e00008 jr $ra
.text+0x6447c file=0x644bc 27bd0040 addiu $sp, $sp, 0x40
.text+0x64480 file=0x644c0 27bdffd8 addiu $sp, $sp, -0x28
.text+0x64484 file=0x644c4 27a40010 addiu $a0, $sp, 0x10
.text+0x64488 file=0x644c8 24050001 addiu $a1, $zero, 1
.text+0x6448c file=0x644cc 3406a000 ori $a2, $zero, 0xa000
.text+0x64490 file=0x644d0 24070001 addiu $a3, $zero, 1
.text+0x64494 file=0x644d4 afbf0024 sw $ra, 0x24($sp)
.text+0x64498 file=0x644d8 afb10020 sw $s1, 0x20($sp)
.text+0x6449c file=0x644dc afb0001c sw $s0, 0x1c($sp)
.text+0x644a0 file=0x644e0 0c0190b9 jal 0x642e4 ;  .text+0x0 type=4
.text+0x644a4 file=0x644e4 a3a00010 sb $zero, 0x10($sp)
.text+0x644a8 file=0x644e8 93b00010 lbu $s0, 0x10($sp)
.text+0x644ac file=0x644ec 27a40010 addiu $a0, $sp, 0x10
.text+0x644b0 file=0x644f0 24050001 addiu $a1, $zero, 1
.text+0x644b4 file=0x644f4 3406a001 ori $a2, $zero, 0xa001
.text+0x644b8 file=0x644f8 24070001 addiu $a3, $zero, 1
.text+0x644bc file=0x644fc 0c0190b9 jal 0x642e4 ;  .text+0x0 type=4