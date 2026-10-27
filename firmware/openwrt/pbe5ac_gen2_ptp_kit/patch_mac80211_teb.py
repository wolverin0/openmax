#!/usr/bin/env python3
"""
Deterministic OpenWrt 24.10.4 (Linux 6.6.110, ath79/generic MIPS32 BE)
mac80211.ko ETH_P_TEB (0x6558) decapsulation patcher (FMX-DISC-36),
4-address EAPOL-Key 2/4 RX_DROP_MONITOR bypass patcher (FMX-DISC-38 / Stage 122A),
and MAC80211 v3 WLAN_STA_AUTHORIZED-Gated 4-Address AP_VLAN Trigger (FMX-DISC-41 / Stage 131A).

Key Linux 6.6.110 ABI invariants (FMX-DISC-36, FMX-DISC-38 & FMX-DISC-41):
  1. .gnu.linkonce.this_module (module_layout) size = 352 bytes (0x160).
  2. struct sk_buff->data sits at offset 0xa8 (lw/sw $t1, 0xa8($a2)) on Linux 6.6.110
     (shifted +4 bytes vs 0xa4 on earlier builds).
  3. 21-instruction in-place patch at .text + 0x033c18..0x033c68 (file offset 0x033c88..0x033cdb,
     212104..212187) inside ieee80211_rx_mesh_check / ieee80211_data_to_8023_exthdr strips the
     14-byte inner 0x6558 (ETH_P_TEB) header emitted by stock airOS 8 4-address WDS peers.
  4. At file offset 0x03757c..0x0375b8 (.text + 0x03750c..0x037548), unexpected 4-address frames
     (FC=0x8803 ToDS=1,FromDS=1 such as stock airOS 8 EAPOL-Key 2/4 arriving at T+1.05ms before
     hostapd spawns phy*-ap0.sta1 AP_VLAN) hit ieee80211_rx_h_data:
       - Preserve-4addr-Event + Bypass-Drop variant (mac80211_teb_4addr_6.6.110.ko):
           * Keeps test_and_set_bit(WLAN_STA_4ADDR_EVENT) and jal cfg80211_rx_unexpected_4addr_frame
             at 0x0375ac so hostapd receives NL80211_CMD_UNEXPECTED_4ADDR_FRAME.
           * Patches 0x037598: 0x14400006 (bnez $v0, 0x375b4), 0x0375b4: 0x1000f91c (b 0x35a28),
             0x0375b8: 0x24070004 (addiu $a3, $zero, 4 = NL80211_IFTYPE_AP_VLAN), bypassing
             RX_DROP_MONITOR (0x20000) and delivering EAPOL-Key 2/4 & 4/4 immediately to hostapd.
       - Direct-Branch variant at 0x03757c (mac80211_teb_4addr_direct_6.6.110.ko):
           * Patches 0x03757c: 0x1000f92a (b 0x35a28) and 0x037580: 0x24070004 (addiu $a3, $zero, 4).
       - Authorized-Gated v3 variant at 0x037580..0x0375b8 (mac80211_teb_4addr_v3_6.6.110.ko, FMX-DISC-41):
           * Because stock airOS 8 (WA.v8.7.11) sends EAPOL-Key 2/4 as a 4-address frame (FC=0x8803) at
             T+1.05ms while WLAN_STA_AUTHORIZED (BIT(3) = 0x08 in rx->sta->_flags at 0x74($v0)) is still 0,
             hostapd (hostapd_notif_unexpected_4addr_frame) ignores NL80211_CMD_UNEXPECTED_4ADDR_FRAME when
             !(sta->flags & WLAN_STA_AUTHORIZED), and setting WLAN_STA_4ADDR_EVENT (BIT(19) = 0x80000)
             prematurely during EAPOL-Key 2/4 prevents cfg80211_rx_unexpected_4addr_frame from firing after
             EAPOL-Key 4/4 authorizes the station.
           * v3 tests BIT(3) (andi $a0, $v1, 0x0008; beqz $a0, 0x375b4) before the LL/SC on BIT(19):
             while !WLAN_STA_AUTHORIZED, 4-address EAPOL frames bypass LL/SC and jump via 0x0375b4 -> 0x035a28
             ($a3 = 4) without setting BIT(19); once WLAN_STA_AUTHORIZED == 1, the first post-auth 4-address
             frame atomically sets BIT(19), calls cfg80211_rx_unexpected_4addr_frame (0x0375ac, preserving
             .rel.text R_MIPS_26 at .text+0x03753c) so hostapd creates/bridges phy*-ap0.sta1 (AP_VLAN), and
             still delivers the frame via 0x0375b4 -> 0x035a28 ($a3 = 4).
"""

