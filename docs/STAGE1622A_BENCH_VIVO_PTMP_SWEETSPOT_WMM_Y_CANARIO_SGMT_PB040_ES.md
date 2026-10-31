<!-- doc-head: Wave97; adquisición OTA real, firmware ya combinado y restauración del banco -->
12 ventanas aceptadas, 2 intentos interrumpidos preservados y 3 descartes.
La recarga RAM y el watchdog se comprobaron; no hubo un nuevo cambio PB040.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stages 1620A..1625A: banco PtMP y Sweet-Spot WMM

## Alcance y resultado

CONFIRMED: AP LAP-120 `198.18.0.43` y Loco asociada `198.18.0.67`,
MAC inalámbrica `PUBLIC_DEVICE_0036`, canal 5180 MHz, 20 MHz y 17 dBm.
El tráfico fue directo OTA, con cuatro flujos TCP bidireccionales, IPTV UDP,
VoIP UDP y ping bajo carga. Se reutilizaron Bench Stage123A y el generador Stage311A.
No se utilizó `.250` como radio ni se accedió a `.241/.242`, LTU o Guarida.

Se completaron tres rondas `A1 → B1 → A2 → B2`: doce ventanas completas.
Las tres decisiones fueron `discard`; el perfil original quedó restaurado.
Los dos intentos anteriores del bloque interrumpido permanecen archivados:
hubo catorce intentos en total. Un pase local verifica estos hechos; no implica promoción.

## Stage1620A: preimagen y canario real

La imagen RAM de 204796 bytes tiene SHA-256
`a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`.
La disección byte a byte encontró:

| Campo | Valor observado en la preimagen |
| --- | --- |
| IE3 segmento2, VA `0x0040c140`, PB050 | 4000 (`0x0fa0`), frente a 2000 en ROM |
| IE3 segmento3, VA `0x009b758e`, PB040 | `0x76`, ya aplicado |
| Diferencias decodificadas ROM → RAM | 9 bytes: 6 cambios ASCII, 2 PB050 y 1 PB040 |

REFUTED para esta preimagen: que aún contuviera `0x72` en el sitio PB040.
El constructor estricto rechazó esa suposición. La opción idempotente emitió
una copia idéntica; no se invirtió el byte para inventar una comparación.
El significado causal de ese bloque CCA y una ganancia nueva de PB040 siguen UNKNOWN.

CONFIRMED: se cargó esa copia en RAM sobre el archivo de firmware del AP,
se recargó ath10k y se dejó vencer realmente el watchdog independiente de 60 segundos.
Se capturaron PID, cmdline y estado del proceso después del cierre del canal lanzador,
el marcador `FIRED`, arranque real, asociación y restauración de la capa anterior.
La CRC del driver fue `92363606`; athwlan `12b29d01` y otp `4c4fd0bc`.
No se escribieron particiones flash.

La primera validación local confundió los dos readbacks idénticos de potencia
de AP y AP/VLAN. Se preservó ese fallo y se corrigió el parser, sin repetir
el temporizador físico. El eco inicial de propiedad de inode era débil;
el script de activación sí usaba `set -eu`, y el readback final comprueba el inode original.
La evidencia no se presenta como un parche nuevo de un byte ni como lectura directa de RAM Xtensa.

## Stage1621A: protocolo y resultados

Sweet-Spot: VO=300/600 us, BE=1200/2400 us, umbral AQL=3000 us,
BQL `eth0` máximo=16384 bytes y reglas nftables propias EF/CS6 → prioridad262.
Los otros valores permanecieron en la preimagen registrada.
La clasificación Linux traduce la prioridad explícita262 a UP6/AC_VO;
EF sin esa regla no equivale por defecto a UP6.
Se guardaron reglas y contadores reales de nftables y contadores TID/AQM.

| Ronda | Comparación | TCP receptor A/B, Mbps | p95 A/B, ms | fmx_loss A/B | Decisión |
| --- | --- | --- | --- | --- | --- |
| I1 | Original / Sweet-Spot | 55.852 / 60.871 | 54.448 / 54.670 | 0.930619 / 0.921406 | discard |
| I2 | Sweet-Spot / mismo binario y política | 86.093 / 89.465 | 232.525 / 112.006 | 3.641111 / 1.712696 | discard |
| I3 | Original / repetición Sweet-Spot | 86.857 / 86.297 | 97.584 / 87.348 | 1.488157 / 1.318791 | discard |

