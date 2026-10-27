"""Disposable Git fixtures; no actual remote or radio access."""
import subprocess

import pytest

from tools.verify import verify_stage826a_public_git_hygiene_and_push_gate as gate


def run(root,*args):
    return subprocess.run(['git',*args],cwd=root,capture_output=True,check=True)


def repository(tmp_path):
    run(tmp_path,'init','-q')
    (tmp_path/'.gitignore').write_text('*.bin\n*.ko\n*.sqfs\n.env*\n*[hH][aA][cC][kK][eE][rR][oO][nN][eE]*\n*STAGE81A*\n*stage98c*\n')
    return tmp_path


def test_actual_index_not_worktree_is_audited(tmp_path):
    root=repository(tmp_path);p=root/'public.py';p.write_text("message='safe'\n")
    run(root,'add','--','.gitignore','public.py')
    p.write_text('password="'+ 'actual'+'credential'+'value"\n')
    assert gate.audit(root)[0]['compliant']
    run(root,'add','public.py')
    result,_,findings=gate.audit(root)
    assert not result['compliant']
    assert any(f['rule']=='literal_credential' for f in findings)
    assert 'actualcredentialvalue' not in str(result)


@pytest.mark.parametrize('name',['dump.bin','module.KO','image.sqfs','MixedHaCkErOnE.md','docs/STAGE81A_private.md','tools/stage98c_private.py'])
def test_forbidden_paths(name):
    assert gate.path_reason(name)


def test_ignored_but_force_tracked_binary_is_rejected(tmp_path):
    root=repository(tmp_path);(root/'dump.bin').write_bytes(b'firmware\0')
    run(root,'add','-f','dump.bin')
    assert not gate.audit(root)[0]['compliant']


def test_force_tracked_ignored_text_is_rejected(tmp_path):
    root=repository(tmp_path)
    with (root/'.gitignore').open('a') as stream:stream.write('local_only.py\n')
    (root/'local_only.py').write_text('public_looking_but_private=True\n')
    run(root,'add','-f','local_only.py')
    result,_,findings=gate.audit(root)
    assert not result['compliant']
    assert any(x['rule']=='ignored_but_tracked' for x in findings)


def test_policy_and_secret_findings_never_echo_values():
    blob=('password="'+'some_real_value'+'"\n').encode()
    findings=gate.content_findings(blob)
    assert findings and 'some_real_value' not in str(findings)
    assert gate.content_findings(b'example account',private_terms=['account'])


def test_missing_ignore_rule_fails_even_with_safe_index(tmp_path):
    root=repository(tmp_path);(root/'.gitignore').write_text('*.bin\n')
    run(root,'add','.gitignore')
    assert not gate.audit(root)[0]['compliant']


@pytest.mark.parametrize('punctuation',['(',')','[',']'])
def test_punctuation_is_not_a_credential_bypass(punctuation):
    blob=('password="'+ 'synthetic'+punctuation+'credential'+'"').encode()
    assert any(x['rule']=='literal_credential' for x in gate.content_findings(blob))


def test_parent_symlink_cannot_escape_publication_plan(tmp_path,monkeypatch):
    root=repository(tmp_path/'repo') if (tmp_path/'repo').mkdir() is None else None
    outside=tmp_path/'outside';outside.mkdir();(outside/'secret.py').write_text('sensitive')
    try:
        (root/'linked').symlink_to(outside,target_is_directory=True)
    except OSError:
        pytest.skip('directory symlink privilege unavailable')
    original=gate.git
    def git_fixture(repo,*args,**kwargs):
        if args[:4]==('ls-files','--cached','--others','--exclude-standard'):
            return b'linked/secret.py\0'
        return original(repo,*args,**kwargs)
    monkeypatch.setattr(gate,'git',git_fixture)
    result,selected,findings=gate.audit(root,plan=True)
    assert not selected
    assert any(x['rule']=='path_outside_checkout' for x in findings)