from __future__ import annotations

import hashlib
import pathlib
import struct
from elftools.elf.elffile import ELFFile


KIT_DIR = pathlib.Path(__file__).resolve().parent
ROM_KO = KIT_DIR / "mac80211_rom_241.ko"
TEB_KO = KIT_DIR / "mac80211_teb_6.6.110.ko"
TEB_4ADDR_KO = KIT_DIR / "mac80211_teb_4addr_6.6.110.ko"
TEB_4ADDR_DIRECT_KO = KIT_DIR / "mac80211_teb_4addr_direct_6.6.110.ko"
TEB_4ADDR_V3_KO = KIT_DIR / "mac80211_teb_4addr_v3_6.6.110.ko"
TEB_241_V3_KO = KIT_DIR / "mac80211_241_v3.ko"

EXPECTED_ROM_SHA256 = "8566fb1c104b61bdb645fc17ba28d6c0ea1bd738e2d05dc8a935464d872a1ce5"
EXPECTED_TEB_SHA256 = "3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868"
EXPECTED_TEB_4ADDR_V2_SHA256 = "c65dc2e2a87274e3073debf4c507606422a5ea1b08cbfe2e40beed58263e81cc"
EXPECTED_TEB_241_V3_SHA256 = "e43115c06316ce2d1b643d1900deb41839f7e07aba50f1537e6ed7a17b45e2f5"
EXPECTED_MODULE_LAYOUT_BYTES = 352
SKB_DATA_OFFSET_6_6_110 = 0xA8


def beq(rs: int, rt: int, pc: int, target: int) -> int:
    off = ((target - (pc + 4)) >> 2) & 0xFFFF
    return (0x04 << 26) | (rs << 21) | (rt << 16) | off


def bne(rs: int, rt: int, pc: int, target: int) -> int:
    off = ((target - (pc + 4)) >> 2) & 0xFFFF
    return (0x05 << 26) | (rs << 21) | (rt << 16) | off


def build_teb_patch_instructions() -> list[tuple[int, int]]:
    """Return the 21 MIPS32 BE instructions at .text + 0x033c18..0x033c68 (file 0x033c88..0x033cd8)."""
    return [
        (0x033C18, beq(6, 0, 0x033C18, 0x033C6C)),       # beqz $a2, 0x33c6c
        (0x033C1C, 0xAFA00064 | (17 << 16)),             # sw $s1, 0x64($sp)
        (0x033C20, 0x8CC80054),                          # lw $t0, 0x54($a2)  [skb->len]
        (0x033C24, 0x8CC90058),                          # lw $t1, 0x58($a2)  [skb->data_len]
        (0x033C28, 0x01094823),                          # subu $t1, $t0, $t1 [skb_headlen]
        (0x033C2C, 0x2D2A001C),                          # sltiu $t2, $t1, 0x1c (28B)
        (0x033C30, bne(10, 0, 0x033C30, 0x033C6C)),      # bnez $t2, 0x33c6c
        (0x033C34, 0x8CC90000 | SKB_DATA_OFFSET_6_6_110),# lw $t1, 0xa8($a2)  [skb->data on 6.6.110]
        (0x033C38, 0x912A000C),                          # lbu $t2, 0xc($t1)
        (0x033C3C, 0x912B000D),                          # lbu $t3, 0xd($t1)
        (0x033C40, 0x000A5200),                          # sll $t2, $t2, 8
        (0x033C44, 0x014B5025),                          # or $t2, $t2, $t3
        (0x033C48, 0x394A6558),                          # xori $t2, $t2, 0x6558 (ETH_P_TEB)
        (0x033C4C, bne(10, 0, 0x033C4C, 0x033C6C)),      # bnez $t2, 0x33c6c
        (0x033C50, 0x2508FFF2),                          # addiu $t0, $t0, -14
        (0x033C54, 0x2529000E),                          # addiu $t1, $t1, 14
        (0x033C58, 0xACC80054),                          # sw $t0, 0x54($a2)
        (0x033C5C, 0xACC90000 | SKB_DATA_OFFSET_6_6_110),# sw $t1, 0xa8($a2)  [skb->data on 6.6.110]
        (0x033C60, 0x90CA0064),                          # lbu $t2, 0x64($a2)
        (0x033C64, 0x7C0A1044),                          # ins $t2, $zero, 1, 2
        (0x033C68, 0xA0CA0064),                          # sb $t2, 0x64($a2)
    ]


