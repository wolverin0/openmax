"""Historical WA actuator aliases are retired, never silently mapped to v13."""
from pathlib import Path
import importlib
import os
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
VERSIONS=((11,284,661),(12,316,715))


@pytest.mark.parametrize('version,windows,stage',VERSIONS)
def test_retirement_contract_is_present_without_executing_original(version,windows,stage):
    text=(ROOT/f'firmware/openwrt/common/fmx_wa_v{version}_{windows}window_field_kit.sh').read_text(encoding='utf-8')
    assert 'PLANNED_RETIRED' in text
    assert 'initial_quantum' not in text and '|| true' not in text
    assert '/sys/' not in text and 'exec ' not in text


@pytest.mark.parametrize('version,windows,stage',VERSIONS)
@pytest.mark.parametrize('args',[[],['--inspect'],['--inspect-only'],['--dry-run'],['--apply'],['--apply','--identity','unused'],['phy0','eth0']])
def test_retired_entrypoints_never_invoke_environment_commands(tmp_path,version,windows,stage,args):
    bindir=tmp_path/'bin';bindir.mkdir()
    log=tmp_path/'calls.txt'
    for tool in ('uci','tc','sysctl','ubus','id','uname','jsonfilter','ethtool','readlink','cat','tee','basename','find','ip','ebtables','modprobe'):
        (bindir/tool).write_text('#!/bin/sh\nprintf "%s\\n" "$0 $*" >> "$RETIRED_CALL_LOG"\nexit 17\n',encoding='utf-8',newline='\n')
    shell_dir='/'+bindir.drive[0].lower()+bindir.as_posix()[2:]
    helper=ROOT/f'firmware/openwrt/common/fmx_wa_v{version}_{windows}window_field_kit.sh'
    command=f'PATH="{shell_dir}:$PATH";export PATH;exec /usr/bin/sh "{helper.as_posix()}" '+ ' '.join(args)
    result=subprocess.run(['C:/Program Files/Git/bin/bash.exe','-c',command],
                          env=dict(os.environ,RETIRED_CALL_LOG=log.as_posix()),capture_output=True,text=True)
    inspect=not args or args[0] in ('--inspect','--inspect-only','--dry-run')
    if inspect:
        assert result.returncode==0 and 'PLANNED_RETIRED' in result.stdout
    else:
        assert result.returncode==64 and 'RETIRED' in result.stderr
    assert 'fmx_wa_v13_344window_field_kit.sh' in result.stdout+result.stderr
    assert 'APPLIED_VERIFIED' not in result.stdout and 'KIT_OK' not in result.stdout
    assert not log.exists()


@pytest.mark.parametrize('version,windows,stage',VERSIONS)
def test_generators_emit_identical_retirement_without_auxiliary_mutators(tmp_path,version,windows,stage):
    module=importlib.import_module(f'tools.firmware.build_stage{stage}a_wa_champion_v{version}_{windows}window_field_rollout_kit')
    helper=ROOT/f'firmware/openwrt/common/fmx_wa_v{version}_{windows}window_field_kit.sh'
    assert module.build_helper_script()==helper.read_text(encoding='utf-8')
    report=module.build(tmp_path)
    assert report['status']=='RETIRED' and report['runtime_acceptance']=='UNKNOWN'
    assert report['activation_allowed'] is False and report['automatic_alias'] is False
    assert report['historical_reported_windows']==windows
    assert 'verified_metrics' not in report
    assert (tmp_path/module.HELPER_REL).read_bytes()==helper.read_bytes()
    assert not (tmp_path/'firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh').exists()
    doc=(tmp_path/'docs'/f'{module.STEM.upper()}.md').read_text(encoding='utf-8')
    assert len(doc.splitlines())<180 and doc.count('<!-- doc-head:')==1 and doc.count('<!-- /doc-head -->')==1


def test_historical_v12_auxiliary_guard_generation_is_disabled():
    from tools.firmware.build_stage715a_wa_champion_v12_316window_field_rollout_kit import build_htt_guard
    with pytest.raises(RuntimeError,match='RETIRED'):
        build_htt_guard()
