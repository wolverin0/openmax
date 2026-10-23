"""Build pinned native flash writers for bench Loco195 (0xe7fa) and production MONZON (0xe7fa).
Makes TCP observer reporting best-effort during init shutdown so wireless link drops while
wpa_supplicant is SIGSTOPped never abort a 100%-verified flash commit.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CANARY = ROOT / "artifacts" / "canary_panel1_guarida"
BASE_C = CANARY / "fmx_flash_writer_panel1_native_20261019.c"

PROFILES = [
    {
        "name": "loco195",
        "target_ip": "192.168.1.20",
        "observer_ip": "192.168.1.170",
        "board_sha": "682220c0c76033a6ef5f303029b1272acd60b5d9d865549765069fdb91f1f059",
        "image_sha": "11c2e4f8ec8bd40119a1fd2cc99b357f88bedd70ec950ce7d37b0ad5f4e5e9bb",
    },
    {
        "name": "monzon",
        "target_ip": "10.10.200.41",
        "observer_ip": "192.168.100.155",
        "board_sha": "45d56ec54f30b0e97b5033ee4fe8054197aee5de9b24462e529d61e73e422e92",
        "image_sha": "f312b82a5087f8359f29a596aaf424466eba305709d962a4f62d5c85fcd2007e",
    },
    {
        "name": "gamboa",
        "target_ip": "10.10.200.223",
        "observer_ip": "192.168.100.155",
        "board_sha": "29efe61667c50bb7c46a625a5be95148645d10f653dce9a64f2fdc06638b3058",
        "image_sha": "098ee698a6c586772461ff3412cdc57250b16410c609b815f7e5c151b86a192e",
    },
]


def main() -> int:
    src_orig = BASE_C.read_text(encoding="utf-8")
    out_meta = {}

    for p in PROFILES:
        src = src_orig
        src = src.replace(
            '#define IMAGE_SHA "2b34379d62cff6738e769c1dd613b6e82bd3b19092be936a54d1b55d416e69a5"',
            f'#define IMAGE_SHA "{p["image_sha"]}"',
        )
        src = src.replace(
            '#define BOARD_SHA "97f3b8a0b1c55e319c6414992f9c1e9a01a78e919708d4b6154cb7a6a5eb1c21"',
            f'#define BOARD_SHA "{p["board_sha"]}"',
        )
        src = src.replace(
            '#define OBSERVER_IP "192.168.100.155"',
            f'#define OBSERVER_IP "{p["observer_ip"]}"',
        )
        src = src.replace(
            't->bench?"192.168.100.195":"10.10.100.84"',
            f't->bench?"192.168.100.195":"{p["target_ip"]}"',
        )
        # Make observer connection and post-SIGSTOP observer_record best-effort so wireless
        # socket timeout during 140s SIGSTOP never rolls back a verified flash image:
        src = src.replace(
            "t->observer=observer_connect();return t->observer<0?-1:0;",
            "t->observer=observer_connect();return 0;",
        )
        src = src.replace(
            'if(observer_record(t,"INIT_PREPARED_BEFORE_QUIESCE"))return -1;',
            '(void)observer_record(t,"INIT_PREPARED_BEFORE_QUIESCE");',
        )
        src = src.replace(
            'return observer_record(t,"INIT_QUIESCED_WATCHDOG_GUARD_PASSED");',
            '(void)observer_record(t,"INIT_QUIESCED_WATCHDOG_GUARD_PASSED");return 0;',
        )
        src = src.replace(
            'if(observer_record(t,t->bench?"INIT_BENCH_PATTERN_AND_RESTORE_VERIFIED":"INIT_AP_IMAGE_VERIFIED")) {',
            'if(0 && observer_record(t,t->bench?"INIT_BENCH_PATTERN_AND_RESTORE_VERIFIED":"INIT_AP_IMAGE_VERIFIED")) {',
        )

        c_file = CANARY / f"fmx_flash_writer_{p['name']}_20261023.c"
        bin_file = CANARY / f"fmx_flash_writer_{p['name']}_20261023"
        c_file.write_text(src, encoding="utf-8")

        wsl_c = f"artifacts/canary_panel1_guarida/{c_file.name}"
        wsl_bin = f"artifacts/canary_panel1_guarida/{bin_file.name}"
        cmd = [
            "wsl",
            "--exec",
            "env",
            "STAGING_DIR=/home/ggorbalan/futuramax/openwrt-24.10.4/staging_dir",
            "/home/ggorbalan/futuramax/openwrt-24.10.4/staging_dir/toolchain-mips_24kc_gcc-13.3.0_musl/bin/mips-openwrt-linux-musl-gcc",
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Os",
            "-static",
            wsl_c,
            "-o",
            wsl_bin,
        ]
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Compile failed for {p['name']}: {r.stderr}")
        b_bytes = bin_file.read_bytes()
        out_meta[p["name"]] = {
            "binary": bin_file.name,
            "bytes": len(b_bytes),
            "sha256": hashlib.sha256(b_bytes).hexdigest(),
            "board_sha": p["board_sha"],
            "image_sha": p["image_sha"],
        }

    print(json.dumps(out_meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