def build_4addr_preserve_event_patch_file_offsets() -> list[tuple[int, int]]:
    """
    Preserve cfg80211_rx_unexpected_4addr_frame at 0x0375ac while bypassing RX_DROP_MONITOR
    at 0x037598 and 0x0375b4..0x0375b8, setting $a3 = 4 (NL80211_IFTYPE_AP_VLAN) and jumping to 0x035a28.
    """
    return [
        (0x037598, 0x14400006),  # bnez $v0, 0x375b4 (if 4ADDR_EVENT already sent, still deliver frame)
        (0x0375B4, 0x1000F91C),  # b 0x35a28 (bypass RX_DROP_MONITOR after cfg80211_rx_unexpected_4addr_frame)
        (0x0375B8, 0x24070004),  # addiu $a3, $zero, 4 (set iftype = NL80211_IFTYPE_AP_VLAN for __ieee80211_data_to_8023)
    ]


def build_4addr_direct_0x3757c_patch_file_offsets() -> list[tuple[int, int]]:
    """
    Direct branch at file offset 0x03757c..0x037580 to 0x035a28 with $a3 = 4.
    """
    return [
        (0x03757C, 0x1000F92A),  # b 0x35a28
        (0x037580, 0x24070004),  # addiu $a3, $zero, 4
    ]


def build_4addr_v3_authorized_gated_patch_file_offsets() -> list[tuple[int, int]]:
    """
    MAC80211 v3 Authorized-Gated 4-Address AP_VLAN Trigger (FMX-DISC-41) at file offset 0x037580..0x0375b8
    (.text + 0x037510..0x037548, leaving 0x03757c ll $v1, 0x74($v0), 0x0375a8 lw $a0, 0x44c($v0), and
    0x0375ac jal cfg80211_rx_unexpected_4addr_frame + .rel.text R_MIPS_26 at .text+0x03753c intact):
      - If !(rx->sta->_flags & BIT(3) [WLAN_STA_AUTHORIZED]), jump directly to 0x0375b4 -> 0x035a28 ($a3 = 4)
        to deliver 4-address EAPOL-Key 2/4 & 4/4 to hostapd WITHOUT setting BIT(19) (WLAN_STA_4ADDR_EVENT).
      - Once WLAN_STA_AUTHORIZED == 1, atomically test_and_set_bit(BIT(19), &rx->sta->_flags), invoke
        cfg80211_rx_unexpected_4addr_frame(rx->sdata->dev, rx->sta->sta.addr, GFP_ATOMIC) at 0x0375ac so
        hostapd creates and bridges phy*-ap0.sta1 (AP_VLAN), and deliver the frame via 0x0375b4 -> 0x035a28.
    """
    return [
        (0x037580, 0x30640008),  # andi $a0, $v1, 0x0008 (test BIT(3) = WLAN_STA_AUTHORIZED)
        (0x037584, 0x1080000B),  # beqz $a0, 0x375b4 (if !AUTHORIZED, deliver EAPOL without setting BIT(19))
        (0x037588, 0x3C010008),  # lui $at, 0x0008 (delay slot: $at = BIT(19) = WLAN_STA_4ADDR_EVENT)
        (0x03758C, 0x00612025),  # or $a0, $v1, $at ($a0 = _flags | BIT(19))
        (0x037590, 0xE0440074),  # sc $a0, 0x74($v0) (atomic store-conditional to rx->sta->_flags)
        (0x037594, 0x1080FFF9),  # beqz $a0, 0x3757c (retry LL/SC at 0x3757c if failed)
        (0x037598, 0x7C6304C0),  # ext $v1, $v1, 19, 1 (delay slot: extract old BIT(19))
        (0x03759C, 0x14600005),  # bnez $v1, 0x375b4 (if BIT(19) already set, skip netlink call and deliver)
        (0x0375A0, 0x2445076C),  # addiu $a1, $v0, 0x76c (delay slot: $a1 = &rx->sta->sta.addr)
        (0x0375A4, 0x8E22000C),  # lw $v0, 0x0c($s1) ($v0 = rx->sdata; 0x0375a8 lw $a0, 0x44c($v0) unchanged)
        # 0x0375a8: 0x8c44044c (lw $a0, 0x44c($v0) = rx->sdata->dev, unchanged)
        # 0x0375ac: 0x0c000000 (jal cfg80211_rx_unexpected_4addr_frame, .rel.text @ .text+0x03753c unchanged)
        (0x0375B0, 0x24060820),  # li $a2, 0x820 (delay slot: $a2 = GFP_ATOMIC)
        (0x0375B4, 0x1000F91C),  # b 0x35a28 (bypass RX_DROP_MONITOR and deliver via __ieee80211_data_to_8023)
        (0x0375B8, 0x24070004),  # addiu $a3, $zero, 4 (delay slot: $a3 = NL80211_IFTYPE_AP_VLAN)
    ]


