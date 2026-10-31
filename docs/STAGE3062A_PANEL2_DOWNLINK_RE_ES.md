<!-- doc-head: W402: mecanismos de bajada de Panel2, identidad OpenWrt y límites de contabilidad; RE local sin acceso a equipos -->
Panel2 es LAP-120/OpenWrt 24.10.4 según 15 observaciones locales durante W398; 8.7.25 de UISP no identifica su firmware de radio.
1267 us/paquete y MCS 7 no bastan para atribuir una causa: faltan fórmula, contadores crudos, tasas de los intentos y tamaño de paquete.
Recibo: artifacts/autoresearch/wave402_panel2_downlink_re.json; gate: artifacts/verification/wave402_lane4_panel2_downlink_gate.json.
Alcance: análisis estático y propuesta condicional de banco; ninguna escritura ni conexión a dispositivos.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W402 — Bajada de Panel2: mecanismos y prueba discriminante

## Identidad y alcance de la evidencia

La tabla local `tools/observability/telemetry.db`, abierta `mode=ro`, conserva 15 muestras `panel2_ap` entre 14:50 y 15:03:57 UTC del 30/10/2026: `observation.board=ubnt,lap-120`, plataforma OpenWrt y release 24.10.4. Se retuvieron únicamente campos permitidos y hashes del payload en `STAGE3062A_review_db_provenance.json`; no se exportaron direcciones ni filas completas. Esto confirma SO y placa en la ventana, no el blob WLAN ni los módulos instalados.

El orquestador identificó kernel 6.6.110 por mensaje `<orca-id>` (15:17:09 UTC). Ese dato es un relé, no un campo del extracto SQLite. El 8.7.25 expuesto por UISP corresponde al bridge. No aplicar recetas airOS/UMAC a este AP.

El árbol OpenWrt retenido permite analizar kernel 6.6.110, mac80211 backports 6.12.52 y ath10k-ct `ac71b14d` (rama seleccionada 6.10). Son versiones de componentes diferentes; la rama host no es la versión del firmware de radio. El inventario nativo adjunto fija tamaños, SHA256, símbolos, relocaciones e instrucciones de los módulos candidatos. No hay SHA actual de Panel2 ni prueba de identidad byte a byte entre esos candidatos y el equipo.

La imagen candidata conserva `firmware-2.bin` QCA988X/hw2.0 de 204796 B, SHA256 `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`; core 714672 B SHA256 `1ef8144f569a84bb5da67fa6b8c515123ab8b5ea809ce5d8cc214ece8e51571a`, pci 64496 B SHA256 `9e758ff4e10ab54269187fae8c4bd2b018d77177bc9842997ed0e7ebab28ce28` y mac80211 829464 B SHA256 `6241158088f1115c555344de7f99c24cd3e9f27b4fd7d3e78c8867829d139df6`. Son pines locales del candidato. La **identidad exacta del firmware WLAN y los módulos de Panel2 permanece UNKNOWN**: las muestras del colector no contienen ese tag/hash.

Existe además deriva local: el `ath10k_core.ko` instalado en `root-ath79` y el recompilado del árbol no son iguales. Sin embargo, se resolvió el fops original y se compararon los 672 bytes del writer de agregación: son idénticos y sus 19 bindings de relocaciones coinciden. Esto confirma el parser estricto de ese mando en ambos candidatos, sin afirmar equivalencia del módulo completo ni identidad con Panel2. El writer original está en `.text+93820`/offset de archivo 93932; SHA256 del cuerpo `5dfc9c4ce198e5df22872fe199d10d5ea8ae0bd71ec23555450f1ae16a3a8296`. Ninguna conclusión requiere cargar, descargar o reiniciar un módulo.

## Primero: qué significa el número de W398

Fuente: `artifacts/autoresearch/wave398_panel2_airtime.json` y `STAGE3058A_AIRE_PROPIO_Y_AJENO_PANEL2_ES.md`.

