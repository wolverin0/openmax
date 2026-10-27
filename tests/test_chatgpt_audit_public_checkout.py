"""Public entrypoints and links need no private raw, operator guide or vendor dump."""
from pathlib import Path
import importlib

from tools.verify.verify_chatgpt_audit_1afaeb7 import (
    CORE_TESTS,available_paths,missing_readme_links,
)

ROOT=Path(__file__).resolve().parents[1]


def test_readme_targets_exist_in_public_tree():
    assert not missing_readme_links((ROOT/'README.md').read_text(encoding='utf-8'),available_paths(ROOT))


def test_link_check_cannot_be_satisfied_by_private_disk_file():
    assert missing_readme_links('[private](docs/private.md)',{'README.md'})==['docs/private.md']


def test_public_core_imports_without_running_producers():
    for name in ['workloads.flent_orchestrator','analysis.regression_gate.gatekeeper',
                 'controller.pb_060_070_autonomous_search_and_phy_gate',
                 'tools.qca988x.sgmt_container_inspector','firmware.xtensa_sgmt_surgical_patcher']:
        assert importlib.import_module(name)
    assert all((ROOT/path).is_file() for path in CORE_TESTS)
