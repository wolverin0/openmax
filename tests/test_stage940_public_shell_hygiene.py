"""Bounded extensionless source formats retain privacy and binary filtering."""
import pytest

from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import (
    path_reason, source_format_findings, content_findings)

KIT = 'firmware/openwrt/pbe5ac_gen2_ptp_kit/'


@pytest.mark.parametrize('path', [KIT+'99-fmx-pbe5ac-ptp',
    KIT+'files/etc/uci-defaults/99-fmx-pbe5ac-ptp'])
def test_known_extensionless_shell_requires_actual_shebang(path):
    assert path_reason(path) is None
    assert not source_format_findings(path, b'#!/bin/sh\nexit 0\n')
    assert source_format_findings(path, b'private text without a script header')


@pytest.mark.parametrize('path', [KIT+'public_release_v3/99-fmx-old',
    KIT+'unknown_source', KIT+'99-fmx-data.bin', KIT+'99-fmx-module.ko'])
def test_unknown_formats_and_binary_dumps_stay_blocked(path):
    assert path_reason(path)


def test_checksum_format_is_narrow_and_paths_cannot_escape():
    path = KIT+'SHA256SUMS'
    assert path_reason(path) is None
    assert not source_format_findings(path, ('a'*64+'  99-fmx-pbe5ac-ptp\n').encode())
    for text in ['not a checksum', 'a'*64+'  ../outside.sh\n', 'a'*64+'  /absolute.sh\n', '']:
        assert source_format_findings(path, text.encode())
    assert path_reason('arbitrary/SHA256SUMS')


def test_allowlisted_format_cannot_bypass_sensitive_content():
    key = 'pass'+'word'
    assert content_findings(('#!/bin/sh\n'+key+'=fixture-sensitive-example\n').encode())
    assert content_findings(b'#!/bin/sh\n\0')
