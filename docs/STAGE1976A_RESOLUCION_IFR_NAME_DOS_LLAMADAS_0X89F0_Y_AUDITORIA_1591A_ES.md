<!-- doc-head -->
*STAGE1976A — ifr_name de las dos llamadas 0x89f0 y auditoría del fallo 1591A*
# STAGE 1976A — wifi0 y el fallo 1591A

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático sobre `athbox`, `umac.ko`, `ath_dev.ko` y el recibo congelado 1591A.
- Este documento no contiene apellidos.

## 1. Stage 1974A — la primera llamada usa wifi0
- `CONFIRMED`: la cadena `wifi0` está en **VA 0x419ae8** y tiene **6** referencias en el binario.
- `CONFIRMED`: una de ellas, en **0x40190c**, cae dentro de la función athstats y **justo antes** del primer ioctl de **0x40194c**. Esa llamada prepara `ifr_name = wifi0`.
- `CONFIRMED`: la cadena `ath0` está en **VA 0x41a11c** y tiene **5** referencias, pero **ninguna** dentro de 0x401890..0x402640.
- `INFERRED`: la segunda llamada de **0x402494** **no** cambia el netdev por nombre: reutiliza el mismo `ifreq` o un override de argv que este análisis estático no puede ver.
- `UNKNOWN`: el netdev efectivo de la segunda llamada en tiempo de ejecución.

## 2. Stage 1974A — los despachos del kernel
- `CONFIRMED`: `umac.ko` tiene **4** sitios de despacho para 0x89f0 entre WA y XC: 0x5cd20 → caso **0x5cdc8** y 0xbcc5c/0xbcc60 → caso **0xbccac/0xbccb0**.
- `CONFIRMED`: **`ath_dev.ko` tiene 0 sitios** para 0x89f0.
- `INFERRED`: ambos buffers salen de `umac.ko`; el primero por el caso 0x5cdc8 y el segundo por el mismo caso o por el segundo despacho.
- `UNKNOWN`: qué función llena 0xb4 y 0xdc. El caso del ioctl solo parchea 0x110c..0x1114 y copia.

## 3. Stage 1975A — el fallo 1591A era del test, no del recibo
- `CONFIRMED`: el test pedía `wmi_9044.openwrt.literal_vaddr`, una clave que el recibo **nunca escribió**.
- `CONFIRMED`: el recibo congelado usa **`literal_vaddr_hex`** entre sus 20 claves.
- `CONFIRMED`: el recibo histórico **no se modificó**: conserva su sha256 original.
- `CONFIRMED`: el arreglo se aplicó **solo al test**, aceptando `literal_vaddr` o `literal_vaddr_hex`.
- `CONFIRMED`: la suite `test_stage1590a_to_1595a_suite.py` pasa ahora **21 de 21**.
- `INFERRED`: no había un fallo de datos; había una expectativa de esquema desactualizada.

## 4. Consecuencia
- El "único fallo preexistente" del repositorio stage1500+ queda explicado y cerrado sin tocar historia.
- Las dos llamadas 0x89f0 comparten nombre de interfaz, así que la diferencia entre los buffers no viene del `ifr_name` sino de los argumentos de cada llamada.
- El llenado de 0xb4/0xdc sigue fuera del camino del ioctl.

## 5. Stage 1977A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.
- `CONFIRMED`: la lectura de ida y vuelta devolvió los **3** con estado `candidate`.

## 6. Lo que no se prueba
- `UNKNOWN`: el netdev efectivo de la segunda llamada.
- `UNKNOWN`: quién llena 0xb4 y 0xdc.
- `UNKNOWN`: el nombre de miembro de cada fila.
- `UNKNOWN`: cualquier lectura en vivo.

## 7. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1974A` | `tools/re/extract_stage1974a_athbox_two_0x89f0_ifr_name_and_kernel_dispatch.py` y su recibo |
| `1975A` | `tools/re/reconcile_stage1975a_dual_buffer_kernel_member_and_1591a_audit.py` y su recibo |
| `1977A` | `tools/verify/record_stage1977a_memorymaster_ingest.py` y su recibo |
| `1978A` | `tests/test_stage1974a_to_1979a_suite.py` |
| `1979A` | `tools/verify/verify_stage1979a_wave156_opencode_gate.py` y la compuerta de la wave |
