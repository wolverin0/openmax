.text+0xbbf40 file=0xbbf80 14430002 bne $v0, $v1, 0xbbf4c
.text+0xbbf44 file=0xbbf84 3c150002 lui $s5, 2
.text+0xbbf48 file=0xbbf88 a2e2e1f0 sb $v0, -0x1e10($s7)
.text+0xbbf4c file=0xbbf8c 0215a821 addu $s5, $s0, $s5
.text+0xbbf50 file=0xbbf90 8ea2e1c0 lw $v0, -0x1e40($s5)
.text+0xbbf54 file=0xbbf94 24030002 addiu $v1, $zero, 2
.text+0xbbf58 file=0xbbf98 3c050000 lui $a1, 0 ; $LC4 .rodata.str1.4+0x15890 type=5
.text+0xbbf5c file=0xbbf9c ac430094 sw $v1, 0x94($v0)
.text+0xbbf60 file=0xbbfa0 00002021 move $a0, $zero
.text+0xbbf64 file=0xbbfa4 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbf68 file=0xbbfa8 24a50000 addiu $a1, $a1, 0 ; $LC4 .rodata.str1.4+0x15890 type=6
.text+0xbbf6c file=0xbbfac 3c050000 lui $a1, 0 ; $LC5 .rodata.str1.4+0x15894 type=5
.text+0xbbf70 file=0xbbfb0 00002021 move $a0, $zero
.text+0xbbf74 file=0xbbfb4 24a50000 addiu $a1, $a1, 0 ; $LC5 .rodata.str1.4+0x15894 type=6
.text+0xbbf78 file=0xbbfb8 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbf7c file=0xbbfbc aea2e8c0 sw $v0, -0x1740($s5)
.text+0xbbf80 file=0xbbfc0 3c050000 lui $a1, 0 ; $LC6 .rodata.str1.4+0x15898 type=5
.text+0xbbf84 file=0xbbfc4 00002021 move $a0, $zero
.text+0xbbf88 file=0xbbfc8 24a50000 addiu $a1, $a1, 0 ; $LC6 .rodata.str1.4+0x15898 type=6
.text+0xbbf8c file=0xbbfcc 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbf90 file=0xbbfd0 a2a2e8c5 sb $v0, -0x173b($s5)
.text+0xbbf94 file=0xbbfd4 3c050000 lui $a1, 0 ; $LC7 .rodata.str1.4+0x158a0 type=5
.text+0xbbf98 file=0xbbfd8 00002021 move $a0, $zero
.text+0xbbf9c file=0xbbfdc 24a50000 addiu $a1, $a1, 0 ; $LC7 .rodata.str1.4+0x158a0 type=6
.text+0xbbfa0 file=0xbbfe0 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbfa4 file=0xbbfe4 a2a2e8c6 sb $v0, -0x173a($s5)
.text+0xbbfa8 file=0xbbfe8 3c050000 lui $a1, 0 ; $LC8 .rodata.str1.4+0x158a8 type=5
.text+0xbbfac file=0xbbfec 00002021 move $a0, $zero
.text+0xbbfb0 file=0xbbff0 24a50000 addiu $a1, $a1, 0 ; $LC8 .rodata.str1.4+0x158a8 type=6
.text+0xbbfb4 file=0xbbff4 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbfb8 file=0xbbff8 a2a2e8c7 sb $v0, -0x1739($s5)
.text+0xbbfbc file=0xbbffc 3c050000 lui $a1, 0 ; $LC9 .rodata.str1.4+0x158b0 type=5
.text+0xbbfc0 file=0xbc000 00002021 move $a0, $zero
.text+0xbbfc4 file=0xbc004 24a50000 addiu $a1, $a1, 0 ; $LC9 .rodata.str1.4+0x158b0 type=6
.text+0xbbfc8 file=0xbc008 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbfcc file=0xbc00c a2a2e8c8 sb $v0, -0x1738($s5)
.text+0xbbfd0 file=0xbc010 3c050000 lui $a1, 0 ; $LC10 .rodata.str1.4+0x158b8 type=5
.text+0xbbfd4 file=0xbc014 00002021 move $a0, $zero
.text+0xbbfd8 file=0xbc018 24a50000 addiu $a1, $a1, 0 ; $LC10 .rodata.str1.4+0x158b8 type=6
.text+0xbbfdc file=0xbc01c 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbfe0 file=0xbc020 a2a2e8c4 sb $v0, -0x173c($s5)
.text+0xbbfe4 file=0xbc024 0002102b sltu $v0, $zero, $v0
.text+0xbbfe8 file=0xbc028 3c050000 lui $a1, 0 ; $LC11 .rodata.str1.4+0x158c4 type=5
.text+0xbbfec file=0xbc02c 00002021 move $a0, $zero
.text+0xbbff0 file=0xbc030 24a50000 addiu $a1, $a1, 0 ; $LC11 .rodata.str1.4+0x158c4 type=6
.text+0xbbff4 file=0xbc034 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbbff8 file=0xbc038 a2a2e8cd sb $v0, -0x1733($s5)
.text+0xbbffc file=0xbc03c 0002102b sltu $v0, $zero, $v0
.text+0xbc000 file=0xbc040 3c050000 lui $a1, 0 ; $LC12 .rodata.str1.4+0x158d0 type=5
.text+0xbc004 file=0xbc044 00002021 move $a0, $zero
.text+0xbc008 file=0xbc048 24a50000 addiu $a1, $a1, 0 ; $LC12 .rodata.str1.4+0x158d0 type=6
.text+0xbc00c file=0xbc04c 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc010 file=0xbc050 a2a2e8cc sb $v0, -0x1734($s5)
.text+0xbc014 file=0xbc054 0002102b sltu $v0, $zero, $v0
.text+0xbc018 file=0xbc058 3c050000 lui $a1, 0 ; $LC13 .rodata.str1.4+0x158dc type=5
.text+0xbc01c file=0xbc05c 00002021 move $a0, $zero
.text+0xbc020 file=0xbc060 24a50000 addiu $a1, $a1, 0 ; $LC13 .rodata.str1.4+0x158dc type=6
.text+0xbc024 file=0xbc064 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc028 file=0xbc068 a2a2e8cb sb $v0, -0x1735($s5)
.text+0xbc02c file=0xbc06c 0002102b sltu $v0, $zero, $v0
.text+0xbc030 file=0xbc070 3c050000 lui $a1, 0 ; $LC14 .rodata.str1.4+0x158e8 type=5
.text+0xbc034 file=0xbc074 00002021 move $a0, $zero
.text+0xbc038 file=0xbc078 24a50000 addiu $a1, $a1, 0 ; $LC14 .rodata.str1.4+0x158e8 type=6
.text+0xbc03c file=0xbc07c 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc040 file=0xbc080 a2a2e8ce sb $v0, -0x1732($s5)
.text+0xbc044 file=0xbc084 0002102b sltu $v0, $zero, $v0
.text+0xbc048 file=0xbc088 3c050000 lui $a1, 0 ; $LC15 .rodata.str1.4+0x158f4 type=5
.text+0xbc04c file=0xbc08c 00002021 move $a0, $zero
.text+0xbc050 file=0xbc090 24a50000 addiu $a1, $a1, 0 ; $LC15 .rodata.str1.4+0x158f4 type=6
.text+0xbc054 file=0xbc094 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc058 file=0xbc098 a2a2e8cf sb $v0, -0x1731($s5)
.text+0xbc05c file=0xbc09c 0002102b sltu $v0, $zero, $v0
.text+0xbc060 file=0xbc0a0 3c050000 lui $a1, 0 ; $LC16 .rodata.str1.4+0x15904 type=5
.text+0xbc064 file=0xbc0a4 00002021 move $a0, $zero
.text+0xbc068 file=0xbc0a8 24a50000 addiu $a1, $a1, 0 ; $LC16 .rodata.str1.4+0x15904 type=6
.text+0xbc06c file=0xbc0ac 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc070 file=0xbc0b0 a2a2e8d0 sb $v0, -0x1730($s5)
.text+0xbc074 file=0xbc0b4 0002102b sltu $v0, $zero, $v0
.text+0xbc078 file=0xbc0b8 3c050000 lui $a1, 0 ; $LC17 .rodata.str1.4+0x1590c type=5
.text+0xbc07c file=0xbc0bc a2a2e8d1 sb $v0, -0x172f($s5)
.text+0xbc080 file=0xbc0c0 00002021 move $a0, $zero
.text+0xbc084 file=0xbc0c4 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc088 file=0xbc0c8 24a50000 addiu $a1, $a1, 0 ; $LC17 .rodata.str1.4+0x1590c type=6
.text+0xbc08c file=0xbc0cc 10400007 beqz $v0, 0xbc0ac
.text+0xbc090 file=0xbc0d0 00002021 move $a0, $zero
.text+0xbc094 file=0xbc0d4 3c050000 lui $a1, 0 ; $LC18 .rodata.str1.4+0x15918 type=5
.text+0xbc098 file=0xbc0d8 00002021 move $a0, $zero
.text+0xbc09c file=0xbc0dc 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc0a0 file=0xbc0e0 24a50000 addiu $a1, $a1, 0 ; $LC18 .rodata.str1.4+0x15918 type=6
.text+0xbc0a4 file=0xbc0e4 0802f031 j 0xbc0c4 ;  .text+0x0 type=4
.text+0xbc0a8 file=0xbc0e8 3c030002 lui $v1, 2
.text+0xbc0ac file=0xbc0ec 3c050000 lui $a1, 0 ; $LC19 .rodata.str1.4+0x15920 type=5
.text+0xbc0b0 file=0xbc0f0 0c000000 jal 0 ; ubnthal_get_radio_cap SHN_UNDEF+0x0 type=4
.text+0xbc0b4 file=0xbc0f4 24a50000 addiu $a1, $a1, 0 ; $LC19 .rodata.str1.4+0x15920 type=6
.text+0xbc0b8 file=0xbc0f8 1440fff7 bnez $v0, 0xbc098
.text+0xbc0bc file=0xbc0fc 3c050000 lui $a1, 0 ; $LC18 .rodata.str1.4+0x15918 type=5
.text+0xbc0c0 file=0xbc100 3c030002 lui $v1, 2
.text+0xbc0c4 file=0xbc104 02031821 addu $v1, $s0, $v1
.text+0xbc0c8 file=0xbc108 8c66e8c4 lw $a2, -0x173c($v1)
.text+0xbc0cc file=0xbc10c 3c040000 lui $a0, 0 ; is_ubnt_ptp .data+0x8b34 type=5
.text+0xbc0d0 file=0xbc110 90840003 lbu $a0, 3($a0) ; is_ubnt_ptp .data+0x8b34 type=6
.text+0xbc0d4 file=0xbc114 3c0500ff lui $a1, 0xff
.text+0xbc0d8 file=0xbc118 34a5ff00 ori $a1, $a1, 0xff00
.text+0xbc0dc file=0xbc11c 00c52824 and $a1, $a2, $a1
.text+0xbc0e0 file=0xbc120 ac62e8d4 sw $v0, -0x172c($v1)
.text+0xbc0e4 file=0xbc124 14a00003 bnez $a1, 0xbc0f4
.text+0xbc0e8 file=0xbc128 a064e882 sb $a0, -0x177e($v1)
.text+0xbc0ec file=0xbc12c 0802f041 j 0xbc104 ;  .text+0x0 type=4
.text+0xbc0f0 file=0xbc130 a060e882 sb $zero, -0x177e($v1)
.text+0xbc0f4 file=0xbc134 10800004 beqz $a0, 0xbc108
.text+0xbc0f8 file=0xbc138 3c020000 lui $v0, 0 ; host_80211_enable .data+0x8b38 type=5
.text+0xbc0fc file=0xbc13c 0802f046 j 0xbc118 ;  .text+0x0 type=4
.text+0xbc100 file=0xbc140 00001821 move $v1, $zero
.text+0xbc104 file=0xbc144 3c020000 lui $v0, 0 ; host_80211_enable .data+0x8b38 type=5
.text+0xbc108 file=0xbc148 8c420000 lw $v0, ($v0) ; host_80211_enable .data+0x8b38 type=6
.text+0xbc10c file=0xbc14c 1040fffb beqz $v0, 0xbc0fc
.text+0xbc110 file=0xbc150 00000000 nop 
.text+0xbc114 file=0xbc154 24030001 addiu $v1, $zero, 1
.text+0xbc118 file=0xbc158 3c040000 lui $a0, 0 ; tgdeb .bss+0x1bca4 type=5
.text+0xbc11c file=0xbc15c 8c880000 lw $t0, ($a0) ; tgdeb .bss+0x1bca4 type=6
.text+0xbc120 file=0xbc160 3c040000 lui $a0, 0 ; vow_config .bss+0x1bc9c type=5
.text+0xbc124 file=0xbc164 8c870000 lw $a3, ($a0) ; vow_config .bss+0x1bc9c type=6
.text+0xbc128 file=0xbc168 3c040000 lui $a0, 0 ; max_peers .bss+0x1bc98 type=5
.text+0xbc12c file=0xbc16c 8c860000 lw $a2, ($a0) ; max_peers .bss+0x1bc98 type=6
.text+0xbc130 file=0xbc170 3c020002 lui $v0, 2
.text+0xbc134 file=0xbc174 3c040000 lui $a0, 0 ; max_vdevs .bss+0x1bc94 type=5
.text+0xbc138 file=0xbc178 02021021 addu $v0, $s0, $v0
.text+0xbc13c file=0xbc17c 8c850000 lw $a1, ($a0) ; max_vdevs .bss+0x1bc94 type=6