| Dato | Lectura admisible | Límite |
| --- | --- | --- |
| 1267 us/paquete | Estadístico agregado reportado | No se conservaron fórmula ni numerador/denominador; no equivale por sí solo a duración PPDU, coste por MPDU exitoso o intento |
| MCS 7 | Tasa reportada en una observación | No reconstruye tasas de los intentos ni NSS/BW/GI de toda la ventana |
| `downlink_failed=0` | Valor failed=0 reportado; alcance exacto dependiente del productor y módulo | No descarta retransmisiones exitosas ni fallback |
| 78,7% suma de duraciones por estación frente a 49,6% survey TX | Los dos conjuntos no son directamente aditivos | No se prueba una unidad, ventana, productor ni denominador común |
| Valor 24,5 de `cpe_200_213` | Puntos porcentuales del canal después del reparto normalizado | La columna está mal rotulada como % del TX del AP: los valores suman 49,6; 24,5/49,6 equivale a 49,4% de ese TX repartido |
| Residual 19,9% | Residual contable de fuentes distintas | No identifica inequívocamente otras redes ni excluye tramas propias no decodificadas |

El factor de normalización es `49.6/78.7 = 0.6302414`. No convierte la duración por estación en una medida física independiente. Tampoco se sabe si los 1267 us fueron normalizados. Las tasas de retries de las CPE son del sentido ascendente: no diagnostican los reintentos del AP en bajada.

El colector persistente actual guarda tasa/MCS/NSS, señal, retries y failed; no guarda `tx_packets`, `tx_duration` ni survey suficientes para reproducir W398. Su hash actual no identifica el productor histórico del agregado. La procedencia exacta de esa fórmula sigue `UNKNOWN`.

## Mecanismos ordenados por prioridad de investigación

El orden indica qué resolver primero para discriminar causas; no es una probabilidad causal medida.

| Prioridad | Mecanismo y capa | Cómo podría dar ese resultado | Evidencia que lo separa |
| --- | --- | --- | --- |
| 1 | Contabilidad, época y denominador — Linux/driver/colector | Duración acumulada de airtime real o estimado dividida por un contador de otra capa; ventanas distintas, reset/wrap o tasa de última trama | Deltas crudos con uptime/boot, misma estación/AC/ventana, fórmula explícita y ruta exportadora del módulo exacto |
| 2 | Agregación efectiva baja — mac80211/ath10k/firmware/peer | A-MPDU pequeño, BA ausente, MSDU pequeños, carga fragmentada o colas sin suficientes tramas amortizan peor preámbulo/ACK/acceso | Bytes y paquetes, BA, distribución de subtramas por agregado y misma carga; comparar límite máximo no demuestra tamaño efectivo |
| 3 | Reintentos exitosos y fallback — firmware QCA | Varios intentos o tasas inferiores al MCS mostrado consumen TX sin elevar `failed` final | Histograma de tasas/intent count, retry de bajada, éxito/fallo con unidades por MPDU/MSDU y firmware identificado |
| 4 | Colas/AQL/fairness y competencia — mac80211/firmware | Cambian turnos, backlog, profundidad pendiente y agregación disponible; pueden aumentar RTT | Backlog/AQL por AC/peer, airtime flags/pesos y carga simultánea; no asumir que espera en cola sea tiempo de transmisión |
| 5 | Contención/protección/BA/errores — MAC/RF | Sobrecoste de acceso, ACK/BA, protección y pérdidas puede reducir eficiencia | Contadores específicos, reintentos y captura coherente; survey residual no determina una causa RF |

No se puede calcular un tiempo esperado preciso con solo el índice MCS. Faltan modo HT/VHT, ancho, NSS, GI, bytes útiles, encapsulado, tamaño del agregado, intentos y alcance del contador. No se identificó un fallo de hardware.

## Mandos: dominio del parser y candidato de banco

