"""Execute the real C decoder and unchanged check_ssid against synthetic wire IEs.

Windows bench checks use the existing Ubuntu gcc/OpenSSL installation. This
does not execute a device binary or access a radio. No captured payload is used.
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
SOURCE = Path(
    r"\\wsl.localhost\Ubuntu\home\ggorbalan\futuramax\openwrt-24.10.4"
    r"\build_dir\target-mips_24kc_musl\hostapd-wpad-basic-mbedtls"
    r"\hostapd-2024.09.15~5ace39b0\src\ap\ieee802_11.c"
)
AP = bytes.fromhex("18e8297455a2")
XC = bytes.fromhex("b4fbe45cd5d2")
SSID = b"FuturaMAX-LAB"
PREFIX = bytes.fromhex("002722ffffff")


def wire(body=None, *, ssid=SSID, hostname=b"synthetic-client"):
    if body is None:
        body = bytearray(96)
        body[:2] = b"\x00\x09"
        body[2:8] = XC
        pos = 18
        for typ, value in [(1, hostname), (2, ssid)]:
            body[pos:pos + 2] = bytes([typ, len(value)])
            body[pos + 2:pos + 2 + len(value)] = value
            pos += 2 + len(value)
        body[pos + 6:pos + 8] = b"\x03\x08"
        body[pos + 8:pos + 16] = b"fixture3"
        # Keep padding shorter than a cipher block, matching the wire format.
        end = pos + 17
        if 96 - end >= 16:
            n = 96 - pos - 9 - 4
            body[pos + 7] = n
            body[pos + 8:pos + 8 + n] = b"x" * n
    key = hmac.new(AP, XC, hashlib.sha1).digest()[:16]
    vendor = PREFIX + b"\x02\x02\x00\x60" + AES.new(key, AES.MODE_ECB).encrypt(bytes(body))
    return bytes([221, len(vendor)]) + vendor


def mutate_body(original, offset, value):
    key = hmac.new(AP, XC, hashlib.sha1).digest()[:16]
    body = bytearray(AES.new(key, AES.MODE_ECB).decrypt(original[12:]))
    body[offset] = value
    return wire(body)


def test_native_c_wire_decoder_and_unchanged_ssid_gate():
    if not SOURCE.exists() or not shutil.which("wsl.exe"):
        pytest.skip("Requires the existing FuturaMAX Ubuntu source/compiler")
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == (
        "b44e5b451a08139ccf98dc0a5cefcb9806b918107168e8a157ce893166f2b918"
    )
    source = SOURCE.read_text()
    start = source.index("static u16 check_ssid(")
    end = source.index("\n\nstatic u16 check_wmm", start)
    original_gate = source[start:end]
    header = (ROOT / "tools/bench/hostapd_preprod1_xc_ssid.h").read_text()
    wrapper = r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <openssl/aes.h>
#include <openssl/hmac.h>
typedef uint8_t u8;
typedef uint16_t u16;
#define os_memcmp memcmp
#define os_memcpy memcpy
#define WPA_GET_BE16(p) (((unsigned)(p)[0] << 8) | (p)[1])
#define WLAN_STATUS_UNSPECIFIED_FAILURE 1
#define WLAN_STATUS_SUCCESS 0
#define HOSTAPD_MODULE_IEEE80211 0
#define HOSTAPD_LEVEL_INFO 0
#define hostapd_logger(...) ((void)0)
struct ssid_conf { u8 ssid[32]; size_t ssid_len; };
struct test_conf { struct ssid_conf ssid; };
struct hostapd_data { struct test_conf *conf; };
struct sta_info { u8 addr[6]; };
static void forced_memzero(void *p, size_t n) {
    volatile u8 *v = p; while (n--) *v++ = 0;
}
static int hmac_sha1(const u8 *key, size_t kl, const u8 *data, size_t dl, u8 *out) {
    unsigned n = 0;
    return HMAC(EVP_sha1(), key, (int)kl, data, dl, out, &n) && n == 20 ? 0 : -1;
}
static void *aes_decrypt_init(const u8 *key, size_t n) {
    AES_KEY *ctx = malloc(sizeof(*ctx));
    if (!ctx) return NULL;
    if (n != 16 || AES_set_decrypt_key(key, 128, ctx)) { free(ctx); return NULL; }
    return ctx;
}
static int aes_decrypt(void *ctx, const u8 *in, u8 *out) {
    AES_decrypt(in, out, ctx); return 0;
}
static void aes_decrypt_deinit(void *ctx) { free(ctx); }
'''
    main = r'''
static int unhex(const char *p, u8 *b, size_t cap) {
    size_t n = strlen(p); unsigned v;
    if (n % 2 || n / 2 > cap) return -1;
    for (size_t i = 0; i < n; i += 2) {
        if (sscanf(p + i, "%2x", &v) != 1) return -1;
        b[i / 2] = v;
    }
    return (int)(n / 2);
}
int main(void) {
    char line[10000], ih[8192], ah[13], sh[13];
    u8 ies[4096], ap[6], sa[6], ssid[32];
    struct test_conf conf = { .ssid = { .ssid = "FuturaMAX-LAB", .ssid_len = 13 } };
    struct hostapd_data hapd = { .conf = &conf };
    struct sta_info sta = {0};
    while (fgets(line, sizeof(line), stdin)) {
        int n, result, status;
        if (sscanf(line, "%8191s %12s %12s", ih, ah, sh) != 3) return 3;
        n = unhex(ih, ies, sizeof(ies));
        if (n < 0 || unhex(ah, ap, 6) != 6 || unhex(sh, sa, 6) != 6) return 4;
        result = fmx_preprod1_xc_ssid(ies, n, ap, sa, ssid);
        status = check_ssid(&hapd, &sta, result > 0 ? ssid : NULL, result > 0 ? result : 0);
        printf("%d %d\n", result, status);
    }
    return 0;
}
'''
    good = wire()
    cases = [
        ("explicit exact SSID", good, AP, XC, (13, 0)),
        ("wrong SSID reaches normal reject", wire(ssid=b"Other-LAB-SSID"), AP, XC, (14, 1)),
        ("empty SSID", wire(ssid=b""), AP, XC, (-1, 1)),
        ("existing exact ID0 never overridden", b"\x00\x0d" + SSID + good, AP, XC, (-1, 1)),
        ("existing wrong ID0 never overridden", b"\x00\x03BAD" + good, AP, XC, (-1, 1)),
        ("duplicate vendor", good + good, AP, XC, (-1, 1)),
        ("foreign AP", good, b"\x01" + AP[1:], XC, (-1, 1)),
        ("foreign station", good, AP, b"\x01" + XC[1:], (-1, 1)),
        ("wrong cipher version", good[:8] + b"\x01" + good[9:], AP, XC, (-1, 1)),
        ("wrong message type", good[:9] + b"\x03" + good[10:], AP, XC, (-1, 1)),
        ("wrong declared length", good[:10] + b"\x00\x50" + good[12:], AP, XC, (-1, 1)),
        ("wrong protocol version", mutate_body(good, 1, 8), AP, XC, (-1, 1)),
        ("embedded SA mismatch", mutate_body(good, 2, 1), AP, XC, (-1, 1)),
        ("wrong TLV1 type", mutate_body(good, 18, 2), AP, XC, (-1, 1)),
        ("overflow TLV1", mutate_body(good, 19, 255), AP, XC, (-1, 1)),
        ("duplicate TLV2 in hostname position", mutate_body(good, 18, 2), AP, XC, (-1, 1)),
        ("overflow TLV2", mutate_body(good, 37, 255), AP, XC, (-1, 1)),
        ("wrong TLV3", mutate_body(good, 57, 2), AP, XC, (-1, 1)),
        ("nonzero padding", mutate_body(good, 95, 1), AP, XC, (-1, 1)),
        ("unrelated IE retained", b"\x01\x01\x0c" + good, AP, XC, (13, 0)),
        ("trailing IE header truncated", good + b"\xdd", AP, XC, (-1, 1)),
    ]
    for n in range(1, len(good)):
        cases.append((f"truncated at {n}", good[:n], AP, XC, (-1, 1)))
    token = "fmx-xc-ssid-" + uuid.uuid4().hex
    directory = Path(r"\\wsl.localhost\Ubuntu\home\ggorbalan\futuramax") / token
    directory.mkdir()
    (directory / "native.c").write_text(wrapper + header + original_gate + main)
    linux_dir = "/home/ggorbalan/futuramax/" + token
    command = ["wsl.exe", "-d", "Ubuntu", "--", "gcc", "-std=c99", "-O1", "-g",
               "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
               "-Wno-deprecated-declarations", linux_dir + "/native.c", "-lcrypto",
               "-o", linux_dir + "/native"]
    built = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert built.returncode == 0, built.stderr
    payload = "".join(f"{ie.hex()} {ap.hex()} {sa.hex()}\n" for _, ie, ap, sa, _ in cases)
    run = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", linux_dir + "/native"],
                         input=payload, capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    assert not run.stderr, run.stderr
    results = [tuple(map(int, line.split())) for line in run.stdout.splitlines()]
    assert len(results) == len(cases)
    for case, result in zip(cases, results):
        assert result == case[-1], (case[0], result, case[-1])
    (directory / "receipt.json").write_text(json.dumps({
        "cases": len(cases), "native_exit": run.returncode,
        "sanitizers": ["address", "undefined"], "captured_payload_used": False,
        "header_sha256": hashlib.sha256(header.encode()).hexdigest(),
        "unchanged_check_ssid_sha256": hashlib.sha256(original_gate.encode()).hexdigest(),
    }, indent=2) + "\n")
