# PUBLIC_REDACTED_DERIVATIVE; new synthetic fixtures, not native replay
"""Public pure-parser and disabled-transport contracts, no private input files."""
import importlib
import inspect
import socket
import pytest
from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer, read_bmi_varint, write_bmi_varint
from tools.autoresearch.run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit import spectral_efficiency

def test_synthetic_varint_vectors_and_truncation():
    for value in [0, 127, 128, 16384, 0xffffffff]:
        encoded=write_bmi_varint(value)
        assert read_bmi_varint(encoded,0)==(value,len(encoded))
    for raw in [b'', b'\x80', b'\xff'*6]:
        with pytest.raises(ValueError): read_bmi_varint(raw,0)

def test_synthetic_sgmt_invalid_inputs_cannot_validate():
    for raw in [b'', b'\x00'*16, b'not-firmware'*4]:
        with pytest.raises(ValueError): SgmtContainer.from_bytes(raw)

def test_synthetic_spectral_arithmetic_domain():
    assert spectral_efficiency(120,40)==3
    for goodput,width in [(1,0),(-1,20),(float('nan'),20),(1,float('inf'))]:
        with pytest.raises(ValueError): spectral_efficiency(goodput,width)

def test_public_acquisition_is_disabled_before_socket(monkeypatch):
    modules=[importlib.import_module('tools.autoresearch.'+name) for name in
      ['stage861_866_common','stage879_884_common','stage897_900_live_common']]
    def denied(*args,**kwargs): raise AssertionError('socket attempted')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(socket.socket,'connect',denied)
    for module,names in zip(modules,[['credential','capture'],['capture'],['connect','run']]):
        for name in names:
            fn=getattr(module,name)
            signature=inspect.signature(fn)
            kwargs={key:None for key,p in signature.parameters.items() if p.default is inspect.Parameter.empty}
            with pytest.raises(RuntimeError,match='PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED'):
                fn(**kwargs)