Son medias de dos ventanas por brazo. La decisión exigió mejora de fmx_loss ≥0.005
en ambos pares, capacidad ≥95% y pérdidas UDP ≤2%; I2 no puede promoverse.
Una mejora media aislada no supera ese criterio. La variación del control
limita cualquier interpretación causal y no demuestra ausencia de sesgo.

La primera recarga I2B1 perdió la readquisición SSH, sin medición válida.
El temporizador restauró el AP automáticamente. Se verificaron ambos extremos,
se archivó el bloque parcial y se registró una única enmienda antes de reanudarlo completo.
Dado que el binario combinado ya era la base, I2 se adquirió de nuevo como A/A,
sin otra recarga. No se emparejó un A anterior a la interrupción con un B posterior.

Limitaciones: transferencias TCP de 3 segundos, diez muestras de ping por ventana,
tráfico y telemetría ejecutados por las CPU de los radios, y una sola pareja física.
Se usaron receptores TCP/UDP reales, sin elegir contadores de emisor de pérdida cero
ni sustituir goodput por el máximo entre la aplicación y los bytes OTA.
La preparación heredada del servidor STA devolvió salida1 porque BusyBox rechaza
`sleep 0.2` y `sleep 0.25`. Ese fallo auxiliar queda en cada captura;
los receptores y las lecturas posteriores sí se comprobaron por separado.
La primera corrida local dejó271PASS/26FAIL por una regla demasiado amplia
que rechazaba también ese error conocido. Se conserva completa y el verificador
solo admite esa advertencia exacta; otros fallos o mediciones ausentes se rechazan.
No se afirma significación estadística, meseta del silicio ni representatividad comercial.

## Investigación, memoria y cierre

Pillar A: contenedor y segmentos SGMT decodificados, hashes y preimagen comprobados.
Pillar B: 16 comprobaciones de fuentes primarias, invocación nativa de Scholar
y reactor en una cola propia, sin modificar la cola compartida.
El backend Scholar disponible fue heurístico (`jev-simulated-v1`): hubo cero
veredictos Jev en vivo. Esto queda separado del respaldo manual de fuentes primarias.
No se afirma haber ejecutado el pipeline Hyperresearch V8 completo.

Pillar C: secuencia real, límite de tres iteraciones y watchdogs independientes.
Pillar D: `scientific-critical-thinking`, objetivo de receptores y límites de causalidad.
Pillar E: cuatro registros solicitados, con ID nativo y lectura posterior en MemoryMaster.
Los estados científicos nativos son `candidate`; confirmar persistencia no los promueve.
Los alias `FMX-STAGE…-MM…` son referencias locales explícitas, no IDs devueltos por el servidor.
La actualización B/E de1536A/1537A conserva sus versiones antiguas y sus fallos históricos.

CONFIRMED al finalizar: hash y CRC base en ambos nodos, valores numéricos y 17 dBm,
asociación OTA, capa original del AP `/tmp/firmware-2-pb050.bin`, eliminación exclusiva
de las dos tablas nft propias y parada de los cuatro servidores de banco creados.
No quedó activada una política candidata.

## Evidencia y reproducción local

- [Canario1620A](../artifacts/autoresearch/stage1620a_live_wa_pb050_pb040_sgmt_ram_canary_receipt.json)
- [Campaña1621A](../artifacts/autoresearch/stage1621a_live_ptmp_wa_sweetspot_wmm_and_pb040_autoresearch_receipt.json)
- [Manifiesto físico congelado](../artifacts/autoresearch/wave97/physical/runtime_frozen_manifest.json)
- [Investigación y cuatro IDs nativos](../artifacts/autoresearch/wave97/research/provenance_final.json)
- [Gate1625A](../artifacts/verification/stage1625a_wave97_codex1_gate.json)

`python -m pytest tests/test_stage1620a_to_1625a_suite.py -q`

`python tools/verify/enforce_5pillar_research_gate.py <recibo> --require-live-hardware`

El gate de esquema de cinco pilares confirma sus campos y referencias.
El verificador Wave97 comprueba por separado fuentes, mediciones, restauración y límites.
Ninguno transforma el resultado heurístico de Scholar en validación semántica en vivo.
