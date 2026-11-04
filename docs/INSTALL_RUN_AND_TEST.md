<!-- doc-head: Install, run and test commands for the public checkout, checked against the repo files on 2026-11-04 -->
Que cubre: entorno Python, archivos de requirements, comando de verificacion offline y pytest, con el estado observado.
Leer cuando: vas a instalar el repo, correr la verificacion offline o interpretar sus fallas actuales.
Estado: vigente al 2026-11-04 (auditoria de documentacion; no se cambio codigo ni dependencias).
<!-- /doc-head -->

# Install, run and test

The repository has no `package.json`, `pyproject.toml`, `setup.py` or `Makefile`.
It is a set of Python scripts plus `pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

## Install

```bash
python3.12 -m venv .venv
```

```bash
. .venv/bin/activate
```

```bash
pip install -r requirements-audit.txt pyyaml
```

| File | Contents | Use |
| --- | --- | --- |
| `requirements-audit.txt` | `pytest==8.3.5`, `numpy==1.26.4`, `scipy==1.17.1` | Offline verifier (`tools/verify/verify_chatgpt_audit_1afaeb7.py`). |
| `requirements-release-v22.txt` | `-r requirements-audit.txt`, `simpy==4.1.2`, `pymoo==0.6.2` | Simulation / Pareto tests (`simpy`, `pymoo`). |
| `requirements-public-projection.txt` | `pytest`, `paramiko`, `scipy`, `pyelftools`, `capstone` | Public-projection tooling and binary-inspection tests. |

`pyyaml` is imported by `tests/test_chatgpt_audit_1afaeb7_regressions.py`,
`tests/test_chatgpt_audit_pb_campaign.py` and `tests/test_pb_060_070_autonomous_search_and_phy_gate.py`
but is not listed in any requirements file, so it is installed explicitly above.

## Run the offline verifier

```bash
python tools/verify/verify_chatgpt_audit_1afaeb7.py
```

It runs 11 test files under pytest and prints a JSON report (`status`, `exit_code`, `tests`).
Options: `--root`, `--private` (also runs separately held firmware checks), `--collect-only`, `--junitxml`, `--report`.
It does not touch the network, radios or firmware.

## Run the test suite

```bash
python -m pytest
```

## Observed status (2026-11-04, Python 3.12 and 3.13)

| Command | Result |
| --- | --- |
| verifier with only `requirements-audit.txt` | `"status": "FAILED"`, `exit_code` 2: `ModuleNotFoundError: No module named 'yaml'`. |
| verifier with `pyyaml` added | `"status": "FAILED"`, `exit_code` 1: 118 passed, 36 failed, all in `tests/test_chatgpt_audit_wa_kit.py` (`IndexError: string index out of range`). |
| `python -m pytest --collect-only` with `requirements-audit.txt` + `pyyaml` | 6929 tests collected, 166 collection errors. Most come from modules not included in this public checkout (for example `controller.multiradio_golden_profile_applicator`, `tools.research.closed_loop_research_reactor`) and from optional packages (`simpy`, `pymoo`, `elftools`, `Crypto`). |

These are code/test issues outside the scope of a documentation-only change; they are recorded here so the
README commands are not read as passing.
