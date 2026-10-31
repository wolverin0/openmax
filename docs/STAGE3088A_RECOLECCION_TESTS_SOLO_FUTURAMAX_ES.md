<!-- doc-head: Stage 3088A (W428) ES: pytest.ini excluye de la recoleccion las copias desechables del repo (*_disposable), una instantanea de corrida (native_run_*) y los clones de terceros de tools/research; la recoleccion pasa de 5040 tests con 2131 errores (cortada) a 25305 tests con 27 errores; la corrida completa se detuvo al 33,7 % por memoria baja del sistema (8192 pasan, 147 fallan, 115 errores en ese tramo) -->
Que cubre: que se excluyo y por que, cifras de antes y despues, y los errores reales que quedan agrupados por causa.
Estado: solo configuracion de tests. Nada movido, borrado ni editado fuera de pytest.ini. Corrida completa incompleta (ver 3).
Datos maquina: artifacts/autoresearch/wave428_test_collection.json.
Leer cuando: antes de correr toda la suite o de interpretar su resultado.
<!-- /doc-head -->
# Stage 3088A: la suite por defecto solo junta tests de FuturaMAX (W428)

## 1. Que se excluyo (pytest.ini, norecursedirs)

- **Copias desechables del repo:** `*_disposable` (6 de W391 en tools/verify, 2 en tools/panel2, 1 en tools/panel3, 1 en tools/watchdog_acceptance) y `native_run_*` (instantanea del watchdog).
- **Clones de terceros:** `tools/research/AutoResearchClaw` (con su .venv), `tools/research/hyperresearch`, `tools/research/srccache` (ath10k-ct).
- **Defaults de pytest:** se mantienen en la primera linea, porque `norecursedirs` los reemplaza.
- **Causa del choque (CONFIRMED):** cada copia desechable trae su propio paquete `tests/`. Pytest importaba `tests.test_X` desde la copia y el modulo real fallaba con ModuleNotFoundError: unos 20 000 tests reales quedaban afuera.

## 2. Recoleccion (CONFIRMED, `pytest --collect-only`)

| | Tests | Errores |
| :-- | --: | --: |
| Antes | 5040 | 2131 (cortada: sin `--continue-on-collection-errors` no corre nada) |
| Despues | 25305 | 27 |

**Errores reales que quedan (no se arreglan en esta ola):**
1. **25 suites** (test_stage1548a_to_1553a ... test_stage2496a_to_2501a): ValueError al importar, "same-run measured AA baseline required before benchmark". Importan runners de banco que arman un contrato del harness de autoresearch a nivel de modulo, y el harness ahora exige banda A/A de la misma corrida.
2. **1 test** (test_stage69a_m5_xw_crossgen_sweep): ImportError, el modulo ya no exporta `DEFAULT_RECEIPT_PATH`.
3. **1 script** (orchestration/autoresearch/stage13_sync_20261025/run_original_historical_test.py): no es un test, pero su nombre termina en `_test.py`. Al importarlo intenta crear un archivo que ya existe (FileExistsError).

## 3. Corrida completa

- **Antes:** referencia W391, con las mismas testpaths y `--continue-on-collection-errors`: 4502 pasan, 2418 fallan, 799 errores.
- **Despues:** con el mismo guard offline de W391, en serie. Claude Code la detuvo al 33,7 % (8533 tests, unos 26 min) por memoria baja del sistema, y no se relanzo.
  - En ese tramo: 8192 pasan, 147 fallan, 115 errores, 79 saltados.
  - **PENDIENTE:** el total y la agrupacion por causa de fallas de ejecucion. El JUnit se escribe al final y no llego a generarse.
- **Para completarla:** con memoria libre, `python -m pytest -q --continue-on-collection-errors --junitxml=<archivo>`, con el guard de `tools/verify/run_wave391_offline_full_pytest.py`.
