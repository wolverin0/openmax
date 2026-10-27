"""Stage29A bounded, offline protocol/knob census and M9-M15 hypothesis miner.

No command/firmware executor, binary exporter or radio access is provided.
An enum ID, literal occurrence, recipe or Champion entry is not runtime proof.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import os
import re
import stat
import struct
import sys
from collections import Counter
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "T-S29A-CODEX-PB010-PB012-DEEP-FIRMWARE-AND-VAULT-SYNTHESIS"
OUTPUT = "artifacts/autoresearch/stage29a_mined_knobs_and_hypotheses_20261025.json"
DRIVER = "tools/research/srccache/ath10k-ct/ath10k-7.2/"
DEEP = "artifacts/firmware_re_xc_ltu/ubnt_poll_and_ltu_12x_deep_re_20261024.json"
CATALOG = "orchestration/autoresearch/firmware_knob_candidates.json"
LIVE_LEDGER = "artifacts/autoresearch/champion_state_ledger.json"
# Explicit research cutoff; the live writer may continue without invalidating it.
LEDGER = ("artifacts/autoresearch/stage29a_source_cutoff_20261025/"
          "champion_state_ledger_e35ecf41d792d2dd2c667cb0cc68c75236e135bf4e268a2a9b6b008062400abd.json")
PB_MAP = "artifacts/physical_boundary/pb010_011_xtensa_wmi_htt_map_20261025.json"
CONSUMERS = "research/raw/target-consumers-ap-20261006-final-reviewed.json"
UMAC = "firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68/umac.ko"
ELF = "analysis/re_ubnt_poll_and_ltu_4096qam.py"
SGMT = "tools/research/sgmt.py"
DOCS = ["docs/STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md",
        "docs/STAGE25_SCHOLAR_HYPERRESEARCH_FUSION_AND_M3_M5_BENCHMARK.md"]
PINS = {
    LEDGER: "e35ecf41d792d2dd2c667cb0cc68c75236e135bf4e268a2a9b6b008062400abd",
    DRIVER+"wmi.h": "df45baed64d1cc03024663203f38b8f2f2ae05d6b8116c65b877bec65b469ced",
    DRIVER+"wmi.c": "64d7d982e27ffda7e548c9327bf9bbcb30dd7509df26fda65d9126c7662407e9",
    DRIVER+"htt.h": "5a9dd5a60913e0bdb8360e944c5798a5d4d3762595f9e88eeca86fb7a49e16d5",
    DRIVER+"htt_tx.c": "313407ebed8a29d465ce2b1b940f89987df1206457358332a8b611e91e4f5684",
    DEEP: "57409afe392fbe1132a48c41e87350f8354a09f6bb95254f3e7e05719180139a",
    CATALOG: "54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a",
    CONSUMERS: "1ee0556a6d956f1b9824d8822a9365da60cb5d3b62c4b6fa6a55a42d0bae52c0",
    UMAC: "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5",
    ELF: "118a02ee21abe31eedd7d3dfea3c7b32359ac8e16276bf65c290a89fc87ca770",
    SGMT: "f6e8a73fa2277a26901469a825373dba512262464015e8772a4acf6a1f47dec8",
}
FIXED = sorted(set(PINS) | {LEDGER, PB_MAP, *DOCS})
MAX_FILE = 4 * 1024 * 1024
MAX_TOTAL = 48 * 1024 * 1024
SURFACE = r"/(?:sys/module/ame_core/parameters|proc/sys/dev/uph(?:_wifi0)?|sys/class/ame/ame_ctrl_dev)/[A-Za-z0-9_]+"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def local_path(value):
    text = os.fspath(value)
    require(type(text) is str, "Local text path required")
    windows = text.replace("/", "\\")
    require(not windows.startswith(("\\\\", "\\??\\"))
            and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", text)
            and not PureWindowsPath(text).is_reserved(), "Remote/device path forbidden")
    path = Path(text).absolute()
    if os.name == "nt":
        import ctypes
        require(ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) != 4, "Mapped remote drive forbidden")
    for parent in reversed((path, *path.parents)):
        try:
            info = parent.lstat()
        except FileNotFoundError:
            break
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                "Symlink/reparse traversal forbidden")
    return path


def read_local(path, limit=MAX_FILE):
    path = local_path(path)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and info.st_size <= limit, "Bounded regular input required")
    with path.open("rb") as stream:
        raw = stream.read(limit+1)
    require(len(raw) <= limit, "Input size limit exceeded")
    return raw


def load_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Duplicate JSON key")
            out[key] = value
        return out
    def bad(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def safe_files(relative, maximum=20000):
    """Walk only verified local directories; reparse paths become coverage gaps."""
    root = local_path(ROOT/relative)
    pending, files, gaps, count = [root], [], [], 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                count += 1
                require(count <= maximum, f"Inventory entry limit exceeded: {relative}")
                try:
                    path = local_path(entry.path)
                except ValueError:
                    gaps.append(Path(entry.path).relative_to(ROOT).as_posix())
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    files.append(path.relative_to(ROOT).as_posix())
    return sorted(files), sorted(gaps)


def _role(path):
    if path in FIXED:
        return "required"
    if re.fullmatch(r"artifacts/autoresearch/stage[^/]+\.json", path) and path != OUTPUT:
        return "stage_receipt_or_plan"
    if (path.startswith("artifacts/hyperresearch_vault/")
            and "/futuramax/" not in path and Path(path).suffix in (".md", ".json")
            and any(part in path for part in ("/sources/", "/claims/", "/research/notes/", "/research/temp/"))):
        return "vault_stored_source_or_claim"
    if path.startswith("firmware/") and Path(path).name.lower() == "firmware-5.bin":
        return "firmware_api5_candidate"
    raise ValueError("Input manifest path outside allowed research population")


def collect_manifest():
    stage, stage_gaps = safe_files("artifacts/autoresearch")
    vault, vault_gaps = safe_files("artifacts/hyperresearch_vault")
    firmware, firmware_gaps = safe_files("firmware", maximum=50000)
    selected = set(FIXED)
    for path in stage+vault+firmware:
        try:
            _role(path)
        except ValueError:
            continue
        selected.add(path)
    require(len(selected) <= 512, "Source population exceeds bounded manifest")
    manifest, total = [], 0
    for path in sorted(selected):
        raw = read_local(ROOT/path)
        if path in PINS:
            require(sha256(raw) == PINS[path], f"Primary source SHA256 mismatch: {path}")
        total += len(raw)
        require(total <= MAX_TOTAL, "Total source byte budget exceeded")
        manifest.append(dict(path=path, bytes=len(raw), sha256=sha256(raw), role=_role(path)))
    inventory = dict(root="firmware", files_inspected=len(firmware),
                     filenames_sha256=sha256("\n".join(firmware).encode()),
                     firmware5_matches=[p for p in firmware if Path(p).name.lower() == "firmware-5.bin"],
                     reparse_paths_not_traversed=firmware_gaps,
                     absence_scope="this retained local tree only", universal_absence_claim=False)
    return manifest, inventory, dict(stage=stage_gaps, vault=vault_gaps)


def read_manifest(manifest):
    require(type(manifest) is list and 1 <= len(manifest) <= 512, "Bounded source manifest required")
    raw, total = {}, 0
    for item in manifest:
        require(type(item) is dict and set(item) == {"path", "bytes", "sha256", "role"}, "Invalid manifest entry")
        path = item["path"]
        require(type(path) is str and "\\" not in path and ".." not in Path(path).parts,
                "Canonical relative manifest path required")
        require(item["role"] == _role(path) and path not in raw, "Duplicate/incorrect source role")
        require(type(item["bytes"]) is int and 0 <= item["bytes"] <= MAX_FILE, "Invalid source byte size")
        require(type(item["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), "Invalid source digest")
        content = read_local(ROOT/path)
        require(len(content) == item["bytes"] and sha256(content) == item["sha256"], f"Frozen source drift: {path}")
        require(path not in PINS or sha256(content) == PINS[path], f"Primary source pin drift: {path}")
        raw[path] = content
        total += len(content)
        require(total <= MAX_TOTAL, "Total source byte budget exceeded")
    require(set(FIXED) <= set(raw), "Required primary inputs missing")
    return raw


def c_comments(text):
    return re.sub(r"/\*.*?\*/|//[^\n]*",
                  lambda m: "".join("\n" if c == "\n" else " " for c in m.group()), text, flags=re.S)


def integer_expression(expression, symbols):
    """Restricted C-enum arithmetic. Unknown constructs remain unresolved."""
    require(type(expression) is str and len(expression) <= 1024, "Bounded enum expression required")
    expression = re.sub(r"\b(0[xX][0-9a-fA-F]+|\d+)[uUlL]+\b", r"\1", expression)
    tree = ast.parse(expression.strip(), mode="eval")
    require(sum(1 for _ in ast.walk(tree)) <= 128, "Enum expression node budget exceeded")
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            result = node.value
        elif isinstance(node, ast.Name):
            require(node.id in symbols and symbols[node.id] is not None, "Unknown enum symbol")
            result = symbols[node.id]
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub, ast.Invert)):
            value = visit(node.operand)
            result = value if isinstance(node.op, ast.UAdd) else -value if isinstance(node.op, ast.USub) else ~value
        elif isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.LShift, ast.RShift)):
                require(0 <= right <= 31, "Shift outside uint32 domain")
            ops = {ast.Add: lambda: left+right, ast.Sub: lambda: left-right,
                   ast.Mult: lambda: left*right, ast.BitOr: lambda: left|right,
                   ast.BitAnd: lambda: left&right, ast.BitXor: lambda: left^right,
                   ast.LShift: lambda: left<<right, ast.RShift: lambda: left>>right}
            require(type(node.op) in ops, "Unsupported enum operator")
            result = ops[type(node.op)]()
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
            value = visit(node.args[0])
            if node.func.id in ("WMI_CMD_GRP", "WMI_EVT_GRP"):
                result = (value << 12) | 1
            else:
                require(node.func.id == "BIT" and 0 <= value <= 31, "Unsupported enum macro")
                result = 1 << value
        else:
            raise ValueError("Unsupported enum expression")
        require(type(result) is int and -(1 << 31) <= result <= 0xffffffff, "Enum arithmetic out of range")
        return result
    return visit(tree.body)


def _members(body):
    start = depth = 0
    for i, char in enumerate(body):
        depth += (char == "(") - (char == ")")
        require(depth >= 0, "Unbalanced enum parentheses")
        if char == "," and depth == 0:
            yield start, body[start:i]
            start = i+1
    require(depth == 0, "Unbalanced enum parentheses")
    if body[start:].strip():
        yield start, body[start:]


def enum_catalog(text, source):
    cleaned, symbols, rows = c_comments(text), {}, []
    for match in re.finditer(r"\benum\s+(\w+)\s*\{([^{}]*)\}\s*;", cleaned, re.S):
        namespace, body = match.group(1), match.group(2)
        relevant = (namespace.startswith("wmi") and namespace.endswith(("_cmd_id", "_event_id", "_pdev_param", "_vdev_param", "_peer_param"))
                    or namespace.startswith("htt") and namespace.endswith("msg_type")
                    or namespace == "htt_dbg_stats_type")
        previous, aliases = -1, {}
        for offset, member in _members(body):
            member = re.sub(r"(?m)^[ \t]*#[^\n]*", lambda m: " "*len(m.group()), member)
            leading = len(member)-len(member.lstrip())
            member = member.strip()
            if not member:
                continue
            parts = member.split("=", 1)
            name, expression = parts[0].strip(), parts[1].strip() if len(parts) == 2 else None
            require(re.fullmatch(r"[A-Za-z_]\w*", name), "Malformed enum member")
            try:
                value = integer_expression(expression, symbols) if expression is not None else previous+1 if previous is not None else None
            except (ValueError, SyntaxError, RecursionError):
                value = None
            previous, symbols[name] = value, value
            if not relevant:
                continue
            if namespace.startswith("htt"):
                direction = "H2T" if "_h2t_" in namespace else "T2H" if "_t2h_" in namespace else "STATS_MASK"
                kind = "message" if direction in ("H2T", "T2H") else "bitmask"
            else:
                kind = "command" if namespace.endswith("_cmd_id") else "event" if namespace.endswith("_event_id") else "parameter"
                direction = "H2T" if kind == "command" else "T2H" if kind == "event" else "PAYLOAD_PARAMETER"
            sentinel = bool(re.fullmatch(r"WMI_(?:10X|10_2|10_4)_(?:START|END)_(?:CMDID|EVENTID)", name)
                            or name.endswith("_NUM_MSGS")
                            or name == "HTT_DBG_NUM_STATS" or "UNSUPPORTED" in name)
            rows.append(dict(namespace=namespace, symbol=name, value=value, hex=f"0x{value:x}" if value is not None else None,
                             expression=expression, resolution="RESOLVED" if value is not None else "UNRESOLVED",
                             kind=kind, direction=direction, sentinel=sentinel, alias_of=aliases.get(value) if value is not None else None,
                             source=source, line=cleaned.count("\n", 0, match.start(2)+offset+leading)+1,
                             host_maps=[], runtime_support_verified=False, exact_build_testedness="UNKNOWN"))
            if value is not None:
                aliases.setdefault(value, name)
    return rows


def protocol_catalog(raw):
    rows = enum_catalog(raw[DRIVER+"wmi.h"].decode(), DRIVER+"wmi.h")
    rows += enum_catalog(raw[DRIVER+"htt.h"].decode(), DRIVER+"htt.h")
    by_symbol = {}
    for row in rows:
        by_symbol.setdefault(row["symbol"], []).append(row)
    source = c_comments(raw[DRIVER+"wmi.c"].decode())
    for table in re.finditer(r"(?:static\s+)?(?:const\s+)?struct\s+(wmi_\w+_map)\s+(\w+)\s*=\s*\{(.*?)\};", source, re.S):
        for assignment in re.finditer(r"\.(\w+)\s*=\s*(WMI_\w+)", table.group(3)):
            for row in by_symbol.get(assignment.group(2), []):
                row["host_maps"].append(f"{table.group(2)}.{assignment.group(1)}")
    return rows


def api5_metadata(blob):
    """Validate the API5 container only; never claim its image ABI is qualified."""
    require(blob.startswith(b"QCA-ATH10K\0"), "Not an ath10k API5 container")
    offset, records, seen = 12, [], set()
    while offset < len(blob):
        require(len(records) < 256, "API5 record budget exceeded")
        require(offset+8 <= len(blob), "Truncated API5 IE")
        ident, size = struct.unpack_from("<II", blob, offset)
        offset += 8
        require(size <= len(blob)-offset and ident not in seen, "Invalid or duplicate API5 IE")
        seen.add(ident)
        payload = blob[offset:offset+size]
        records.append(dict(id=ident, bytes=size, sha256=sha256(payload)))
        offset += (size+3) & ~3
        require(offset <= len(blob), "Truncated API5 padding")
    require(3 in seen, "API5 firmware image IE missing")
    return dict(format="ATH10K_API5_CONTAINER", records=records, firmware_image_ie=3,
                loader_abi_qualified=False, execution_verified=False)


def firmware_evidence(raw, protocols, inventory):
    for path in (ELF, SGMT):
        require(sha256(raw[path]) == PINS[path], "Unverified helper source")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    elf_module = importlib.import_module("analysis.re_ubnt_poll_and_ltu_4096qam")
    decoder = importlib.import_module("tools.research.sgmt")
    require(local_path(elf_module.__file__) == local_path(ROOT/ELF)
            and local_path(decoder.__file__) == local_path(ROOT/SGMT), "Unexpected helper import")
    elf = elf_module.Elf32Image(SimpleNamespace(read_bytes=lambda: raw[UMAC]))
    section, symbols = elf.section_bytes(".data"), {s["name"]: s for s in elf.symbols}
    known = {r["value"] for r in protocols if r["kind"] == "command" and r["value"] is not None and r["value"] >= 0x1000}
    crossrefs, images = {}, []
    for name in ("athwlan_AR9888v2_ptmp_ap_bin", "athwlan_AR9888v2_ptmp_sta_bin", "athwlan_AR9888v2_ptp_bin"):
        symbol = symbols[name]
        blob = section[symbol["value"]:symbol["value"]+symbol["size"]]
        metadata, payloads = decoder.decode_sgmt_memory(blob)
        require(metadata["consumed_bytes"] == len(blob), "Incomplete SGMT parse")
        images.append(dict(symbol=name, bytes=len(blob), sha256=sha256(blob),
                           segments=len(payloads), decoded_bytes=metadata["decoded_total"]))
        for segment, (address, payload) in enumerate(payloads):
            for offset in range(0, len(payload)-3, 4):
                value = struct.unpack_from("<I", payload, offset)[0]
                if value in known:
                    item = crossrefs.setdefault(f"0x{value:x}", dict(count=0, examples=[]))
                    item["count"] += 1
                    if len(item["examples"]) < 16:
                        item["examples"].append(dict(image=name, segment=segment, offset=offset,
                                                     address=f"0x{address+offset:08x}"))
    api5 = []
    for path in inventory["firmware5_matches"]:
        metadata = api5_metadata(raw[path])
        api5.append(dict(path=path, sha256=sha256(raw[path]), **metadata))
    return dict(requested_firmware5_status="PRESENT_CONTAINER_ONLY" if api5 else "ABSENT_IN_BOUNDED_TREE",
                inventory=inventory, api5_images=api5, vendor_module=dict(path=UMAC, sha256=PINS[UMAC]),
                vendor_sgmt_images=images, aligned_u32_literal_crossrefs=crossrefs,
                literal_hits_prove_dispatch=False, vendor_sgmt_is_api5=False,
                all_proprietary_opcodes_mined=False, exact_firmware_runtime_abi_verified=False)


def knob_catalog(raw):
    catalog, deep = load_json(raw[CATALOG]), load_json(raw[DEEP])
    rows = []
    for item in catalog["knobs"]:
        if item["family"] not in ("airos_sysctl", "ltu_sysfs"):
            continue
        rows.append(dict(id=item["id"], name=item["name"], population=item["family"],
                         platform_scope=item["platform_scope"], surface=item["interface"]["surface"],
                         declaration_source=CATALOG, source_refs=item["source_refs"],
                         encoding_domain=item["encoding_domain"], physical_safe_range=None,
                         permissions_verified=False, writable_reversible_verified=False,
                         readback_kind=item["interface"]["state_readback"]))
    parameters = deep["ltu_4096qam_re"]["aflturocket_2_4_2_ame_core"]
    require(parameters["module_parameters_count"] == len(parameters["module_parameters"]), "AME declared count mismatch")
    for item in parameters["module_parameters"]:
        rows.append(dict(id="ame_ap_2_4_2:"+item["name"], name=item["name"], population="ame_core_module_parameter",
                         platform_scope=["aflturocket_2.4.2"], surface=item["sysfs_path"],
                         declaration_source=DEEP, declared_type=item["type"], description=item["description"],
                         physical_safe_range=None, permissions_verified=False, writable_reversible_verified=False,
                         readback_kind="UNKNOWN; module metadata is not a proven live state getter"))
    return rows


def _walk_json(value, pointer="", depth=0):
    require(depth <= 40, "JSON nesting budget exceeded")
    if isinstance(value, dict):
        for key, item in value.items():
            escaped = key.replace("~", "~0").replace("/", "~1")
            yield from _walk_json(item, pointer+"/"+escaped, depth+1)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _walk_json(item, pointer+"/"+str(i), depth+1)
    else:
        yield pointer, value


def setting_references(text, source, pointer="", category="MENTION_ONLY"):
    """Only extract literal control paths/numeric values; never save shell scripts."""
    require(type(text) is str and len(text) <= MAX_FILE, "Bounded source text required")
    refs, covered = [], set()
    for match in re.finditer(r"\becho\s+(['\"]?)([-+0-9a-fA-FxX \t]+)\1\s*>\s*("+SURFACE+r")\b", text):
        tokens = match.group(2).strip().split()
        try:
            values = [int(token, 0) for token in tokens]
        except ValueError:
            values = []
        surface = match.group(3)
        refs.append(dict(surface=surface, value=values[0] if len(values) == 1 else values or None,
                         source=source, pointer=pointer, category=category,
                         error_suppression_present=bool(re.search(r"\|\|\s*(?:true|:)",
                                                                 text[match.start():match.end()+32])),
                         runtime_effect_verified=False))
        covered.add((surface, match.start(3)))
    for match in re.finditer(SURFACE+r"\b", text):
        if (match.group(), match.start()) not in covered:
            refs.append(dict(surface=match.group(), value=None, source=source, pointer=pointer,
                             category="MENTION_ONLY", error_suppression_present=False, runtime_effect_verified=False))
    return refs


def tested_references(raw, knobs):
    refs, names = [], {r["name"]: r["surface"] for r in knobs if r["population"] == "ame_core_module_parameter"}
    for path, content in raw.items():
        if path != LEDGER and not (path.startswith("artifacts/autoresearch/stage") and path.endswith(".json")):
            continue
        data = load_json(content)
        # Dispatch authority is independent from whether saved measurements exist.
        # automatic_execution_allowed=False alone must not erase historical tests.
        offline = bool(re.search(r"OFFLINE|DRY_RUN|PLAN_ONLY",
                                 str(data.get("mode", data.get("execution_mode", ""))), re.I))
        for pointer, value in _walk_json(data):
            leaf = pointer.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~")
            numeric = value if type(value) is int else None
            if type(value) is str and re.fullmatch(r"[-+]?(?:0[xX][0-9a-fA-F]+|[0-9]+)", value.strip()):
                numeric = int(value.strip(), 0) if "x" in value.lower() else int(value.strip(), 10)
            if numeric is not None and (re.fullmatch(SURFACE, leaf) or leaf in names):
                refs.append(dict(surface=leaf if leaf.startswith("/") else names[leaf], value=numeric,
                                 source=path, pointer=pointer,
                                 category="NUMERIC_RECEIPT_MENTION" if not offline else "OFFLINE_PLAN_ONLY",
                                 error_suppression_present=False, runtime_effect_verified=False))
            if isinstance(value, str):
                if path == LEDGER and "/apply_commands/" in pointer:
                    category = "CHAMPION_DECLARED_SETTING"
                elif "script" in pointer.lower() or "command" in pointer.lower():
                    category = "RECIPE_INTENTION_NOT_EXECUTION"
                elif offline:
                    category = "OFFLINE_PLAN_ONLY"
                elif re.search(r"/(?:rounds|phases|final_ram_state|mechanism_tested)/", pointer):
                    category = "SAVED_RECEIPT_REPORTED_SETTING"
                else:
                    category = "MENTION_ONLY"
                refs.extend(setting_references(value, path, pointer, category))
    unique = {json.dumps(r, sort_keys=True): r for r in refs}
    return sorted(unique.values(), key=lambda r: (r["surface"], r["source"], r["pointer"], str(r["value"])))


def testedness(surface, proposed_value, references):
    require(type(surface) is str and re.fullmatch(SURFACE, surface), "Literal control surface required")
    require(proposed_value is None or type(proposed_value) is int
            or type(proposed_value) is list and len(proposed_value) <= 16
            and all(type(v) is int for v in proposed_value), "Typed integer/vector mutation value required")
    matches = [r for r in references if r["surface"] == surface]
    exact = [r for r in matches if proposed_value is not None and type(r["value"]) is type(proposed_value)
             and r["value"] == proposed_value]
    reported = [r for r in matches if r["category"] in ("CHAMPION_DECLARED_SETTING", "SAVED_RECEIPT_REPORTED_SETTING", "NUMERIC_RECEIPT_MENTION")]
    return dict(status="REPORTED_CONTROL_OVERLAP_EXACT_BUILD_UNRESOLVED" if reported else
                "PROPOSED_OR_MENTIONED_NOT_EXECUTION" if matches else "NO_MATCH_IN_FROZEN_CORPUS",
                proposed_value=proposed_value, matching_value_references=len(exact), references=matches,
                untested_everywhere_claim=False, exact_build_testedness="UNKNOWN",
                independent_execution_or_causal_acceptance=False)


SPECS = [
    ("M9", "WMI per-AC contention-window characterization", "WMI", "PDEV_SET_WMM_PARAMS_CMDID",
     "cwmin", "Change only BE CWmin by one qualified discrete value; preserve every other AC/field.",
     "One contention-window coordinate may improve mixed-rate tail fairness without altering PHY/regulatory settings.",
     ["airtime", "backoff", "fairness"]),
    ("M10", "HTT A-MSDU ceiling with A-MPDU held fixed", "HTT", "HTT_H2T_MSG_TYPE_AGGR_CFG",
     "max_num_amsdu_subframes", "Characterize A-MSDU3->2 only after exact API/payload qualification; preserve captured A-MPDU.",
     "A lower A-MSDU ceiling may bound retry amplification while preserving the existing A-MPDU budget.",
     ["aggregation", "queue", "latency"]),
    ("M11", "AME DL lottery scheduling isolation", "AME", "do_lotto", None,
     "Compare documented on/off states only after boolean encoding, baseline and restoration are proven.",
     "A single DL allocation policy may change fairness under heterogeneous queues.",
     ["airtime", "scheduling", "fairness"]),
    ("M12", "AME cross-frame backoff maximum wait", "AME", "cz_cross_frame_max_timeout", None,
     "On a separately qualified backoff-enabled baseline, change only one approved maximum-wait unit; zero disables this timer.",
     "A bounded cross-frame wait may limit scheduler tail delay without changing the existing retry policy.",
     ["backoff", "queue", "latency"]),
    ("M13", "AME multicast descriptor-stall threshold", "AME", "add_stall_bd_mcast_threshold", None,
     "Change one approved descriptor-count step under bounded multicast load; keep scheduler and RF settings fixed.",
     "A descriptor-pressure threshold may trade multicast queue delay against unicast stability.",
     ["queue", "latency", "multicast"]),
    ("M14", "UPH software retry-limit characterization", "UPH", "swr_limit", None,
     "Resolve selector/vector semantics and true state getter before proposing one bounded retry-limit change.",
     "A software retry bound may reduce head-of-line delay; scratch reads cannot demonstrate it.",
     ["retry", "latency", "hidden"]),
    ("M15", "UPH fixed-frame multicast airtime budget", "UPH", "ff_mcast_airtime_limit", None,
     "Identify units/active-mode dependency and true state getter, then reduce one approved budget unit.",
     "A bounded multicast allocation may protect interactive unicast at equal regulatory settings.",
     ["airtime", "multicast", "fairness"]),
]


def candidate_hypotheses(protocols, knobs, references, raw):
    candidates = []
    vault = {p: b.decode("utf-8") for p, b in raw.items() if _role(p) == "vault_stored_source_or_claim"}
    for ident, title, family, selector, field, mutation, hypothesis, terms in SPECS:
        protocol_matches = [r for r in protocols if (r["symbol"].endswith(selector) if family == "WMI" else r["symbol"] == selector)]
        knob_matches = [r for r in knobs if r["name"] == selector and
                        (family == "AME" and r["population"] == "ame_core_module_parameter"
                         or family == "UPH" and r["population"] == "airos_sysctl")]
        require(protocol_matches or knob_matches, f"Candidate control absent: {ident}")
        surfaces = sorted({r["surface"] for r in knob_matches})
        observations = [testedness(surface, None, references) for surface in surfaces]
        support = []
        for path, text in vault.items():
            lines = text.splitlines()
            hits = [i+1 for i, line in enumerate(lines) if sum(bool(re.search(r"\b"+re.escape(term)+r"\b", line, re.I)) for term in terms) >= 2]
            if hits:
                support.append(dict(path=path, lines=hits[:8], match_kind="LEXICAL_TOPIC_OVERLAP_ONLY",
                                    paper_claim_verified=False, hardware_transfer_proven=False))
        novelty = 0 if any(t["status"].startswith("REPORTED") for t in observations) else 2
        hook = 2 if knob_matches else 1
        source_specificity = 2 if any(r.get("description") for r in knob_matches) else 1
        score = hook+source_specificity+novelty+int(bool(support))
        candidates.append(dict(
            id=ident, title=title, family=family, selector=selector, payload_field=field,
            hypothesis=hypothesis, mutation=mutation, proposed_numeric_value=None,
            protocol_refs=[dict(namespace=r["namespace"], symbol=r["symbol"], hex=r["hex"],
                                source=r["source"], line=r["line"], host_maps=r["host_maps"]) for r in protocol_matches],
            host_encoding_domain=(dict(amsdu_subframes=[1, 31], ampdu_subframes=[1, 64],
                                       source=DRIVER+"htt_tx.c", physical_safe_range=None) if family == "HTT" else None),
            control_refs=[dict(id=r["id"], surface=r["surface"], platform_scope=r["platform_scope"],
                               source=r["declaration_source"]) for r in knob_matches],
            testedness=observations if observations else [
                dict(status="WIRE_PAYLOAD_EXPERIMENT_NOT_IDENTIFIED_IN_FROZEN_CORPUS",
                     routine_driver_use="UNKNOWN; common commands may be used normally",
                     exact_build_testedness="UNKNOWN", untested_everywhere_claim=False)],
            vault_refs=support, ranking_score=score,
            ranking_basis=dict(hook_specificity=hook, source_specificity=source_specificity,
                               corpus_novelty=novelty, lexical_support=int(bool(support)),
                               meaning="local triage heuristic, not predicted gain"),
            hardware_testable_conditionally=True, ready_for_hardware_dispatch=False,
            qualification_status="BLOCKED_PENDING_EXACT_BUILD_DOMAIN_AND_RECOVERY",
            gates=["Exact board/build/API/role match and current accepted baseline",
                   "Real writable setter, encoding/units/safe domain and effective state getter",
                   "One changed coordinate; complete coupled-state snapshot and independently qualified restoration",
                   "Bounded isolated canary authority, watchdog, health and unchanged regulatory/calibration state"],
            experiment=dict(primary_metric="worst-station p95 latency", secondary=["aggregate/per-CPE goodput", "p99", "loss", "retries", "Jain", "CPU", "firmware resets"],
                            design="randomized paired ABBA blocks with fixed workload; repetitions preregistered from pilot variance",
                            guardrails=dict(max_goodput_drop_pct=2, max_loss_increase_pp=0, max_p99_regression_pct=0, allowed_firmware_resets=0),
                            rollback="Restore exact captured typed state, then association/uptime/config/health verification; no default guesses",
                            result="NOT_RUN", decision="INCONCLUSIVE"),
            execution_commands=[], expected_gain_pct=None))
    candidates.sort(key=lambda c: (-c["ranking_score"], int(c["id"][1:])))
    for rank, candidate in enumerate(candidates, 1):
        candidate["rank"] = rank
    return candidates


def build_report(manifest=None):
    if manifest is None:
        manifest, inventory, gaps = collect_manifest()
    else:
        current, inventory, gaps = collect_manifest()
        require(type(manifest) is list and all(type(row) is dict and "path" in row for row in manifest),
                "Invalid frozen source manifest")
        require({r["path"] for r in manifest} == {r["path"] for r in current},
                "Source population changed or frozen evidence was omitted; regenerate with an explicit new cutoff")
    raw = read_manifest(manifest)
    protocols, knobs = protocol_catalog(raw), knob_catalog(raw)
    references = tested_references(raw, knobs)
    firmware = firmware_evidence(raw, protocols, inventory)
    for row in knobs:
        row["testedness"] = testedness(row["surface"], None, references)
    candidates = candidate_hypotheses(protocols, knobs, references, raw)
    return dict(
        schema_version=1, task_id=TASK_ID, stage="Stage29A", mode="OFFLINE_STATIC_MINING_NO_ACTUATION",
        automatic_execution_allowed=False, physical_acceptance=False, new_physical_observations=0,
        firmware_payload_exported=False, source_manifest=manifest, inventory_gaps=gaps,
        source_cutoff=dict(ledger_original_path=LIVE_LEDGER, ledger_snapshot_path=LEDGER,
                           ledger_sha256=PINS[LEDGER],
                           rule="Explicit immutable dated cutoff; no claim of equality to the later live ledger"),
        coverage=dict(exhaustive_for_frozen_declarations=True, all_remaining_proprietary_opcodes=False,
                      firmware5_mining_complete=False, runtime_test_registry_complete=False,
                      tested_population="Frozen top-level stage*.json plus pinned Champion cutoff declarations; older bench trees and external tests not exhaustively joined",
                      vault_population="Stored source/claim/topic notes excluding mirrored futuramax/ docs; lexical matches are not paper verification",
                      ame_cpe_parameter_names="UNKNOWN: held report gives count48 but only AP57 names",
                      curated_ame_attrs_are_module_parameters=False),
        firmware=firmware, protocol_summary=dict(by_namespace=dict(Counter(r["namespace"] for r in protocols)),
                                                by_kind=dict(Counter(r["kind"] for r in protocols)),
                                                unresolved=sum(r["value"] is None for r in protocols),
                                                counts_are_executable_opcodes=False),
        protocol_declarations=protocols, knob_summary=dict(by_population=dict(Counter(r["population"] for r in knobs)),
                                                         physically_qualified_safe_ranges=0),
        knob_declarations=knobs, setting_references=references, candidates=candidates,
        source_conflicts=[
            dict(topic="M3/M5 identity", stage24="M3 chainmask; M5 host AQL/custom target TDMA",
                 stage25="M3 TXQ CoDel; M5 asymmetric ACK pacing", rule="namespace labels by stage/build/control"),
            dict(topic="Target subtype routing", legacy=PB_MAP, reviewed=CONSUMERS,
                 legacy_route="0x17 ->9b5c02", reviewed_route="23->9b2578->9b7264;30->9b24c5->9b77c4",
                 status="CONFLICT_RETAINED; reviewed model conditional on LITBASE; indirect slots remain unmapped"),
            dict(topic="M4 aliases", aliases=["power_Balance_adjust", "dl_ul_Symbol_adjust"],
                 status="NOT_PRESENT_IN_HELD_AP57; Stage24D remaps to other real parameters; not newly writable controls"),
        ],
        decision="KEEP_BOUNDED_MINER_AND_RANKED_HYPOTHESES; DO_NOT_DISPATCH",
    )


def validate_report(report):
    require(type(report) is dict and "source_manifest" in report, "Source-bound report required")
    expected = build_report(report["source_manifest"])
    encode = lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), allow_nan=False)
    require(encode(report) == encode(expected), "Report differs from recomputed frozen evidence")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", help="Validate a saved local report; no execution")
    args = parser.parse_args(argv)
    if args.validate:
        validate_report(load_json(read_local(args.validate, limit=8*1024*1024)))
        print("PASS frozen Stage29A report; hardware dispatch remains blocked")
    else:
        report = build_report()
        path = local_path(ROOT/OUTPUT)
        require(path.parent.is_dir(), "Existing local artifact directory required")
        path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(f"WROTE {OUTPUT}: {len(report['protocol_declarations'])} declarations, {len(report['knob_declarations'])} knobs, 7 gated candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
