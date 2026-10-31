<!-- doc-head: Stage3015A extractor offline QCA988x, endian mixto y limites de acceso/ranging -->
Layout y fixtures sinteticos verificados; ningun dispositivo accedido ni captura fisica aceptada.
El gate de lane4 refuta la exportacion del PPDU-end del host mediante pktlog en este build.
<!-- /doc-head -->

# Stage 3015A: extractor userspace offline del Pilar 2

Implementacion: `tools/ground_up/pillar2/ppdu_evm_ranging.py`.
Pruebas: `tests/test_pillar2_ppdu_evm_ranging.py`.
Gate: `artifacts/verification/wave355_lane2_pillar2_extractor_gate.json`.

## Evidencia y alcance

**CONFIRMED, software offline:** interpretacion del perfil documentado y pruebas
con bytes sinteticos. No prueba al modulo despachado ni mediciones RF reales.
Se contrastaron las estructuras de la fuente local con
[ath10k rx_desc.h, fuente Linux](https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/wireless/ath/ath10k/rx_desc.h).

**REFUTED, acceso userspace sin parche en el build auditado:**
`artifacts/verification/wave355_lane4_pillar2_ppdu_access_gate.json` y
`artifacts/autoresearch/wave355_pillar2_ppdu_access.json` indican que pktlog no
exporta este descriptor del host y el tracepoint necesario no esta compilado.
No existe un encabezado pktlog confirmado que permita recuperar estos campos.
`NativePktlogAdapter` consume ese contrato y rechaza la entrada; no interpreta
arbitrariamente los registros del firmware como PPDU-end.

Lane4 ademas corrige Stage348A: este arbol usa la variante common+QCA988x,
no el nombre `rx_ppdu_end_v1`; la ubicacion dentro del descriptor completo se
publica en unidades de cuatro bytes. El hook previo al pull requiere un parche
de fuente y recompilacion; el header historico no compila tal cual contra ese
arbol. El .ko sin BTF/DWARF deja la correspondencia binaria como **UNKNOWN**.

## Layouts y framing explicitos

| Perfil | Bytes 0..63 | Timestamps | Cola 72..83 |
|---|---|---|---|
| `dma_le` | 16 dwords EVM | TSF en 64, WB en 68, little-endian | little-endian |
| `fmx_sample` | TSF/WB en 0/4; EVM empieza en 8 | CPU-endian declarado | CPU-endian declarado |

El sample FMX conserva los bytes EVM sin conversion y convierte sus escalares
a CPU-endian. Por eso MIPS big-endian exige interpretacion mixta.
Ambos perfiles miden 84 bytes; su longitud no permite autodetectarlos.

`Raw84Adapter` exige alineacion y longitud multiplo de 84. Es una entrada
de fixtures o exportaciones explicitamente preparadas, no una via real de pktlog.
`StructTraceAdapter` recibe formato, endian, campos de longitud/tipo y offset
de payload declarados por el productor. Los tests usan un framing sintetico
propio que no pretende representar el encabezado del firmware.
Otros productores pueden implementar `frames(bytes) -> Iterable[Frame]`.
No se resincroniza sobre supuestas firmas dentro de bytes basura.

## Estadisticas EVM y estaciones

- Cada piloto produce cuatro bytes signed; los estadisticos incluyen cantidad,
  media, minimo, maximo y desviacion poblacional mediante Welford.
- El contrato Stage348A trata `-128` como ausente. La fuente no confirma esa
  politica ni la escala dB: se etiqueta como supuesto documental, configurable
  con `--retain-all-evm` o `sentinel=None` en la API.
- `PPDU_DONE` es obligatorio; PHY_ERR/codigo de error excluyen el registro de
  estadisticas saludables. Peer 0 es valido solamente con PEER_IDX_VALID.
- Sin tabla externa se agrupa por receptor/epoca/peer_index, no por identidad
  permanente. `station_map={(receiver, epoch, peer_index): anonymous_id}` resuelve
  una estacion con contexto explicito y una epoca no vacia.
- No se deducen Fresnel, interferencia, NSS activo ni EVM calibrado en dB.

## Reloj y ranging

Para el perfil **asumido** de 80 MHz, cada tick equivale a 12.5 ns y el reloj
compuesto es `80 * wb_timestamp + locationing_timestamp`, con fraccion 0..79.
Su modulo es `80 * 2**32`; no se usa el wrap TSF como sustituto.
El wrap es opt-in y exige un delta maximo. La epoca del productor debe marcar
reinicios: el parser no puede detectar un reset omitido en esos metadatos.

Un timestamp RX aislado no es RTT. La distancia queda `null / UNKNOWN`.
La API `RttReference` exige referencia TX calibrada, receptor/epoca/peer
coincidentes y correcciones de turnaround/calibracion no negativas.
Solo entonces convierte el RTT corregido mediante `c / (2 * 80e6)`:
**1.8737028625 m por tick RTT**. El resultado es estimado desde la calibracion
suministrada, no una certificacion fisica ni una resolucion de distancia lograda.

## Validacion y siguientes pasos

```powershell
python -m pytest tests/test_pillar2_ppdu_evm_ranging.py -q -p no:cacheprovider
python tools/ground_up/pillar2/ppdu_evm_ranging.py capture.raw --adapter dma84
python tools/ground_up/pillar2/ppdu_evm_ranging.py capture.raw --adapter fmx84 --cpu-endian big
```

Las pruebas cubren endian, signed/sentinel, peers, PHY_ERR, wraps, calibracion,
agregacion, plugins, limites, truncados, basura y tamper del gate de acceso.
Hay limites de bytes, registros, estaciones y diagnosticos. Una truncacion del
framing descarta resultados parciales; basura dentro de records alineados se
cuenta explicitamente y la CLI devuelve no-cero si hubo rechazos.
Un bloque basura estructuralmente valido no puede autenticarse sin framing o
integridad del productor. Esa limitacion no se oculta mediante heuristicas.

Queda para la siguiente ronda de banco: parche de fuente y ABI de exportacion,
snapshot consistente, propiedad/consumo del PPDU_DONE, secuencias contra duplicados,
tabla de peers por epoca, perfil de reloj y calibracion fisica de RTT/EVM.
Este trabajo no habilita debugfs, pktlog ni tracefs, ni compila o carga firmware.