def build_4addr_241_v3_patch_file_offsets() -> list[tuple[int, int]]:
    """
    Live .241 v3 WLAN_STA_AUTHORIZED-gated 4-address patch (mac80211_241_v3.ko,
    SHA-256: e43115c06316ce2d1b643d1900deb41839f7e07aba50f1537e6ed7a17b45e2f5):
    Gates cfg80211_rx_unexpected_4addr_frame on WLAN_STA_AUTHORIZED (sta->_flags & 8) at 0x037578..0x0375b8
    so the 4-way handshake completes on phy*-ap0 before phy*-ap0.sta1 is spawned.
    """
    return [
        (0x037578, 0x24070004),  # addiu $a3, $zero, 4
        (0x03757C, 0x8C430074),  # lw $v1, 0x74($v0)
        (0x037580, 0x30640008),  # andi $a0, $v1, 8 (WLAN_STA_AUTHORIZED)
        (0x037584, 0x1080F928),  # beqz $a0, 0x35a28
        (0x037588, 0x3C010008),  # lui $at, 8 (WLAN_STA_4ADDR_EVENT)
        (0x03758C, 0x00612024),  # and $a0, $v1, $at
        (0x037590, 0x1480F925),  # bnez $a0, 0x35a28
        (0x037594, 0x00611825),  # or $v1, $v1, $at
        (0x037598, 0xAC430074),  # sw $v1, 0x74($v0)
        (0x0375B4, 0x1000F91C),  # b 0x35a28
        (0x0375B8, 0x24070004),  # addiu $a3, $zero, 4
    ]


