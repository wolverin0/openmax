<!-- doc-head -->
*STAGE2000A — Disección de ubntspecd, parada espectral e inicializador priv+0x10*
# STAGE 2000A — ubntspecd y priv+0x10

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `ubntspecd` y de los módulos WA/XC. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 1998A — cómo se registra y cómo se dispara
- `CONFIRMED`: ambos `ubntspecd` miden **47192** bytes y usan **ioctl**. Imprimen `ss_pid`, `ss_fft_period`, `ss_period`, la lista de canales y el mensaje de desincronización con DFS.
- `CONFIRMED`: `ath_dev.ko` importa **`request_threaded_irq`** y **`free_irq`**. Por eso la búsqueda de `request_irq` de la wave anterior daba cero: el handler es **enhebrado**.
- `CONFIRMED`: `ath_spectral_filter_init` (0x27c00, 124 B) hace tres llamadas relocalizadas, coherente con registrar el handler por el import enhebrado.
- `INFERRED`: `ubntspecd` dispara el escaneo por ioctl y configura `ss_period` / `ss_fft_period`.
- `INFERRED`: parar el demonio o llamar a `ath_spectral_filter_stop` libera el handler y silencia el IRQ, porque existe `free_irq` y el camino de datos es independiente.
- `UNKNOWN`: si el TX/RX normal se ve afectado. No se midió.

## 2. Stage 1999A — priv+0x10 no se resuelve por offset
- `CONFIRMED`: hay **4178** stores con inmediato 0x10 en WA y XC `umac.ko` (2089 por módulo).
- `CONFIRMED`: **514** caen en funciones de la familia attach/init/alloc/setup/create.
- `CONFIRMED`: **176** usan el registro base `s0`.
- `REFUTED`: que escanear `sw reg,0x10(base)` identifique el inicializador. El offset 0x10 es un campo pequeño omnipresente; el censo lo demuestra con 4178 candidatos.
- `UNKNOWN`: qué función de attach guarda el puntero de estadísticas en `priv+0x10`.
- `UNKNOWN`: cuál de los 42 escritores de 0xb4/0xdc es el real.

## 3. Consecuencia
- El registro del IRQ es enhebrado y liberable; la parada del demonio es la palanca natural.
- El inicializador de `priv+0x10` no se puede aislar por offset: hace falta flujo de registros por función, no un censo.
- Los 42 candidatos siguen sin atribución.

## 4. Stage 2001A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: número de ioctl que configura `ss_period`.
- `UNKNOWN`: máscara de IRQ y ring buffer.
- `UNKNOWN`: inicializador de `priv+0x10` y escritor real de 0xb4/0xdc.
- `UNKNOWN`: impacto en TX/RX.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1998A` | `tools/re/extract_stage1998a_ubntspecd_and_ath_spectral_stop_dissection.py` y su recibo |
| `1999A` | `tools/re/reconcile_stage1999a_priv_0x10_initializer.py` y su recibo |
| `2001A` | `tools/verify/record_stage2001a_memorymaster_ingest.py` y su recibo |
| `2002A` | `tests/test_stage1998a_to_2003a_suite.py` |
| `2003A` | `tools/verify/verify_stage2003a_wave160_opencode_gate.py` y la compuerta de la wave |
