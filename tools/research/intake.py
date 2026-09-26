#!/usr/bin/env python3
"""FuturaMAX R0 intake: register + hash every external Deep Research input.

Covers: provenance capture for research/intake/manifest.yaml, byte-exact raw copies
under research/raw/<provider>/<run_id>/, SHA-256 hashing of primary docs and of every
saved-page asset bundle. Keywords: intake, provenance, manifest, sha256, run_id.
Read when: a new external model report arrives and must be registered before anyone
interprets it. Never mutates futuramaxresearch/ (the operator drop zone) - read-only.
Verdict: CURRENT. Re-runnable; run_id is content-derived so re-runs are idempotent.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DROP = ROOT / "futuramaxresearch"
RAW = ROOT / "research" / "raw"
INTAKE = ROOT / "research" / "intake"


@dataclass
class Input:
    provider: str
    model_label: str
    primary: Path
    asset_dir: Path | None = None
    notes: str = ""
    run_id: str = field(default="", init=False)


INPUTS = [
    Input("chatgpt", "ChatGPT Deep Research (exact model unrecorded)", DROP / "chatgpt.md"),
    Input("google", "Google/Gemini Deep Research (exact model unrecorded)", DROP / "googleresearch.md"),
    Input("qwen", "Qwen Max Deep Research (exact model unrecorded)", DROP / "qwenmax.pdf"),
    Input(
        "perplexity",
        "Perplexity Deep Research (exact model unrecorded)",
        DROP / "FuturaMAX  Evidence-Based Limits and Opportunities on Ubiquiti airMAX AC (QCA988x) Hardware.md",
        None,
        "Supplied 2026-08-08 after the first six runs. Uses [^n] footnote citations rather than inline URLs.",
    ),
    Input(
        "glm",
        "Z.ai GLM-5.2 (per saved page title)",
        DROP / "glm" / "Z.ai - Advanced AI Chatbot & Agent powered by GLM-5.2.html",
        DROP / "glm" / "Z.ai - Advanced AI Chatbot & Agent powered by GLM-5.2_files",
        "Browser-saved chat page; sidebar chrome present in text extraction.",
    ),
    Input(
        "grok",
        "xAI Grok (exact model unrecorded)",
        DROP / "grok" / "FutrMAX airMAX AC firmware research evidence - Grok.html",
        DROP / "grok" / "FutrMAX airMAX AC firmware research evidence - Grok_files",
        "Browser-saved chat page; UI language Spanish; sidebar chrome present.",
    ),
    Input(
        "mistral",
        "Mistral Le Chat (exact model unrecorded)",
        DROP / "mistral" / "Ubiquiti airMAX Optimization.html",
        DROP / "mistral" / "Ubiquiti airMAX Optimization_files",
        "Browser-saved chat page; contains the verbatim operator prompt at the top.",
    ),
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_tree(d: Path) -> tuple[str, int, int]:
    """Deterministic hash over an asset bundle: sha256 of sorted 'relpath sha256' lines."""
    entries = []
    total = 0
    for p in sorted(d.rglob("*")):
        if p.is_file():
            digest = sha256_file(p)
            rel = p.relative_to(d).as_posix()
            entries.append(f"{rel} {digest}")
            total += p.stat().st_size
    blob = "\n".join(entries).encode()
    return hashlib.sha256(blob).hexdigest(), len(entries), total


def yaml_escape(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    if not DROP.is_dir():
        print(f"FATAL: drop zone missing: {DROP}", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records = []
    missing = []

    for inp in INPUTS:
        if not inp.primary.is_file():
            missing.append(str(inp.primary))
            continue

        digest = sha256_file(inp.primary)
        inp.run_id = f"{inp.provider}-{digest[:8]}"
        dest_dir = RAW / inp.provider / inp.run_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / inp.primary.name
        if not dest.exists() or sha256_file(dest) != digest:
            shutil.copy2(inp.primary, dest)
        verify = sha256_file(dest)
        if verify != digest:
            print(f"FATAL: copy hash mismatch for {inp.primary}", file=sys.stderr)
            return 2

        asset = None
        if inp.asset_dir and inp.asset_dir.is_dir():
            tree_hash, n_files, n_bytes = hash_tree(inp.asset_dir)
            index = dest_dir / "asset_bundle_index.txt"
            lines = []
            for p in sorted(inp.asset_dir.rglob("*")):
                if p.is_file():
                    lines.append(f"{sha256_file(p)}  {p.relative_to(inp.asset_dir).as_posix()}")
            index.write_text("\n".join(lines) + "\n", encoding="utf-8")
            asset = {
                "original_path": inp.asset_dir.relative_to(ROOT).as_posix(),
                "retained_in_place": True,
                "tree_sha256": tree_hash,
                "file_count": n_files,
                "bytes": n_bytes,
                "index_file": index.relative_to(ROOT).as_posix(),
            }

        st = inp.primary.stat()
        records.append(
            {
                "run_id": inp.run_id,
                "provider": inp.provider,
                "model_label": inp.model_label,
                "primary_original_path": inp.primary.relative_to(ROOT).as_posix(),
                "primary_raw_path": dest.relative_to(ROOT).as_posix(),
                "primary_sha256": digest,
                "primary_bytes": st.st_size,
                "file_mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                "registered_at": now,
                # Wave-1 prompt recovered verbatim from the saved grok/mistral pages; identity for
                # chatgpt/google/qwen is INFERRED from all six returning the same 11-section template.
                "prompt_recorded": (
                    "inputs/prompts/external-deep-research-prompt.md (VERBATIM)"
                    if inp.provider in ("grok", "mistral")
                    else "inputs/prompts/external-deep-research-prompt.md (INFERRED same prompt)"
                ),
                "run_started_at": "UNKNOWN",
                "run_completed_at": "UNKNOWN",
                "source_link_count": "PENDING_EXTRACTION",
                "asset_bundle": asset,
                "notes": inp.notes,
            }
        )

    INTAKE.mkdir(parents=True, exist_ok=True)
    (INTAKE / "manifest.json").write_text(json.dumps({"generated_at": now, "runs": records}, indent=2), encoding="utf-8")

    out = [
        "# FuturaMAX research intake manifest",
        "# Summary: provenance record for every external Deep Research run ingested at R0.",
        "# Keywords: intake, provenance, run_id, sha256, raw preservation, asset bundle.",
        "# Read when: you need to know where a claim's originating report came from.",
        "# Verdict: GENERATED - do not hand-edit; regenerate with tools/research/intake.py.",
        "# Rule: raw primary documents are byte-exact copies; asset bundles stay at their",
        "# original drop-zone path and are pinned by a per-file sha256 index.",
        "",
        f"generated_at: {now}",
        f"generator: tools/research/intake.py",
        "runs:",
    ]
    for r in records:
        out.append(f"  - run_id: {r['run_id']}")
        for k in (
            "provider",
            "model_label",
            "primary_original_path",
            "primary_raw_path",
            "primary_sha256",
            "primary_bytes",
            "file_mtime_utc",
            "registered_at",
            "prompt_recorded",
            "run_started_at",
            "run_completed_at",
            "source_link_count",
        ):
            v = r[k]
            out.append(f"    {k}: {yaml_escape(str(v)) if isinstance(v, str) else v}")
        if r["asset_bundle"]:
            out.append("    asset_bundle:")
            for k, v in r["asset_bundle"].items():
                out.append(f"      {k}: {yaml_escape(str(v)) if isinstance(v, str) else str(v).lower() if isinstance(v, bool) else v}")
        else:
            out.append("    asset_bundle: null")
        out.append(f"    notes: {yaml_escape(r['notes'])}")
    if missing:
        out.append("missing_declared_inputs:")
        for m in missing:
            out.append(f"  - {yaml_escape(m)}")
    (INTAKE / "manifest.yaml").write_text("\n".join(out) + "\n", encoding="utf-8")

    print(f"registered {len(records)} runs -> {INTAKE / 'manifest.yaml'}")
    for r in records:
        print(f"  {r['run_id']:<20} {r['primary_bytes']:>9} B  {r['primary_original_path']}")
    if missing:
        print("MISSING:", *missing, sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