def apply_and_verify_teb_patch(
    rom_path: pathlib.Path = ROM_KO,
    out_path: pathlib.Path = TEB_KO,
    write_4addr_variants: bool = True,
) -> dict:
    raw_rom = rom_path.read_bytes()
    rom_sha256 = hashlib.sha256(raw_rom).hexdigest()
    with rom_path.open("rb") as f:
        elf = ELFFile(f)
        text = elf.get_section_by_name(".text")
        text_file_offset = int(text["sh_offset"])
        this_mod = elf.get_section_by_name(".gnu.linkonce.this_module")
        module_layout_size = int(this_mod["sh_size"])
        rel_sec = elf.get_section_by_name(".rel.text")
        rel_375ac_found = False
        for rel in rel_sec.iter_relocations():
            if 0x033BEC <= rel["r_offset"] <= 0x033C9C:
                raise RuntimeError(f"Unexpected relocation at 0x{rel['r_offset']:06x}")
            if rel["r_offset"] == 0x03753C:
                rel_375ac_found = True
        if not rel_375ac_found:
            raise RuntimeError("Expected R_MIPS_26 relocation at .text+0x03753c (file 0x0375ac) not found")

    # 1. Standard ETH_P_TEB (0x6558) patched image (mac80211_teb_6.6.110.ko)
    raw_teb = bytearray(raw_rom)
    insns = build_teb_patch_instructions()
    for text_addr, word in insns:
        struct.pack_into(">I", raw_teb, text_file_offset + text_addr, word)
    patched_sha256 = hashlib.sha256(raw_teb).hexdigest()

    rx_drop_site_words = [
        struct.unpack_from(">I", raw_teb, file_off)[0]
        for file_off in (0x0375AC, 0x0375B0, 0x0375B4, 0x0375B8)
    ]

    # 2. ETH_P_TEB + 4-addr EAPOL RX_DROP_MONITOR bypass preserving cfg80211_rx_unexpected_4addr_frame (v2)
    raw_teb_4addr = bytearray(raw_teb)
    for file_off, word in build_4addr_preserve_event_patch_file_offsets():
        struct.pack_into(">I", raw_teb_4addr, file_off, word)
    teb_4addr_sha256 = hashlib.sha256(raw_teb_4addr).hexdigest()

    # 3. ETH_P_TEB + direct 0x3757c -> 0x35a28 branch
    raw_teb_4addr_direct = bytearray(raw_teb)
    for file_off, word in build_4addr_direct_0x3757c_patch_file_offsets():
        struct.pack_into(">I", raw_teb_4addr_direct, file_off, word)
    teb_4addr_direct_sha256 = hashlib.sha256(raw_teb_4addr_direct).hexdigest()

    # 4. ETH_P_TEB + MAC80211 v3 WLAN_STA_AUTHORIZED-Gated 4-Address AP_VLAN Trigger (FMX-DISC-41)
    raw_teb_4addr_v3 = bytearray(raw_teb)
    for file_off, word in build_4addr_v3_authorized_gated_patch_file_offsets():
        struct.pack_into(">I", raw_teb_4addr_v3, file_off, word)
    teb_4addr_v3_sha256 = hashlib.sha256(raw_teb_4addr_v3).hexdigest()

    # 5. ETH_P_TEB + mac80211_241_v3.ko (e43115c06316ce2d1b643d1900deb41839f7e07aba50f1537e6ed7a17b45e2f5)
    raw_teb_241_v3 = bytearray(raw_teb)
    for file_off, word in build_4addr_241_v3_patch_file_offsets():
        struct.pack_into(">I", raw_teb_241_v3, file_off, word)
    teb_241_v3_sha256 = hashlib.sha256(raw_teb_241_v3).hexdigest()

    if write_4addr_variants:
        TEB_4ADDR_KO.write_bytes(bytes(raw_teb_4addr))
        TEB_4ADDR_DIRECT_KO.write_bytes(bytes(raw_teb_4addr_direct))
        TEB_4ADDR_V3_KO.write_bytes(bytes(raw_teb_4addr_v3))
        TEB_241_V3_KO.write_bytes(bytes(raw_teb_241_v3))

    return {
        "rom_sha256": rom_sha256,
        "patched_sha256": patched_sha256,
        "matches_expected_teb_sha256": patched_sha256 == EXPECTED_TEB_SHA256,
        "teb_4addr_preserve_event_sha256": teb_4addr_sha256,
        "matches_expected_teb_4addr_v2_sha256": teb_4addr_sha256 == EXPECTED_TEB_4ADDR_V2_SHA256,
        "teb_4addr_direct_0x3757c_sha256": teb_4addr_direct_sha256,
        "teb_4addr_v3_authorized_gated_sha256": teb_4addr_v3_sha256,
        "teb_241_v3_sha256": teb_241_v3_sha256,
        "matches_expected_teb_241_v3_sha256": teb_241_v3_sha256 == EXPECTED_TEB_241_V3_SHA256,
        "text_file_offset": text_file_offset,
        "patch_file_offset_start": text_file_offset + 0x033C18,
        "patch_file_offset_end": text_file_offset + 0x033C6C,
        "module_layout_size_bytes": module_layout_size,
        "skb_data_offset_hex": hex(SKB_DATA_OFFSET_6_6_110),
        "rx_drop_monitor_4addr_words_hex": [f"0x{w:08x}" for w in rx_drop_site_words],
        "rx_4addr_preserve_event_patched_words_hex": {
            f"0x{file_off:06x}": f"0x{word:08x}"
            for file_off, word in build_4addr_preserve_event_patch_file_offsets()
        },
        "rx_4addr_direct_0x3757c_patched_words_hex": {
            f"0x{file_off:06x}": f"0x{word:08x}"
            for file_off, word in build_4addr_direct_0x3757c_patch_file_offsets()
        },
        "rx_4addr_v3_authorized_gated_patched_words_hex": {
            f"0x{file_off:06x}": f"0x{word:08x}"
            for file_off, word in build_4addr_v3_authorized_gated_patch_file_offsets()
        },
        "rx_4addr_241_v3_patched_words_hex": {
            f"0x{file_off:06x}": f"0x{word:08x}"
            for file_off, word in build_4addr_241_v3_patch_file_offsets()
        },
    }


if __name__ == "__main__":
    import json
    summary = apply_and_verify_teb_patch()
    print(json.dumps(summary, indent=2))
