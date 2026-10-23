"""Execute AL's actual extracted admission and response fragment, offline only.

The parser/delegated normal checks are controlled stubs, with the unchanged
real check_ssid gate. This is not a handshake, driver, RF or power model.
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
AK = Path(r"\\wsl.localhost\Ubuntu\home\ggorbalan\futuramax"
          r"\preprod1_r5ak_userspace_r3_20261023\hostapd\src\ap")
AP, XC = bytes.fromhex("18e8297455a2"), bytes.fromhex("b4fbe45cd5d2")
SSID = b"FuturaMAX-LAB"
PINS = {
    "AK_ieee802_11.c": "388f547344c15ecb89d280ae09bdd0aa361f81ab81c907f418f8e56b80de8aa3",
    "AK_sta_info.h": "ffaeff6b593dd10ff2718909d04384506c98db8df5df5590f5f5489697aaf924",
    "AL_ieee802_11.c": "ba7cd371f6c34962bf953da693f6728fc43c98b51f4545e4ccba55213fa970bb",
    "patch": "6d86c2b4cc958263b47e99ee558a183b106016414c63bb4824f04ea38601c2a7",
    "ssid_header": "34a85e278810284a6d68976736366e4efe59c7020f2515712c06f4bb0367526e",
    "response_header": "12e75a40c614d09557496fa18b3665738c2e62c9d21de83575051d623f76323f",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def function(source, name):
    start = source.index(name)
    return source[start:source.index("\n}\n", start) + 3]


def request(ssid=SSID):
    """Independent synthetic type2 request; no captured/proprietary bytes."""
    body = bytearray(96)
    body[:8] = b"\x00\x09" + XC
    body[18:24] = b"\x01\x04test"
    body[24:26] = bytes([2, len(ssid)])
    body[26:26 + len(ssid)] = ssid
    pos = 26 + len(ssid)
    # TLV3 length makes the final zero padding shorter than a cipher block.
    n = 96 - pos - 9 - 4
    body[pos + 6:pos + 8] = bytes([3, n])
    body[pos + 8:pos + 8 + n] = b"x" * n
    key = hmac.new(AP, XC, hashlib.sha1).digest()[:16]
    payload = bytes.fromhex("002722ffffff02020060") + AES.new(key, AES.MODE_ECB).encrypt(body)
    return bytes([221, len(payload)]) + payload


PRELUDE = r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <openssl/aes.h>
#include <openssl/hmac.h>
typedef uint8_t u8;
typedef uint16_t u16;
#define CONFIG_FMX_PREPROD1_XC_SSID_COMPAT
#define CONFIG_FMX_PREPROD1_XC_ASSOCRESP_COMPAT
#define ETH_ALEN 6
#define WPA_PROTO_RSN 2
#define WPA_KEY_MGMT_PSK 2
#define WPA_CIPHER_CCMP 16
#define WLAN_STATUS_SUCCESS 0
#define WLAN_STATUS_UNSPECIFIED_FAILURE 1
#define HOSTAPD_MODULE_IEEE80211 0
#define HOSTAPD_LEVEL_INFO 0
#define MSG_INFO 0
#define hostapd_logger(h,s,...) do { (void)(h); (void)(s); } while (0)
#define wpa_printf(...) ((void)0)
#define os_memcmp memcmp
#define os_memcpy memcpy
#define WPA_GET_BE16(p) (((unsigned)(p)[0] << 8) | (p)[1])
#define WPA_PUT_BE16(p,v) do { (p)[0]=(u8)((v)>>8); (p)[1]=(u8)(v); } while (0)
struct ssid_conf { u8 ssid[32]; size_t ssid_len; };
struct test_conf { struct ssid_conf ssid; int wpa, wpa_key_mgmt, rsn_pairwise; };
struct test_iface { int freq; };
struct hostapd_data { struct test_conf *conf; struct test_iface *iface; u8 own_addr[6]; };
struct sta_info { u8 addr[6], fmx_xc_response, fmx_xc_nonce_valid, fmx_xc_nonce[4]; };
struct ieee80211_mgmt { u8 da[6], bssid[6], sa[6]; };
struct ieee802_11_elems { const u8 *ssid; size_t ssid_len; };
enum { ParseOK, ParseFailed };
static int normal_status, normal_calls, rng_fail, rng_calls, rng_serial, seen_ssid_len;
static int tx_calls, appended;
static u8 output[64];
static void forced_memzero(void *p, size_t n) { volatile u8 *v=p; while(n--) *v++=0; }
static int hmac_sha1(const u8 *k,size_t kl,const u8 *d,size_t dl,u8 *out) {
    unsigned n=0; return HMAC(EVP_sha1(),k,(int)kl,d,dl,out,&n) && n==20 ? 0:-1;
}
static void *aes_decrypt_init(const u8 *k,size_t n) {
    AES_KEY *c=malloc(sizeof(*c)); if(!c) return NULL;
    if(n!=16 || AES_set_decrypt_key(k,128,c)) { free(c); return NULL; } return c;
}
static int aes_decrypt(void *c,const u8 *in,u8 *out) { AES_decrypt(in,out,c); return 0; }
static void aes_decrypt_deinit(void *c) { free(c); }
static void *aes_encrypt_init(const u8 *k,size_t n) {
    AES_KEY *c=malloc(sizeof(*c)); if(!c) return NULL;
    if(n!=16 || AES_set_encrypt_key(k,128,c)) { free(c); return NULL; } return c;
}
static int aes_encrypt(void *c,const u8 *in,u8 *out) { AES_encrypt(in,out,c); return 0; }
static void aes_encrypt_deinit(void *c) { free(c); }
static int ieee802_11_parse_elems(const u8 *ies,size_t n,struct ieee802_11_elems *e,int show) {
    size_t p=0; (void)show; memset(e,0,sizeof(*e));
    while(p<n) {
        if(n-p<2 || ies[p+1]>n-p-2) return ParseFailed;
        if(ies[p]==0) { e->ssid=ies+p+2; e->ssid_len=ies[p+1]; }
        p+=ies[p+1]+2;
    }
    return ParseOK;
}
static int os_get_random(u8 *out,size_t n) {
    rng_calls++; rng_serial++;
    memset(out,rng_fail ? 0xe1:rng_serial,n);
    return rng_fail ? -1:0;
}
'''

DELEGATE = r'''
static int __check_assoc_ies(struct hostapd_data *h,struct sta_info *s,const u8 *ies,
                size_t n,struct ieee802_11_elems *e,int reassoc,bool mld) {
    int status; (void)ies; (void)n; (void)reassoc; (void)mld;
    normal_calls++; seen_ssid_len=(int)e->ssid_len;
    status=check_ssid(h,s,e->ssid,e->ssid_len);
    return status ? status:normal_status;
}
'''

RUNNER = r'''
struct scenario {
    const char *name,*wire;
    int direct,seed,freq,wpa,key,cipher,reassoc,bad_mgmt,normal,random_fail;
    int response_status,response_reassoc,bad_addr,bad_ap,bad_xc,cap;
};
static void run_case(struct scenario c) {
    static struct sta_info s;
    struct test_conf conf={ .ssid={ .ssid="FuturaMAX-LAB",.ssid_len=13 },
                           .wpa=c.wpa,.wpa_key_mgmt=c.key,.rsn_pairwise=c.cipher };
    struct test_iface iface={ .freq=c.freq };
    struct hostapd_data h={ .conf=&conf,.iface=&iface };
    struct ieee80211_mgmt mgmt;
    const u8 ap[6]={0x18,0xe8,0x29,0x74,0x55,0xa2},xc[6]={0xb4,0xfb,0xe4,0x5c,0xd5,0xd2};
    u8 ies[256],addr[6]; size_t n=strlen(c.wire)/2;
    int status,sent; unsigned v;
    if(c.seed!=2) {
        memset(&s,0,sizeof(s)); memcpy(s.addr,xc,6);
        if(c.seed==1) { s.fmx_xc_response=s.fmx_xc_nonce_valid=1; memset(s.fmx_xc_nonce,0xab,4); }
    }
    memcpy(h.own_addr,ap,6); if(c.bad_ap) h.own_addr[0]^=1;
    if(c.bad_xc) s.addr[0]^=1;
    memcpy(mgmt.da,h.own_addr,6); memcpy(mgmt.bssid,h.own_addr,6); memcpy(mgmt.sa,s.addr,6);
    if(c.bad_mgmt==1) mgmt.da[0]^=1;
    if(c.bad_mgmt==2) mgmt.bssid[0]^=1;
    if(c.bad_mgmt==3) mgmt.sa[0]^=1;
    if(n>sizeof(ies)) exit(3);
    for(size_t i=0;i<n;i++) { if(sscanf(c.wire+i*2,"%2x",&v)!=1) exit(4); ies[i]=(u8)v; }
    normal_status=c.normal; rng_fail=c.random_fail;
    rng_calls=normal_calls=seen_ssid_len=0;
    status=c.direct ? 0:check_assoc_ies(&h,&s,ies,n,c.reassoc,c.bad_mgmt==4 ? NULL:&mgmt);
    memcpy(addr,s.addr,6); if(c.bad_addr) addr[0]^=1;
    tx_calls=appended=0; memset(output,0xa5,sizeof(output));
    sent=response_fragment(&h,&s,addr,c.response_status<0 ? status:c.response_status,
                           c.response_reassoc,c.cap);
    printf("%s %d %u %u ",c.name,status,s.fmx_xc_response,s.fmx_xc_nonce_valid);
    for(int i=0;i<4;i++) printf("%02x",s.fmx_xc_nonce[i]);
    printf(" %d %d %d %d %d %d ",rng_calls,normal_calls,seen_ssid_len,sent,appended,tx_calls);
    for(size_t i=0;i<sizeof(output);i++) printf("%02x",output[i]);
    puts("");
}
'''


def test_actual_al_admission_and_response_fragment():
    if not shutil.which("wsl.exe") or not AK.is_dir():
        pytest.skip("Requires existing isolated AK source and Ubuntu gcc/OpenSSL/patch")
    patch = (ROOT / "tools/bench/hostapd_preprod1_xc_assocresp.patch").read_bytes()
    ssid_header = (ROOT / "tools/bench/hostapd_preprod1_xc_ssid.h").read_bytes()
    response_header = (ROOT / "tools/bench/hostapd_preprod1_xc_assocresp.h").read_bytes()
    original = (AK / "ieee802_11.c").read_bytes()
    sta_header = (AK / "sta_info.h").read_bytes()
    for key, data in [("patch", patch), ("ssid_header", ssid_header), ("response_header", response_header),
                      ("AK_ieee802_11.c", original), ("AK_sta_info.h", sta_header)]:
        assert sha(data) == PINS[key], key
    token = "fmx-al-integration-" + uuid.uuid4().hex
    directory = AK.parents[2] / token
    (directory / "src/ap").mkdir(parents=True)
    (directory / "src/ap/ieee802_11.c").write_bytes(original)
    (directory / "src/ap/sta_info.h").write_bytes(sta_header)
    (directory / "change.patch").write_bytes(patch)
    # directory is under the existing isolated home; never modifies AK or /tmp.
    linux_dir = "/home/ggorbalan/futuramax/preprod1_r5ak_userspace_r3_20261023/" + token
    patched = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "patch", "--batch", "--fuzz=0",
                              "-d", linux_dir, "-p1", "-i", linux_dir + "/change.patch"],
                             capture_output=True, text=True, timeout=20)
    (directory / "patch.stdout.txt").write_text(patched.stdout)
    (directory / "patch.stderr.txt").write_text(patched.stderr)
    assert patched.returncode == 0, (directory, patched.stderr, patched.stdout)
    source_bytes = (directory / "src/ap/ieee802_11.c").read_bytes()
    assert sha(source_bytes) == PINS["AL_ieee802_11.c"]
    source, old = source_bytes.decode(), original.decode()
    assert function(source, "static int __check_assoc_ies(") == function(old, "static int __check_assoc_ies(")
    assert function(source, "static u16 check_ssid(") == function(old, "static u16 check_ssid(")
    admission = function(source, "static int check_assoc_ies(")
    send = function(source, "static u16 send_assoc_resp(")
    start = send.index("#ifdef CONFIG_FMX_PREPROD1_XC_ASSOCRESP_COMPAT")
    end = send.index("#endif", start) + len("#endif")
    fragment = send[start:end]
    assert end < send.index("hostapd_drv_send_mlme("), "Append must precede ordinary TX"
    assert admission.index("sta->fmx_xc_response = 0") < admission.index("ieee802_11_parse_elems(")
    # Execute the actual response fragment, replacing only the surrounding
    # response construction/driver TX with a bounded local recording model.
    response = '''static int response_fragment(struct hostapd_data *hapd,struct sta_info *sta,
            const u8 *addr,int status_code,int reassoc,size_t buflen) {
        u8 *buf=output,*p=buf; int res=WLAN_STATUS_SUCCESS;
        if(buflen>sizeof(output)) return -9;
    ''' + fragment + '''
        appended=(int)(p-buf); tx_calls++;
    done: return res;
    }
    '''
    good, standard = request(), b"\x00\x0d" + SSID
    defaults = dict(wire=good.hex(), direct=0, seed=0, freq=5180, wpa=2, key=2, cipher=16,
                    reassoc=0, bad_mgmt=0, normal=0, random_fail=0, response_status=-1,
                    response_reassoc=0, bad_addr=0, bad_ap=0, bad_xc=0, cap=64)
    cases = []
    def add(name, expected, **changes):
        cases.append((dict(defaults, name=name, **changes), expected))
    # expected: admission status,responseflag,noncevalid,rngcalls,normalcalls,ssidlen,sendrc,append,tx
    ok = (0, 1, 1, 1, 1, 13, 0, 44, 1)
    add("valid", ok)
    add("retry", (0, 1, 1, 0, 1, 13, 0, 44, 1), seed=2)
    add("new_peer", ok)
    add("normal_reject", (37, 0, 0, 0, 1, 13, 0, 0, 1), normal=37, seed=1)
    add("random_fail", (1, 0, 0, 1, 1, 13, 0, 0, 1), random_fail=1)
    add("standard", (0, 0, 0, 0, 1, 13, 0, 0, 1), wire=standard.hex(), seed=1)
    add("wrong_ssid", (1, 0, 0, 0, 1, 13, 0, 0, 1), wire=request(b"Different-LAB").hex(), seed=1)
    add("parse_failure", (1, 0, 1, 0, 0, 0, 0, 0, 1), wire="ddff", seed=1)
    add("reassoc", (1, 0, 0, 0, 1, 0, 0, 0, 1), reassoc=1, seed=1)
    for name, change in [("frequency", dict(freq=5200)), ("WPA", dict(wpa=1)),
                         ("key_mgmt", dict(key=1)), ("cipher", dict(cipher=8)),
                         ("DA", dict(bad_mgmt=1)), ("BSSID", dict(bad_mgmt=2)),
                         ("SA", dict(bad_mgmt=3)), ("no_mgmt", dict(bad_mgmt=4)),
                         ("AP", dict(bad_ap=1)), ("XC", dict(bad_xc=1))]:
        add("request_" + name, (1, 0, 0, 0, 1, 0, 0, 0, 1), seed=1, **change)
    for name, change in [("failure_status", dict(response_status=37)), ("reassoc", dict(response_reassoc=1)),
                         ("frequency", dict(freq=5200)), ("WPA", dict(wpa=1)),
                         ("key_mgmt", dict(key=1)), ("cipher", dict(cipher=8)), ("address", dict(bad_addr=1))]:
        add("response_" + name, (0, 1, 1, 0, 0, 0, 0, 0, 1), direct=1, seed=1, **change)
    for name, change in [("AP", dict(bad_ap=1)), ("XC", dict(bad_xc=1)), ("capacity", dict(cap=43))]:
        add("encoder_" + name, (0, 1, 1, 0, 0, 0, 1, 0, 0), direct=1, seed=1, **change)
    calls = []
    for config, _ in cases:
        fields = ','.join('.' + k + '=' + (json.dumps(v) if isinstance(v, str) else str(v))
                          for k, v in config.items())
        calls.append('run_case((struct scenario){' + fields + '});')
    native = (PRELUDE + ssid_header.decode() + response_header.decode() +
              function(source, "static u16 check_ssid(") + DELEGATE + admission + response + RUNNER +
              '\nint main(void) {\n' + '\n'.join(calls) + '\nreturn 0; }\n')
    (directory / "native.c").write_bytes(native.encode())
    built = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "gcc", "-std=c99", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-Wall", "-Wextra",
                            "-Werror", "-Wno-deprecated-declarations", linux_dir + "/native.c", "-lcrypto",
                            "-o", linux_dir + "/native"], capture_output=True, text=True, timeout=30)
    (directory / "compile.stdout.txt").write_text(built.stdout)
    (directory / "compile.stderr.txt").write_text(built.stderr)
    assert built.returncode == 0, (directory, built.stderr)
    run = subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", linux_dir + "/native"],
                         capture_output=True, text=True, timeout=30)
    (directory / "native.stdout.txt").write_text(run.stdout)
    (directory / "native.stderr.txt").write_text(run.stderr)
    assert run.returncode == 0 and not run.stderr, (directory, run.returncode, run.stderr)
    rows = run.stdout.splitlines()
    assert len(rows) == len(cases)
    nonces = {}
    for (config, expected), row in zip(cases, rows):
        name, status, flag, valid, nonce, rng, normal, ssid_len, sent, size, tx, wire = row.split()
        assert name == config['name']
        actual = tuple(map(int, (status, flag, valid, rng, normal, ssid_len, sent, size, tx)))
        assert actual == expected, (name, actual, expected)
        nonces[name] = nonce
        data = bytes.fromhex(wire)
        assert data[int(size):] == b"\xa5" * (64 - int(size)), name
        if int(size) == 44:
            assert data[:12] == bytes.fromhex("dd2a002722ffffff02030020"), name
            body = AES.new(hmac.new(XC, AP, hashlib.sha1).digest()[:16], AES.MODE_ECB).decrypt(data[12:44])
            assert body == b"\x00\x09" + AP + b"\x03\x03" + bytes.fromhex(nonce) + bytes(2) + b"\x03" + bytes(15)
    assert nonces['valid'] == nonces['retry'] != nonces['new_peer']
    for name in ['standard', 'normal_reject', 'random_fail', 'wrong_ssid', 'reassoc']:
        assert nonces[name] == '00000000', name
    assert nonces['parse_failure'] == 'abababab'  # Flag blocks output; per-STA nonce may survive bad retries.
    receipt = dict(status="PASS_OFFLINE_AL_EXTRACTED_INTEGRATION_MODEL_ONLY", cases=len(cases),
                   patch_exit=patched.returncode, compile_exit=built.returncode, native_exit=run.returncode,
                   pins=PINS, admission_sha256=sha(admission.encode()), response_fragment_sha256=sha(fragment.encode()),
                   test_sha256=sha(Path(__file__).read_bytes()), sanitizers=['address', 'undefined'],
                   parse_and_normal_delegate_are_stubs=True, unchanged_real_check_ssid=True,
                   no_handshake_driver_RF_or_power_acceptance=True, captured_payload_used=False)
    (directory / "receipt.json").write_text(json.dumps(receipt, indent=2) + '\n')
    print('offline receipt:', directory / 'receipt.json')
