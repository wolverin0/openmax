"""Existing V7 pinned connection body, bound to the verified fresh OpenWrt host key."""
import ast
import hashlib
from pathlib import Path
import paramiko
HERE = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def ap_client():
    provider = HERE / 'panel1_cutover_preflight_20261019.py'
    if sha(provider.read_bytes()) != '9bb2fae2fce44c07b8b6f5bd67c1aa53e907c9b9dfc5fe2831b836c822ba492b':
        raise RuntimeError('CREDENTIAL_PROVIDER_CHANGED')
    fn = next(n for n in ast.parse(provider.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='credentials')
    pointer = next(n for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pointer' for t in n.targets))
    values = {}
    with Path(ast.literal_eval(pointer.value.args[0])).open(encoding='utf-8') as stream:
        for line in stream:
            key, sep, value = line.strip().partition('=')
            if sep and key in {'UBNT_CPE_USER','UBNT_CPE_PASSWORD'}:
                values[key] = value.strip().strip(chr(34)).strip(chr(39))
            if len(values)==2:
                break
    client = paramiko.SSHClient()
    class Pin(paramiko.MissingHostKeyPolicy):
        def missing_host_key(self, connection, host, key):
            if sha(key.asbytes()) != 'e796c11c4a833e08bdc74eeff07482b72160be50385cf5ed3a6a6362c9a1c116':
                raise RuntimeError('AP_SSH_PIN_CHANGED')
            connection.get_host_keys().add(host,key.get_name(),key)
    client.set_missing_host_key_policy(Pin())
    try:
        client.connect('fe80::1ae8:29ff:fe75:55a2%27',username='root',password=values['UBNT_CPE_PASSWORD'],timeout=8,banner_timeout=8,auth_timeout=8,look_for_keys=False,allow_agent=False)
        return client
    except BaseException:
        client.close()
        raise
    finally:
        values.clear()
