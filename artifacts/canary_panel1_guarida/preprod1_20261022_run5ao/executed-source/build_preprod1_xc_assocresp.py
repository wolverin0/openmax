"""Isolated userspace-only PREPROD1 association-response build using existing OpenWrt sources/tools.

Run in the existing Ubuntu distro. Never writes the source tree, installs a
package, accesses devices, or executes the resulting MIPS binary.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openwrt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.openwrt.resolve(strict=True)
    out = args.out.resolve()
    if out.exists() or out == root or root in out.parents:
        raise RuntimeError("New isolated output outside existing OpenWrt tree required")
    project = Path(__file__).resolve().parents[2]
    source = root / "build_dir/target-mips_24kc_musl/hostapd-wpad-basic-mbedtls/hostapd-2024.09.15~5ace39b0"
    original_c = source / "src/ap/ieee802_11.c"
    if digest(original_c) != "b44e5b451a08139ccf98dc0a5cefcb9806b918107168e8a157ce893166f2b918":
        raise RuntimeError("Held source changed")
    out.mkdir()
    record = {
        "utc": datetime.now(timezone.utc).isoformat(), "status": "INCOMPLETE",
        "source": str(source), "out": str(out), "device_access": False,
        "target_execution": False, "commands": [], "inputs": {},
        "baseline_c_sha256": digest(original_c),
        "provenance_limit": "Same held source version; existing built executable differs from live stock. No exact-live-build equivalence claimed.",
    }
    env = dict(os.environ)
    toolchain = root / "staging_dir/toolchain-mips_24kc_gcc-13.3.0_musl"
    cross = toolchain / "bin/mips-openwrt-linux-musl-"
    env["PATH"] = str(toolchain / "bin") + os.pathsep + env["PATH"]
    env["STAGING_DIR"] = str(root / "staging_dir/target-mips_24kc_musl")

    def run(argv, cwd):
        index = len(record["commands"])
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=180)
        log = out / f"command-{index}.log"
        log.write_bytes(result.stdout + result.stderr)
        record["commands"].append({"argv": argv, "cwd": str(cwd), "exit_code": result.returncode,
                                   "log_sha256": digest(log)})
        if result.returncode:
            raise RuntimeError(f"Build command {index} failed, exit {result.returncode}: {result.stderr[-1500:].decode(errors='replace')}")
        return result.stdout

    try:
        copied = out / "hostapd"
        # Held objects predate AC enablement. Rebuild both archives together;
        # reusing them would mix incompatible feature-dependent structures.
        shutil.copytree(source, copied, symlinks=True, ignore=shutil.ignore_patterns(
            "build", "*.o", "*.a", "wpad", ".built*", ".pkgdir", "ipkg-mips_24kc"))
        for name in ["hostapd_preprod1_xc_ssid.h", "hostapd_preprod1_xc_ssid.patch",
                     "hostapd_preprod1_xc_assocresp.h", "hostapd_preprod1_xc_assocresp.patch"]:
            p = project / "tools/bench" / name
            record["inputs"][name] = digest(p)
        run(["patch", "--batch", "--fuzz=0", "-p1", "-i",
             str(project / "tools/bench/hostapd_preprod1_xc_ssid.patch")], copied)
        shutil.copy2(project / "tools/bench/hostapd_preprod1_xc_ssid.h",
                     copied / "src/ap/hostapd_preprod1_xc_ssid.h")
        if digest(copied / "src/ap/ieee802_11.c") != "388f547344c15ecb89d280ae09bdd0aa361f81ab81c907f418f8e56b80de8aa3":
            raise RuntimeError("Validated AK baseline changed")
        run(["patch", "--batch", "--fuzz=0", "-p1", "-i",
             str(project / "tools/bench/hostapd_preprod1_xc_assocresp.patch")], copied)
        shutil.copy2(project / "tools/bench/hostapd_preprod1_xc_assocresp.h",
                     copied / "src/ap/hostapd_preprod1_xc_assocresp.h")
        record["inputs"]["held_cflags"] = digest(source / ".cflags")
        flags = shlex.split((copied / ".cflags").read_text().replace(str(source), str(copied)))
        flags += ["-DCONFIG_IEEE80211AC", "-DCONFIG_FMX_PREPROD1_XC_SSID_COMPAT",
                  "-DCONFIG_FMX_PREPROD1_XC_ASSOCRESP_COMPAT"]
        # As in OpenWrt's multicall recipe, both builds use the same complete
        # combined CFLAGS. Make options must select matching object lists.
        options = ["MULTICALL=1", "CONFIG_ACS=y", "CONFIG_DRIVER_NL80211=y",
                   "CONFIG_IEEE80211AC=y", "CONFIG_IEEE80211AX=", "CONFIG_IEEE80211BE=",
                   "CONFIG_MBO=y", "CONFIG_UCODE=y", "CONFIG_APUP=y", "CONFIG_TLS=mbedtls",
                   "CONFIG_SAE=y", "CONFIG_OWE=y", "CONFIG_WEP=",
                   "CC=" + str(cross) + "gcc", "AR=" + str(cross) + "gcc-ar",
                   "RANLIB=" + str(cross) + "gcc-ranlib", "CFLAGS=" + shlex.join(flags)]
        run(["make", "-j4"] + options + ["hostapd_multi.a"], copied / "hostapd")
        run(["make", "-j4"] + options + ["wpa_supplicant_multi.a"], copied / "wpa_supplicant")
        archive = copied / "hostapd/hostapd_multi.a"
        members = run([str(cross) + "gcc-ar", "t", str(archive)], copied).decode().splitlines()
        if members.count("ieee802_11.o") != 1:
            raise RuntimeError("Ambiguous archive member")
        libraries = ["-lmbedcrypto", "-lmbedx509", "-lmbedtls", "-lubox", "-lubus",
                     "-lblobmsg_json", "-lucode", "-lm", "-lnl-tiny", "-ludebug"]
        search = ["-L" + str(root / "staging_dir/target-mips_24kc_musl/usr/lib"),
                  "-L" + str(root / "staging_dir/target-mips_24kc_musl/lib"),
                  "-L" + str(toolchain / "usr/lib"), "-L" + str(toolchain / "lib")]
        binary = out / "wpad.compat"
        run([str(cross) + "gcc", "-o", str(binary)] + flags +
            [str(root / "package/network/services/hostapd/files/multicall.c"), str(archive),
             str(copied / "wpa_supplicant/wpa_supplicant_multi.a")] + search +
            ["-pie", "-Wl,--gc-sections", "-Wl,-z,now", "-Wl,-z,relro"] + libraries, copied)
        run([str(root / "staging_dir/host/bin/sstrip"), "-z", str(binary)], copied)
        record.update(status="BUILT_NOT_RUNTIME_QUALIFIED", binary_sha256=digest(binary),
                      binary_bytes=binary.stat().st_size,
                      patched_c_sha256=digest(copied / "src/ap/ieee802_11.c"),
                      patched_sta_info_sha256=digest(copied / "src/ap/sta_info.h"),
                      full_clean_archives=True, coherent_AC_every_translation_unit=True,
                      PIE_ELF_type=binary.read_bytes()[16:18] == b"\x00\x03",
                      stock_VHT_marker_present=b"mandatory VHT" in binary.read_bytes(),
                      compat_marker_present=b"FMX-PREPROD1-XC-EXPLICIT-SSID" in binary.read_bytes(),
                      assocresp_marker_present=b"FMX-PREPROD1-XC-ASSOCRESP" in binary.read_bytes())
        if not all(record[key] for key in
                   ["stock_VHT_marker_present", "compat_marker_present", "assocresp_marker_present", "PIE_ELF_type"]):
            record["status"] = "INVALID_FEATURE_BASELINE_NO_EXECUTE"
            raise RuntimeError("Expected VHT and compatibility features absent")
    except BaseException as exc:
        record["error"] = str(exc)
        raise
    finally:
        record["original_c_unchanged"] = digest(original_c) == record["baseline_c_sha256"]
        (out / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in
                      ["status", "binary_sha256", "binary_bytes", "original_c_unchanged"]}))


if __name__ == "__main__":
    main()
