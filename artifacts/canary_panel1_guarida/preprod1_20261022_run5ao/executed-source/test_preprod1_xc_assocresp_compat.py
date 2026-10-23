"""Offline synthetic msg3 fixtures; never accesses a device or captured frame.

Execute the C encoder under ASAN/UBSAN using the existing Ubuntu gcc/OpenSSL.
Python HMAC/AES independently decodes its output and checks the public schema.
"""
import hashlib
import hmac
import json
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest
from Crypto.Cipher import AES


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "tools/bench/hostapd_preprod1_xc_assocresp.h"
SCHEMA = ROOT / "artifacts/canary_panel1_guarida/preprod1_r5al_response_wire_schema_20261023.json"
SCHEMA_SHA = "8c792db3ed8a71cd50c055e105091f849c22c77f700f9ea3fa52a0e9f1d311ca"
AP = bytes.fromhex("18e8297455a2")
XC = bytes.fromhex("b4fbe45cd5d2")


def decode_consumer_model(wire, ap=AP, xc=XC):
    """Only the identified msg3 fields; not a target driver or WPA model."""
    assert len(wire) == 44 and wire[:10] == bytes.fromhex("dd2a002722ffffff0203")
    assert int.from_bytes(wire[10:12], "big") == 32
    key = hmac.new(xc, ap, hashlib.sha1).digest()[:16]
    plain = AES.new(key, AES.MODE_ECB).decrypt(wire[12:])
    assert plain[:2] == b"\x00\x09" and plain[2:8] == ap
    assert plain[8:10] == b"\x03\x03"
    assert plain[16:19] == b"\x03\x00\x00"  # Empty TLV3 then power metadata.
    assert plain[19:] == bytes(13)
    # A zero-length TLV permits an empty bounded slice, no firmware dereference.
    assert plain[18:18 + plain[17]] == b""
    return plain


