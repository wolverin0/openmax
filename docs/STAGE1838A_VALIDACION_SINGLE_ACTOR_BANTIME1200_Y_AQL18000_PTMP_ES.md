<!-- doc-head: Wave133, evidencia viva PtMP, netifd y contraste AQL18000 -->
Ocho ventanas reales, restauración verificada y candidato descartado.
El criterio del healer solicitado sigue incumplido; las pruebas locales no lo sustituyen.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage1838A — Auditoría netifd y AQL18000 en PtMP

## Resultado y alcance

CONFIRMED: AP 198.18.0.43 y STA 198.18.0.67, exclusivamente.
Se completaron dos rondas A1→B1→A2→B2 con TCP bidireccional, IPTV y VoIP UDP.
No hubo flash, recarga de red ni cambios en otros radios.
El gate distingue adquisición completa de aceptación operativa incompleta.
El candidato se descarta; no se promueve una configuración nueva.

## Stage1836A: interfaz nueva y actor observado

- Ifindex 996→997, ausencia explícita del antiguo AP_VLAN y nueva asociación.
- `del_client` usó `ban_time=1200`; se eliminó explícitamente la interfaz antigua.
- La traza del PID real de netifd contiene dos SIOCBRADDIF exitosos, separados por una baja.
- Cero EBUSY en esa traza. Son dos operaciones del mismo proceso.
- No se instaló un hook adicional ni se trazó a todos los posibles actores.
- Estado nativo 3 y multicast_to_unicast 0 después de la recreación.
- El archivo solicitado `fmx_apvlan_bridge_healer.sh` está ausente.
- Existe `fmx_ap_4addr_peer_healer.sh`, con ban1200: otro archivo, sin equivalencia probada.
- Para probar multicast1 se escribió temporalmente el atributo en RAM.
- Primer ping: 10 enviados, 8 recibidos, 1 duplicado y 20% de pérdida.
- El parser inicial no reconocía el resumen con duplicados; se conservó el error.
- Se restauró multicast0. La comprobación posterior dio 10/10, sin borrar el fallo original.
- UNKNOWN: causa de esa pérdida y si multicast1 la causó; no hay prueba causal suficiente.

No se afirma que el healer ausente haya mantenido multicast1 automáticamente.
La traza pasiva se retiró y su binario temporal se eliminó tras comprobar su hash.

## Stage1837A: diseño y datos reales

Stage1747 había probado sólo umbral 12000→18000 en PowerBeam y terminó DISCARD.
No había demostrado un ganador con todos los AC 2000/4000.
Aquí ambos brazos normalizan VO/VI/BE/BK a 2000/4000 microsegundos.
A mantiene umbral 3000; B cambia sólo el umbral a 18000.
El perfil original heterogéneo se restaura entre ventanas y al final.
Por tanto, A no representa una medición del perfil original sin normalización.
Cobertura 0, 5180 MHz/20 MHz y potencia 20 dBm AP/17 dBm STA permanecieron iguales.

| Ronda | A Mbps | B Mbps | Cambio | A p95 ms | B p95 ms | Cambio |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 77.402 | 49.265 | -36.35% | 41.533 | 26.286 | -36.71% |
| 2 | 79.736 | 33.165 | -58.41% | 21.328 | 45.525 | +113.46% |

| Bloque | IPTV pérdida % | VoIP pérdida % | IPTV jitter ms | VoIP jitter ms | Ping recibidos |
|---|---:|---:|---:|---:|---:|
| 1A | 0 | 0 | 1.403 | 4.106 | 40/40 |
| 1B | 0.263 | 0 | 1.110 | 3.049 | 33/40 |
| 2A | 0 | 0 | 1.794 | 4.240 | 40/40 |
| 2B | 0 | 0 | 0.970 | 1.120 | 31/40 |

Goodput es la suma de TCP bidireccional y UDP recibido, no sólo TCP.
Cada ventana pide 20 s; se conserva la duración efectiva reportada por iperf3.
Las medias de dos ventanas por brazo son descriptivas, no muestras independientes de población.
No se infiere significancia estadística ni superioridad general del umbral.

## Fallo conservado y reparación del arnés

El primer intento se detuvo en A1: la lectura a 21 s precedió el cierre TCP a 23,8 s.
Los archivos nativos y la restauración permanecen en `wave133/holdout/`.
El segundo intento espera ambos marcadores de fin hasta un límite compartido de 28 s.
No amplía el watchdog de 45 s ni reutiliza archivos del intento fallido.
Las ocho ventanas completas están en `wave133/holdout_attempt2/`.
El parser distingue respuestas únicas de duplicados y mantiene la pérdida real.

## Seguridad y límites de interpretación

Ambos watchdogs se verifican antes de modificar ajustes.
La limpieza identifica cada proceso por PID, tiempo de nacimiento y comando propio.
La lectura final independiente confirmó AC originales, umbral 3000, cobertura 0, RF y firmware.
SHA256 firmware: `a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`.
Las dos direcciones de gestión del AP se conservaron; no quedaron cargas propias activas.
Estado final del AP_VLAN: 997, estado 3, multicast0.
La lectura global AQL no demuestra límites efectivos de peers previamente personalizados.

## Cinco pilares, memoria y verificación

A: procedencia binaria histórica y fuente mac80211 oficial; no nueva equivalencia ELF desplegada.
B: fuentes primarias, invocación Scholar nativa y reactor privado real.
Scholar devuelve heurísticas; cero verificaciones semánticas Jev en vivo.
C: dos bloques temporales ABAB completos, mismos ajustes y guard de 45 s.
D: contraste descriptivo y revisión de capacidad, pérdida, latencia y jitter.
E: dos claims reales, uno por etapa, con lectura posterior y scope project:futuramax.
Los resultados finitos se agregan a artifacts/autoresearch/results.tsv.
Pytest verifica hashes, datos nativos, restauración y rechazo de evidencia incompleta.
El gate compartido de cinco pilares valida presencia estructural; no certifica óptimos de RF.

## Evidencia

- [Recibo1836](../artifacts/autoresearch/stage1836a_live_clean_single_actor_bantime1200_rebind_receipt.json)
- [Recibo1837](../artifacts/autoresearch/stage1837a_live_ptmp_gentle_aql18000_triple_play_receipt.json)
- [Manifiesto nativo](../artifacts/autoresearch/wave133/runtime_manifest.json)
- [Seguridad final](../artifacts/autoresearch/wave133/safety_final.json)
- [Gate1841](../artifacts/verification/stage1841a_wave133_codex1_gate.json)

Antes de certificar el healer solicitado, resolver su implementación ausente y la política multicast.
La recuperación del enlace y pytest no sustituyen ese criterio pendiente.