La tabla nativa del recibo contiene rutas, funciones, líneas, offsets ELF, condiciones y semántica de cada mando. `phyX` es la radio seleccionada tras inventario en banco; no asumir `phy0`. La existencia de un archivo en la fuente no confirma que esté expuesto en Panel2. Las lecturas debugfs pueden solicitar estadísticas al firmware: no se ejecutaron en esta ola.

El candidato prioritario es `/sys/kernel/debug/ieee80211/phyX/ath10k/htt_max_amsdu_ampdu`. La sintaxis es **AMSDU primero, AMPDU después**. El dominio semántico retenido es AMSDU 1..31 y AMPDU 1..64; no ensayar ceros, negativos ni valores que dependan de truncamiento. El getter es estado cacheado en el host: ni `write` exitoso ni lectura igual prueban aplicación en el firmware o agregación efectiva.

Propuesta condicional de una sola variable: si el banco identifica el mismo mecanismo, dispone de getter y el original es `A 64`, mantener `A` y comparar **`A 64` frente a `A 32`**. No fijar arbitrariamente AMSDU=3 si el original es otro. Restaurar exactamente el par original. Si el getter no devuelve AMPDU=64 o el dispositivo no cumple las condiciones, no aplicar esta pareja y conservar `UNKNOWN`; no convertirla en una receta para producción. Son puntos de caracterización dentro del dominio del parser, **no un rango de seguridad física demostrado**.

| Mando/familia | Papel | Decisión de esta ola |
| --- | --- | --- |
| `htt_max_amsdu_ampdu` | Límite global de agregación enviado por HTT; no ajuste por estación | Primer A/B condicional; 64→32 manteniendo AMSDU, carga y resto constantes |
| AQL `aql_txq_limit` / `aql_threshold` | Airtime pendiente estimado, no tamaño real del A-MPDU | Leer y fijar valores originales durante el primer A/B; un ensayo posterior requiere su propio valor y control |
| `airtime_flags` / peso por estación | Política de scheduling/débito; no equivalen a borrar acumuladores de duración | Mantener originales; no usar para hacer desaparecer el contador ni como prueba de eficiencia PHY |
| Retry WMI/CT (`agg_sw_retry`, `non_agg_sw_retry`, XRETRY) | Política de reintentos del firmware, mapas dependientes de versión | Sin actuador portable, dominio físico ni readback actual demostrado: no proponer enteros crudos |
| `set_rates`, `set_rate_override`, máscara de bitrate | Ámbitos y soporte distintos; tasa fija puede impedir fallback | No trasladar `set_rates` de broadcast/beacon a unicast ni congelar MCS 7 para explicar un snapshot |
| `iwpriv ... AMPDUFrames/aggr_swretry/set_multiq`, `/proc/sys/dev/uph/...` airOS | Driver propietario y otra plataforma | No son los mandos del Panel2 OpenWrt; no trasladar valores por coincidencia de nombre |

El recibo nativo detalla las rutas de duración HTT, estadísticas y survey. `airtime_flags` condiciona el débito del scheduler; los acumuladores TX/RX se incrementan por otra operación. El estimador usado por AQL y la duración exportada por `iw` deben distinguirse; una estimación pendiente no mide tiempo físico de cada paquete.

## Qué probó realmente el ledger de 571 knobs

El catálogo exacto tiene 571 entradas y `automatic_execution_allowed=false`; ninguna entrada está habilitada. Se cruzaron 63 IDs relevantes con Stage72C, 18 fuentes con SHA coincidente y 11 ensayos/rondas extraídos de cinco recibos JSON. El detalle por ID está en `STAGE3062A_review_findings.json`.