WRAPPER = r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <openssl/aes.h>
#include <openssl/hmac.h>
typedef uint8_t u8;
#define os_memcmp memcmp
#define os_memcpy memcpy
#define WPA_PUT_BE16(p,v) do { (p)[0] = (u8)((v) >> 8); (p)[1] = (u8)(v); } while (0)
static int fault, encrypt_calls, deinit_calls, erased;
static void forced_memzero(void *p, size_t n) {
    volatile u8 *v = p; erased += (int)n; while (n--) *v++ = 0;
}
static int hmac_sha1(const u8 *key, size_t kl, const u8 *data, size_t dl, u8 *out) {
    unsigned n = 0;
    if (fault == 1) { memset(out, 0x71, 20); return -1; }
    return HMAC(EVP_sha1(), key, (int)kl, data, dl, out, &n) && n == 20 ? 0 : -1;
}
static void *aes_encrypt_init(const u8 *key, size_t n) {
    AES_KEY *ctx;
    if (fault == 2) return NULL;
    ctx = malloc(sizeof(*ctx));
    if (!ctx) return NULL;
    if (n != 16 || AES_set_encrypt_key(key, 128, ctx)) { free(ctx); return NULL; }
    return ctx;
}
static int aes_encrypt(void *ctx, const u8 *in, u8 *out) {
    encrypt_calls++;
    if (fault == encrypt_calls + 2) { memset(out, 0x72, 16); return -1; }
    AES_encrypt(in, out, ctx); return 0;
}
static void aes_encrypt_deinit(void *ctx) {
    deinit_calls++; memset(ctx, 0, sizeof(AES_KEY)); free(ctx);
}
'''

MAIN = r'''
static int unhex(const char *s, u8 *b, size_t n) {
    unsigned v;
    if (strlen(s) != n * 2) return -1;
    for (size_t i = 0; i < n; i++) {
        if (sscanf(s + i * 2, "%2x", &v) != 1) return -1;
        b[i] = (u8)v;
    }
    return 0;
}
int main(void) {
    char line[256], ah[13], xh[13], nh[9], rh[5];
    int cap, null_arg;
    while (fgets(line, sizeof(line), stdin)) {
        u8 ap[6], xc[6], nonce[4], rssi[2], storage[66];
        int result;
        if (sscanf(line, "%d %d %d %12s %12s %8s %4s", &cap, &fault,
                   &null_arg, ah, xh, nh, rh) != 7) return 3;
        if (cap < 0 || cap > 64 || unhex(ah, ap, 6) || unhex(xh, xc, 6) ||
            unhex(nh, nonce, 4) || unhex(rh, rssi, 2)) return 4;
        memset(storage, 0xa5, sizeof(storage));
        encrypt_calls = deinit_calls = erased = 0;
        result = fmx_preprod1_xc_assocresp(null_arg == 1 ? NULL : storage + 1, cap,
                    null_arg == 2 ? NULL : ap, null_arg == 3 ? NULL : xc,
                    null_arg == 4 ? NULL : nonce, null_arg == 5 ? NULL : rssi);
        if (storage[0] != 0xa5 || storage[65] != 0xa5) return 5;
        printf("%d %d %d %d ", result, encrypt_calls, deinit_calls, erased);
        for (size_t i = 0; i < sizeof(storage); i++) printf("%02x", storage[i]);
        puts("");
    }
    return 0;
}
'''


def test_native_c_encoder_exact_wire_and_failure_atomicity():
    assert hashlib.sha256(SCHEMA.read_bytes()).hexdigest() == SCHEMA_SHA
    base = Path(r"\\wsl.localhost\Ubuntu\home\ggorbalan\futuramax")
    if not shutil.which("wsl.exe") or not base.is_dir():
        pytest.skip("Requires existing Ubuntu gcc/OpenSSL, no installation attempted")
    token = "fmx-xc-assocresp-" + uuid.uuid4().hex
    directory = base / token  # Persistent isolated home; WSL startup may clear /tmp.
    directory.mkdir()
    linux_dir = "/home/ggorbalan/futuramax/" + token
    header = HEADER.read_text()
    (directory / "native.c").write_text(WRAPPER + header + MAIN)
    built = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "gcc", "-std=c99", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-Wall", "-Wextra",
                            "-Werror", "-Wno-deprecated-declarations", linux_dir + "/native.c", "-lcrypto",
                            "-o", linux_dir + "/native"], capture_output=True, text=True, timeout=30)
    (directory / "compile.stdout.txt").write_text(built.stdout)
    (directory / "compile.stderr.txt").write_text(built.stderr)
    assert built.returncode == 0, (directory, built.stderr)
    # cap, crypto fault, NULL argument, addresses, nonce and RSSI; no real payload.
    cases = [("canonical zero feedback", 44, 0, 0, AP, XC, b"\x01\x02\x03\x04", b"\x00\x00", True),
             ("nonce variation", 64, 0, 0, AP, XC, b"\x04\x03\x02\x01", b"\x00\x00", True),
             ("provided RSSI unchanged", 44, 0, 0, AP, XC, b"\xff\x80\x00\x01", b"\xd0\xcf", True),
             ("wrong AP", 44, 0, 0, b"\x19" + AP[1:], XC, bytes(4), bytes(2), False),
             ("wrong XC", 44, 0, 0, AP, b"\xb5" + XC[1:], bytes(4), bytes(2), False)]
    cases += [(f"capacity {n}", n, 0, 0, AP, XC, bytes(4), bytes(2), False) for n in range(44)]
    cases += [(f"crypto fault {n}", 44, n, 0, AP, XC, bytes(4), bytes(2), False) for n in range(1, 5)]
    cases += [(f"NULL argument {n}", 44, 0, n, AP, XC, bytes(4), bytes(2), False) for n in range(1, 6)]
    payload = "".join(f"{cap} {fault} {null} {ap.hex()} {xc.hex()} {nonce.hex()} {rssi.hex()}\n"
                      for _, cap, fault, null, ap, xc, nonce, rssi, _ in cases)
    run = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", linux_dir + "/native"], input=payload,
                         capture_output=True, text=True, timeout=30)
    (directory / "native.stdout.txt").write_text(run.stdout)
    (directory / "native.stderr.txt").write_text(run.stderr)
    assert run.returncode == 0 and not run.stderr, (directory, run.returncode, run.stderr)
    results = run.stdout.splitlines()
    assert len(results) == len(cases)
    outputs = []
    for case, row in zip(cases, results):
        name, cap, fault, null, ap, xc, nonce, rssi, good = case
        ret, calls, deinit, erased, data = row.split()
        ret, calls, deinit, erased = map(int, (ret, calls, deinit, erased))
        data = bytes.fromhex(data)
        assert len(data) == 66 and data[0] == data[-1] == 0xa5, name
        assert erased == 96, name
        if good:
            assert (ret, calls, deinit) == (44, 2, 1), name
            assert data[45:] == b"\xa5" * 21, name
            plain = decode_consumer_model(data[1:45], ap, xc)
            assert plain[10:14] == nonce and plain[14:16] == rssi, name
            outputs.append(data[1:45])
        else:
            assert ret == -1 and data == b"\xa5" * 66, name
            assert deinit == int(fault in (3, 4)), name
            assert calls == ({3: 1, 4: 2}.get(fault, 0)), name
    assert outputs[0] != outputs[1], "Nonce must change the recipient-bound ciphertext"
    wrong_key = hmac.new(AP, XC, hashlib.sha1).digest()[:16]
    assert AES.new(wrong_key, AES.MODE_ECB).decrypt(outputs[0][12:])[:8] != b"\x00\x09" + AP
    (directory / "receipt.json").write_text(json.dumps({
        "status": "PASS_OFFLINE_SYNTHETIC_MSG3_CODEC_MODEL_ONLY", "cases": len(cases),
        "native_exit": run.returncode, "compile_exit": built.returncode,
        "header_sha256": hashlib.sha256(HEADER.read_bytes()).hexdigest(), "schema_sha256": SCHEMA_SHA,
        "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sanitizers": ["address", "undefined"], "consumer_model_not_target_driver": True,
        "RF": False, "captured_payload_used": False,
    }, indent=2) + "\n")
    print("offline receipt:", directory / "receipt.json")
