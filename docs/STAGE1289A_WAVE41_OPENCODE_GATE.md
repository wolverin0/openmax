<!-- doc-head: Stage 1289A - Wave 41 gate, thirty-two checks and three cross-stage agreements, all passing, with the LED matrix recorded as not recoverable and four UNKNOWN board counts rather than fabricated zeros -->
# Stage 1289A — Wave 41 gate

- **Recibo**: [`artifacts/verification/stage1289a_wave41_opencode_gate.json`](../artifacts/verification/stage1289a_wave41_opencode_gate.json)
- **Herramienta**: [`tools/verify/verify_stage1289a_wave41_opencode_gate.py`](../tools/verify/verify_stage1289a_wave41_opencode_gate.py)
- **Alcance**: verificación estática offline. Sólo lee JSON y Markdown.

## 0. Resultado

```
[1289A] checks=32/32 cross=3 failures=0 compliant=True led_matrix_recoverable=0
```

| Métrica | Valor |
| :--- | :-: |
| checks | **32** |
| aprobados | **32** |
| cross-stage | **3** |
| failures | **0** |
| `compliant` | **True** |
| `led_matrix_recoverable` | **0** |

## 1. Qué verifica

| Etapa | Aserciones |
| :--- | :--- |
| **1284A** | 4 boards, 4 imágenes, 0 FDT, 4 recuentos UNKNOWN, 0 barras declaradas, matriz no recuperable, scope estático, gaps, 0 colisiones |
| **1286A** | rango 1230A..1259A, partición cerrada 20+10=30, 0 gates FAIL, ausentes nombrados |
| **1285A** | menos de 160 líneas, 1 doc-head, 0 exclamaciones en prosa, marcadores en español |
| **1287A** | ambos índices bajo 200 líneas, 1 doc-head, sección Waves 32..41 presente |
| **1288A** | suite presente |

## 2. Los tres cross-checks

**`cross.matrix_unknown_stated`** — 1284A declara `led_matrix_recoverable = 0` y el doc español dice
literalmente «no es recuperable». Si alguien convirtiera los UNKNOWN en ceros, esta comprobación cae.

**`cross.audit_mentioned_in_state`** — `CURRENT_STATE.md` nombra el recibo consolidado de Waves 32..36,
de modo que el índice y la auditoría no pueden divergir en silencio.

**`cross.ranges_disjoint`** — 1284A y 1286A declaran etapas distintas, así que un recibo no puede
suplantar al otro.

## 3. Lo que este gate no certifica

**`REFUTED`**: que alguna board tenga un número concreto de LEDs.

El gate certifica los **recibos** y la **negativa a inventar**. La matriz física sigue **UNKNOWN** para
las cuatro boards hasta que exista un DTS de OpenWrt o una lectura en vivo de `/sys/class/leds/`.

## 4. Estado de las seis etapas

| Etapa | Entregable | Estado |
| :--- | :--- | :-: |
| 1284A | herramienta + recibo matriz LED | **CONFIRMED** (matriz no recuperable) |
| 1285A | doc español de la matriz | **CONFIRMED** |
| 1286A | auditoría consolidada 1230A..1259A | **CONFIRMED** (20/30, 0 FAIL) |
| 1287A | `CURRENT_STATE.md` y `MASTER_...INDEX.md` | **CONFIRMED** (180 y 175 líneas) |
| 1288A | suite pytest | **CONFIRMED** |
| 1289A | gate | **CONFIRMED** (`compliant`) |

## 5. Huecos

- **`UNKNOWN`** — el recuento real de LEDs por board.
- **`UNKNOWN`** — por qué diez etapas de Waves 32..36 no tienen recibo de gate.
- **Límite conocido** — un `compliant` verde aquí no re-mide ningún gate anterior.
- **No intentado** — arrancar una board, leer LEDs en vivo, contactar un radio.