| IDs o grupo | Evidencia retenida | Conclusión aplicable |
| --- | --- | --- |
| `htt_aggr_size` | Parejas históricas [2,48], [3,32], [3,64] catalogadas; Stage72C `CATALOGED_STATIC_RE`, sin prueba aislada 60–71 | No hay A/B aislado que valide 64→32 en este módulo/firmware |
| `aql_txq_limit`, `aql_threshold` | Puntos de receta antiguos; Stage72C no evaluado | No son rangos seguros ni aceptación de este equipo |
| `wmi10_1_pdev_agg_sw_retry_th`, `wmi10_1_pdev_non_agg_sw_retry_th`, `ct_special_9` | Mapa de fuente 10.1, límites semánticos/readback sin cerrar; último excluido | No trasladar IDs, defaults ni rangos wire-u32 a otra versión |
| Nueve IDs históricos `AMPDUFrames/aggr_swretry/nonaggr_swretry` | Ausentes del catálogo actual de 571 | No inventar una correspondencia exacta |
| S62A-R2 | Perfil multi-knob: 20,328→25,615 Mbit/s (+26,01%); p95 6,889→7,438 ms (+7,97%, peor) | Stage72C copió otras cifras y una mejora de p95; el fuente R2 no actúa AMPDUFrames: no atribuirle agregación |
| S68C-XC-R1 | Varios mandos; getter `ampdu_frames` vacío; multiq=1 en A y B | Sin aplicación verificada de ese knob ni causalidad individual |
| S70B / burst CT | Ensayo airOS enlazado por Stage72C a IDs WMI CT | Ese enlace no prueba actuación del ID CT/OpenWrt |
| S70C | Goodput +8,559%, p95 +5,769%; `RETAIN_CURRENT_CHAMPION`, `promoted=false` | No es aceptación general ni mejora simultánea de latencia |

El ledger es evidencia de catálogo y de intentos fechados; los recibos originales resuelven sus discrepancias. No se modificaron catálogo ni ensayos históricos.

## Checklist para el banco de lane_1

1. Identificar placa, release, kernel, módulos y blob WLAN exactos, features/versión HTT y debugfs presente. Conservar hashes, getter original y errores; no asumir identidad por versión de UISP o rama host.
2. Capturar A/A con una estación y carga fija, mismo ancho/NSS/GI, longitud y dirección de tráfico; guardar inicio/fin monotónicos, boot/uptime, bytes/paquetes/duration/retries/failed y survey por interfaz/canal. Deltas negativos/reset o denominador cero invalidan la métrica.
3. Explicitar qué cuenta cada numerador y denominador, antes de comparar us/paquete. Conservar estadísticos de tasas y agregados reales si están disponibles; declarar lo que siga faltando.
4. Solo si se cumplen las condiciones del candidato: A=`A 64`, B=`A 32`; tres pares contrabalanceados/ABBA, con carga, AQL, fairness, tasa, canal, potencia y firmware constantes. La prueba de tamaño máximo no garantiza que el firmware forme agregados de ese tamaño.
5. Usar el watchdog independiente vigente del banco, con duración/lifetime y restauración verificados antes del cambio. Registrar límites de parada antes de ejecutar, por memoria, pérdida de asociación y regresión de latencia/goodput. Esta ola no certifica un watchdog ni fija umbrales sin baseline.
6. Medir goodput, RTT cargado p50/p95/p99, retries/failed de bajada, us por paquete con fórmula reproducible, backlog/AQL y MemAvailable. Restaurar el par original y verificar getter, asociación, radio y salud. Un getter cacheado no sustituye la validación de efecto.

No se pide cargar módulos, cambiar firmware ni actuar sobre producción para este experimento. La ejecución y aceptación física pertenecen al contrato posterior de banco; esta ola entrega la discriminación estática y sus límites.

## Entregables y cierre

`wave402_panel2_downlink_re.json` reúne identidad, hashes, rutas de fuente/binario, tabla de knobs, ranking, cruce del ledger y límites. Los extractos nativos y la revisión están bajo `docs/STAGE3062A_*`. El gate declara por separado aceptación del análisis estático y estado de causalidad/seguridad/identidad WLAN. No se afirma que los 1267 us sean causados por un límite de agregación, ni que exista ya una mejora física demostrada.
