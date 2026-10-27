"""Cross-block offline acceptance and fail-closed provenance regressions."""
from pathlib import Path

from tools.verify import stage779_822_offline_common as c
from tools.verify import verify_stage822a_ground_up_v13_822stage_gate as gate

ROOT = Path(__file__).resolve().parents[1]


def test_all_requested_stages_and_five_pillar_structure():
    from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
    result = gate.build(ROOT)
    assert result['compliant'], result
    assert len(result['stages_verified']) == 5
    assert len(result['first_block_rechecked']) == 5
    assert result['live_target_accepted'] is False
    assert result['physical_acceptance'] == 'UNKNOWN'
    assert audit_stage_receipt_5pillars(result)['compliant']
    assert result['docs_audit']['compliant']


def test_empty_checkout_fails_without_executing_producers(tmp_path):
    result = gate.build(tmp_path)
    assert not result['compliant']
    assert all(not row['compliant'] for row in result['stages_verified'])
    assert not result['boundary']['ssh_executed']


def test_helper_and_image_tampering_is_rejected(tmp_path):
    for label in ['tools/builder.py', 'tests/suite.py', 'kit/helper.sh', 'kit/image.bin', 'kit/original.bin']:
        path=tmp_path/label;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'original')
    data=c.receipt(817,'fixture',[])
    data.update(helper_script='kit/helper.sh',helper_sha256=c.snapshot(tmp_path,'kit/helper.sh')['sha256'],
                images=[dict(path='kit/image.bin',sha256=c.snapshot(tmp_path,'kit/image.bin')['sha256'],
                             source='kit/original.bin',source_sha256=c.snapshot(tmp_path,'kit/original.bin')['sha256'])])
    c.save(tmp_path,'stage817a_fixture',data,'fixture\n')
    check=lambda: c.verify_stage(tmp_path,817,'tools/builder.py','stage817a_fixture','tests/suite.py')
    assert check()['compliant']
    (tmp_path/'kit/helper.sh').write_text('tampered')
    assert 'helper hash mismatch' in check()['failures']
    (tmp_path/'kit/helper.sh').write_bytes(b'original')
    (tmp_path/'kit/image.bin').write_text('tampered')
    assert any('image hash mismatch' in f for f in check()['failures'])


def test_document_budget_is_strict_and_requires_paired_header(tmp_path):
    docs=tmp_path/'docs';docs.mkdir()
    path=docs/'example.md';path.write_text('<!-- doc-head: example -->\nbody\n')
    assert not gate.audit_docs(tmp_path)['compliant']
    path.write_text('<!-- doc-head: example -->\n<!-- /doc-head -->\nbody\n')
    assert gate.audit_docs(tmp_path)['compliant']
    path.write_text(path.read_text() + '\n'*177)
    assert not gate.audit_docs(tmp_path)['compliant']


def test_scorecard_keeps_live_unknown():
    result=c.read_json(ROOT,'artifacts/autoresearch/stage821a_960window_cross_lane_master_scorecard.json')
    assert result['target_windows'] == 960
    assert result['accepted_live_windows'] is None
    assert result['live_target_accepted'] is False
    assert all(lane['accepted_live_windows'] is None for lane in result['lanes'])


def test_shell_helpers_reject_unsupported_activation():
    # Shell execution and stubbed firewall tests live in the isolated kit suite.
    pb=(ROOT/'firmware/openwrt/common/fmx_pb060_triple_patch_loader.sh').read_text(encoding='utf-8')
    ltu=(ROOT/'firmware/ltu_safe_kit/fmx_ltu_4096qam_12x_safe_kit.sh').read_text(encoding='utf-8')
    assert '--inspect-only' in pb and 'BLOCKED' in pb
    assert '--inspect-only' in ltu and 'BLOCKED' in ltu
    assert 'pkill' not in ltu and 'killall' not in ltu
