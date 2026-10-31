<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1335A en español, actualizado en Wave 58: respuesta con evidencia graduada a si se puede probar OpenWrt en un LiteBeam del Edificio Principal contra un LiteBeam stock, lista exacta de candidatos de 1332A (inventario UISP solo lectura, cableado sin probar), exclusiones SG-01, plan acotado por riesgo con backup mtd, watchdog 45 s/120 s, criterios go/no-go, lo NO probado y la reconciliación 1386A/1387A/1389A (interop REFUTED_AS_STATED, imágenes oficial vs OpenMax, PtP-Colo con radiografía y backups pero bloqueado por el Step-0 de frecuencia; ver STAGE1388A) -->
# Stage 1335A - Candidatos LiteBeam del Edificio Principal y prueba híbrida stock/OpenWrt

Estado: `DOC_NOT_EXECUTED`. Escrito offline a partir de los recibos 1332A, 1333A y 1334A y de documentos del repo; actualizado en Wave 58 con 1344A a 1346A, 1386A, 1387A y 1389A (sección 6). Ningún radio fue tocado por esta etapa. No autoriza ningún cambio: toda mutación de producción necesita la compuerta del operador.
Etiquetas: CONFIRMED / INFERRED / UNKNOWN / REFUTED. Clases: CONFIRMED_LIVE_HARDWARE, CONFIRMED_STATIC_BINARY, SIMULATED_MODEL_ONLY, LIVE_READONLY_INVENTORY, OFFLINE_ARTIFACT_INFERENCE.
Recibos: `artifacts/verification/stage1332a_edificio_principal_ptp_candidates.json`, `artifacts/verification/stage1333a_litebeam_hybrid_preflight_verifier.json`, `artifacts/verification/stage1334a_historical_sirq_ram_crossref.json`. Checklist unificado del PtP-Colo: `docs/STAGE1388A_CHECKLIST_UNIFICADO_PTP_COLO_105_62_54_INFRA_Y_BACKUP_MTD_ES.md`.

## 1. Respuesta directa a la pregunta del operador

Pregunta: qué certeza hay de aplicar este firmware a dos LiteBeam sin problemas, y si se puede probar en uno del Edificio Principal contra un LiteBeam stock.
Respuesta corta: no hay una certeza demostrada para LiteBeam. No se da un porcentaje porque ningún recibo lo sostiene. Lo que existe es evidencia de otro equipo (PowerBeam) y de otros pares, y lo que se pide nunca se hizo. Probar en uno del Edificio es posible solo como prueba acotada, con ventana de servicio y compuerta del operador, y hoy el veredicto del verificador 1333A es NOT_READY para las 15 unidades.

| Afirmación | Clase de evidencia | En qué equipo o rig | Estado |
| --- | --- | --- | --- |
| Ciclo del kit v17 (dry-run, apply, verify, rollback) con 12 acciones nativas | CONFIRMED_LIVE_HARDWARE | Par de banco PowerBeam .241/.242, ambos OpenWrt (`docs/STAGE1175A_LIVE_PBE5AC_V17_VERIFIED_LIFECYCLE.md`) | Solo prueba el ciclo del kit; no es rendimiento ni estabilidad |
| Flasheo OTA de ambos extremos a OpenWrt 24.10.4 | CONFIRMED_LIVE_HARDWARE | PowerBeam de banco, 105A (`docs/STAGE105A_PBE5AC_GEN2_REMOTE_OTA_PTP_CONVERSION_AND_AB_BENCHMARK.md`) | En LiteBeam: nunca |
| Imagen OpenWrt para LiteBeam (placa 0xe7f9) | Construida y receta fijada por 132A | Archivo en disco, sha256 verificado en 1333A | Sin validación en hardware; solo para puesta inicial por cable. Existe además la oficial stock, otro artefacto (sección 6) |
| LiteBeam OpenWrt registrado como cliente en producción | CONFIRMED_LIVE_HARDWARE | Panel1, contra un AP OpenWrt (`artifacts/canary_panel1_guarida/guarida_32cpe_radiography_20261024.json`) | Contra AP OpenWrt, no contra AP stock |
| Cliente OpenWrt contra AP airOS 8 stock | CONFIRMED_LIVE_HARDWARE (resultado negativo) | PowerBeam de banco, 105A FMX-DISC-39 | Autenticó, asoció y cerró WPA2, pero el AP stock descartó el tráfico unicast |
| Fix de 509A a 518A (op_mode=0 y allow_80211=1 arreglan el unicast de 105A, con 152.97 y 146.97 Mbps) | REFUTED (REFUTED_AS_STATED en 1386A) | Ninguno | Cero apariciones de esas perillas en 509A a 518A; 105A reporta el descarte incluso con op_mode=0; 152.97 solo corresponde a una edad brctl y a 152.976 ms de latencia (nunca a throughput) y 146.97 existe una sola vez como Mbps, un ul_goodput_mbps SIMULATED_MODEL_ONLY (`artifacts/ptmp_sim/mode_a_vs_mode_b_crossover_20261024.json:28133`); ninguna es medición viva de 509A a 518A |
| PtP-Colo (198.18.0.91 y 198.18.0.92): radiografía y backup mtd0/1/4/5 de ambos extremos | LIVE_READONLY_INVENTORY (CONFIRMED) | Par real del Edificio Principal, LiteBeam 5AC Gen2, lectura viva de solo lectura (1344A, 1345A) | Backups verificados por sha256; el enlace opera a 6035 MHz, sobre el tope de 5865 MHz de OpenWrt: bloqueo Step-0 (sección 6) |
| Palanca allow_80211 / op_mode dentro de `ubnt_poll_host.ko` | CONFIRMED_STATIC_BINARY (REFUTED como palanca) | Binario, 1159A (`docs/STAGE1159A_UPH_ALLOW_80211_OP_MODE_0_HYBRID_OTA_RE.md`) | Interop viva: UNKNOWN |
| AP OpenWrt que admite clientes stock | CONFIRMED_LIVE_HARDWARE | Banco con clientes Loco, Rocket, SXT y M5 (`docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`) | Ningún cliente LiteBeam stock admitido; uno quedó pendiente e ignorado en Panel1 |
| Un LiteBeam OpenWrt registrado contra un LiteBeam stock en el Edificio Principal | NUNCA se hizo | Ninguno | Sin evidencia de ninguna clase |
| Watchdog v17 de 45 s / 120 s | Estático y raíz falsa (CONFIRMED_STATIC_BINARY, SIMULATED_MODEL_ONLY) | 1099A y 1100A, sin radio; un watchdog anterior se armó en vivo en 68A y 84A | v17 nunca corrió en un radio |
| Emisión de una imagen SquashFS propia | BLOCKED / NOT_EXECUTED | 988A (`docs/STAGE988A_SQUASHFS_WATCHDOG_AND_REPO_HYGIENE_GATE.md`) | No se puede construir una nueva hoy |
| Recuperación por cable de un LiteBeam | NUNCA se ejercitó | Ninguno | Camino de retorno sin probar en este modelo |

Problemas abiertos que bloquean un GO: 988A deployment_authorized falso y aceptación física UNKNOWN; 1077A MATRIX_NOT_EXECUTED; cableado local de cada candidato UNKNOWN; mecanismo del lado stock documentado de cuatro formas distintas (sección 3). Para el PtP-Colo se suman el Step-0 de frecuencia (6035 MHz contra un tope de 5865 MHz) y el drenaje de mangles de Infra sin ejecutar; el checklist 1387A da NOT_READY.

## 2. Candidatos (1332A)

Fuente y calidad. Inventario UISP en vivo, solo lectura: un GET de `/devices` devolvió 604 registros (clase LIVE_READONLY_INVENTORY). Tabla de puertos del router de borde: BLOCKED_NO_CREDENTIAL (ningún credencial del repo para ese equipo), por eso el cableado no se pudo verificar. Tabla ARP de esta PC: 41 entradas, ninguna en 198.18.0.93/24. INFERRED: esta PC no ve esa LAN a nivel 2, así que el acceso "desde esta red" tampoco está probado. Ningún radio fue contactado (writes 0, radio_connections 0 recalculados desde el ledger). Reproducible con `python tools/uisp/discover_edificio_principal_ptp_litebeam_candidates.py --live --out DIR/candidatos.json` (solo GET y comandos print; sin `--live` trabaja offline). Los nombres de host de UISP pueden contener nombres de clientes y se omiten aquí: cada fila se identifica por IP y prefijo del id UISP.

| Id | IP | Rol | Placa y modelo | UISP id | Par (rol) | Estado | Ubicación | Clase de evidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | `198.18.0.94` | ap | 0xe7f9 LBE-5AC-Gen2 | c44af853 | 198.18.0.95 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C02 | `198.18.0.96` | ap | 0xe3d6 PBE-5AC-Gen2 | fd452d0b | 198.18.0.97 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C03 | `198.18.0.98` | ap | 0xe7f9 LBE-5AC-Gen2 | cbf7a731 | 198.18.0.99 (station) | active | AMBIGUOUS | LIVE_READONLY_INVENTORY |
| C04 | `198.18.0.100` | ap | 0xe3d6 PBE-5AC-Gen2 | c15baec8 | 198.18.0.101 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C05 | `198.18.0.102` | ap | 0xe7f9 LBE-5AC-Gen2 | d7e7b3ae | 198.18.0.103 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C06 | `198.18.0.104` | ap | 0xe3d6 PBE-5AC-Gen2 | 10cc2020 | 198.18.0.105 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C07 | `198.18.0.106` | ap | 0xe7f9 LBE-5AC-Gen2 | 9f29f65d | 198.18.0.107 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C08 | `198.18.0.108` | ap | 0xe7f9 LBE-5AC-Gen2 | f6f39c6d | 198.18.0.109 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C09 | `198.18.0.110` | ap | 0xe7f9 LBE-5AC-Gen2 | c6b62549 | 198.18.0.111 (station) | active | AMBIGUOUS | LIVE_READONLY_INVENTORY |
| C10 | `198.18.0.111` | station | 0xe7f9 LBE-5AC-Gen2 | fe14d1ef | 198.18.0.110 (ap) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C11 | `198.18.0.112` | ap | 0xe7f9 LBE-5AC-Gen2 | e8eabc59 | 198.18.0.113 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C12 | `198.18.0.114` | ap | 0xe7f9 LBE-5AC-Gen2 | 3d799a39 | 198.18.0.115 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C13 | `198.18.0.92` | station | 0xe7f9 LBE-5AC-Gen2 | bf009de3 | 198.18.0.91 (ap) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C14 | `198.18.0.91` | ap | 0xe7f9 LBE-5AC-Gen2 | 2bcf2ced | 198.18.0.92 (station) | active | LOCAL_EDIFICIO_SITE | LIVE_READONLY_INVENTORY |
| C15 | `198.18.0.116` | ap | 0xe7f9 LBE-5AC-Gen2 | ca5787d9 | 198.18.0.117 (station) | disconnected | LOCAL_EDIFICIO_SITE | OFFLINE_ARTIFACT_INFERENCE |

- 15 candidatos: 12 LiteBeam (0xe7f9) y 3 PowerBeam (0xe3d6). Cableado local: true 0, false 0, unknown 15. C09 con C10 y C13 con C14 son los dos extremos de un mismo enlace.
- "Ubicación LOCAL_EDIFICIO_SITE" significa que UISP archiva el equipo en ese sitio; no significa que esté enchufado al router de borde o a un switch PoE local. C15 sale solo de la copia de UISP del repo (OFFLINE_ARTIFACT_INFERENCE), no del inventario en vivo.
- Los 46 extremos remotos de clientes no se listan. Todos los candidatos son enlaces PtP que figuran activos (salvo C15): tocar un extremo interrumpe un enlace en servicio.
- Mejor candidato por criterios offline: C07 (`198.18.0.106`), empatado con C01, C05 y C08; el desempate alfabético por nombre es arbitrario. Nivel de afirmación: OFFLINE_ARTIFACT_INFERENCE_NOT_PROVEN_WIRED. Conclusión: ninguno con evidencia suficiente para afirmar acceso por cable local desde esta red.
- Exclusiones SG-01 explícitas: no se lista nada del backbone Edificio Principal -> Almafuerte (.60) -> Guarida (.61), ni `198.18.0.79` ni `198.18.0.80` (switches PoE), ni el router de borde `198.18.0.2`, ni `ether2-sw-poe200`. También se excluye por prudencia el salto PTP-Alma (.56 y .57) y los paneles Guarida (.82 a .86); AGENTS.md solo nombra .60/.61 y la interfaz, así que esa ampliación es conservadora (1332A, conflicto SG01_HOP1_NOT_IN_AGENTS). Excluidos y listados: 4 equipos de infraestructura; contados sin listar: 68 por cadena de sitio, 17 por IP en la radiografía de Guarida, 10 por MAC y 7 por par en el conjunto protegido.
- Conflictos abiertos: 14 (mapeo placa a modelo contradictorio en textos viejos, y el grafo 1181A no tiene nodo del Edificio Principal). El mapeo 0xe7f9 = LiteBeam 5AC Gen2 y 0xe3d6 = PowerBeam 5AC Gen2 viene del catálogo del operador, no de los bytes de la imagen.
- C13 y C14 son los dos extremos del PtP-Colo (un solo enlace). Es el único con radiografía viva y backup mtd0/1/4/5 de ambos extremos (1344A y 1345A); ver sección 6.

## 3. Plan acotado por riesgo (no es riesgo cero)

Premisas: flashear el extremo local de un enlace en servicio lo interrumpe; la vuelta atrás es un reflasheo por cable, no el watchdog; cambiar un AP o cliente stock de producción es una mutación que exige aprobación del operador (SG-03 a SG-05). Nunca pedir subir a una torre ni traer un radio remoto al switch local. Nada de esto se ejecuta desde esta etapa.

1. Elegir dirección y unidad. Preferible una unidad libre o en banco, no un enlace en servicio; si solo hay candidatos en servicio, acordar una ventana con aviso. Dirección A, AP OpenWrt con cliente stock: el AP stock del Edificio se reemplaza y el remoto queda stock; no hay comando del lado stock. Dirección B, AP stock con cliente OpenWrt: es la pregunta del operador y es la que falló en banco (sección 1). Con `--flash-end partner` el verificador evalúa el otro extremo.
2. Verificador de pre-vuelo (solo lectura, sin red): `python tools/deploy/verify_litebeam_edificio_principal_hybrid_preflight.py --auto-image --prebuilt-image-ok --out DIR/preflight.json`. Opciones reales: `--candidate-id`, `--image`, `--board-id`, `--flash-end`, `--scan-dir`, `--selftest`. Salidas 0 / 10 / 20 (READY_FOR_OPERATOR_REVIEW, NOT_READY, INSUFFICIENT_DATA). Hoy: NOT_READY en las 15 unidades; READY solo significaría que el archivo se puede mostrar al operador.
3. Respaldo mtd0, mtd1, mtd4 y mtd5 de ambos extremos antes de flashear: `python tools/deploy/backup_and_verify_production_ptp_mtd.py --ap-ip AP_IP --sta-ip STA_IP --out-dir DIR`. Pide el par completo (también el extremo remoto, solo lectura por SSH, que sigue siendo tocar un radio de producción). Evidencia: la CLI y el orquestador estaban solo en dry-run (`docs/STAGE1258A_TARJETA_OPERATIVA_PRIMER_PTP_PRODUCCION_Y_GUARIDA_PANEL2_ES.md`); la lectura viva de solo lectura corrió después una vez, sobre el PtP-Colo, con 8 de 8 volcados verificados por sha256 (`artifacts/verification/stage1345a_ptp_colo_mtd_backup_and_art_sha256.json`). mtd0, mtd1 y mtd5 son protegidas: nunca se escriben.
4. Imagen. La prebuilt que elige `--auto-image` es `firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release/openwrt-24.10.4-ubnt-lbe5ac-gen2-openmax-public-factory.bin`, presente en disco, 6947480 bytes, sha256 `97ae94bf5a116ca77e14a72b78d5983b97cb07323eba2e2e4bc211e971eb6304` (recalculado desde el archivo). Fijada por el recibo `artifacts/autoresearch/stage132a_public_lbe5ac_pbe5ac_release_receipt.json`; sin recibo de flasheo vivo; es para puesta inicial por cable, sin perfil de migración remota ni credenciales guardadas. El hash del enunciado, `05fc87bc52f946897fc477a86b3be4d8ff32dc9d9ff95f861d7eb181448e9de8`, no aparece en ningún recibo ni archivo del repo: NOT_VERIFIED, no se asume ninguna identidad. Una imagen SquashFS propia con preconfiguración no se puede emitir (988A BLOCKED). Para el PtP-Colo el perfil de 1346A nombra en cambio la imagen oficial stock; son artefactos distintos y ninguna sirve hoy para un OTA remoto (sección 6).
5. Cambio del lado stock (solo dirección B), mutación de producción con aprobación explícita; el verificador solo las imprime. Los comandos literales del enunciado, `echo allow_80211=1 > /proc/sys/dev/uph_wifi0/config` y `echo op_mode=0 > /proc/sys/dev/uph_wifi0/config`, son UNVERIFIED: esa ruta solo aparece en archivos propios de la Wave 49 que la citan, y ninguna fuente primaria la documenta (1386A). Lo documentado difiere entre fuentes: `iwpriv ath0 wds 1` (68A, vivo en 8.7.11), parámetros `host_80211_enable` y `ubnt_op_mode` del módulo umac (84A, 8.7.11), perillas por archivo bajo `uph_wifi0` (82A, silenciosas ante fallo, ruta sin verificar en 8.7.25) y `allow_80211` como opción de wpad del cliente (1159A). Ninguna se aplicó en 8.7.25 con un cliente OpenWrt que pasara datos.
6. Flashear primero la unidad local por cable, nunca por el aire. El remoto no se toca hasta tener evidencia del primero. Capturar antes y después el verificador 1097A (`tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py`) y un volcado de salud (`firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_v17_one_shot_health_dump.sh --peer HOST`, solo lectura).
7. Qué significa "registra contra el LiteBeam stock", en términos observables: (a) asociación completa con WPA2 en estado COMPLETED en el lado OpenWrt y la estación visible en el AP stock; (b) puente WDS de cuatro direcciones arriba y ping unicast en ambos sentidos, no solo ARP de difusión (esa es la firma del fallo de 105A); (c) tres de tres respuestas de ping en ráfagas repetidas, y los umbrales de aborto de 1125A (`docs/STAGE1125A_PTP_PRODUCTION_CANARY_MONITORING_AND_ABORT_CRITERIA.md`): pérdida mayor a 2 por ciento, p99 mayor a 40 ms o desbalance de cadenas mayor a 6 dB abortan, sin promediar. Recibos a guardar: manifiesto mtd antes y después, preflight, capturas 1097A, volcados de salud, salida de los comandos y el recibo del lane en vivo.
8. Watchdog. Ventana de 45 s fuera de DFS y de 120 s en DFS (`--dfs`), con rollback tras dos fallos de ping consecutivos (`firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh --arm --peer HOST`). Nivel de evidencia real: solo raíz falsa en la PC; no corrió en ningún radio, y restaura perillas y configuración, no firmware. Un flasheo malo no tiene red de seguridad automática.
9. Vuelta atrás. Reflasheo por cable con el respaldo mtd y la imagen stock en mano. No existe restauración automática de airOS stock en el repo (`restore_stock_airos8_with_known_cfg.sh` es un stub retirado que termina en exit 65). El procedimiento de recuperación por cable de un LiteBeam no está probado.

Go / no-go. GO requiere todo a la vez: verificador sin FAIL ni UNKNOWN relevante; cableado local probado con puerto nombrado; respaldo mtd hecho y verificado; ventana acordada con el operador; aprobación explícita del cambio stock; imagen en mano con su sha256 verificado. NO-GO ante cualquiera: unidad del backbone o switch PoE tocada o por tocar (SG-01), hash que no coincide, placa que no corresponde, par sin respaldo, o dato de que se desactivaría `ether2-sw-poe200`.
Abortar: pérdida, p99 o desbalance sobre los umbrales del punto 7; cambio de hash mtd entre antes y después; ping unicast que falla con asociación aparente (firma 105A). Si aborta, volver por cable; no reintentar sin preflight nuevo.

## 4. Qué NO está probado

- Un LiteBeam OpenWrt como cliente o AP contra un LiteBeam stock: nunca, en ninguna dirección.
- Que el firmware OpenWrt de LiteBeam arranque, asocie y pase tráfico: la imagen está construida, sin validación en hardware.
- Que el AP stock acepte datos de un cliente OpenWrt: en PowerBeam de banco los descartó; la causa sigue UNKNOWN.
- Que un AP OpenWrt admita un cliente LiteBeam stock: un caso en Panel1 quedó pendiente e ignorado.
- Todo `--execute` del orquestador 1279A (`tools/deploy/run_production_ptp_canary_one_command.py`): solo dry-run. El backup mtd vivo de solo lectura corrió una vez, en el PtP-Colo (1345A); falta en los demás candidatos.
- Watchdog v17 con vencimiento real de 45 s o 120 s en un radio; recuperación de un flasheo malo; reboot y persistencia.
- Cableado local de cualquier candidato, acceso desde esta red y credenciales del router de borde.
- Rendimiento, estabilidad, falsos positivos cero y aceptación de producción: UNKNOWN (veredicto vigente NO_GO en `docs/STAGE1128A_PTP_PRODUCTION_GO_NO_GO_DOSSIER.md`).

## 5. Cruce Sirq y RAM (1334A)

- Existen cifras vivas de softirq y RAM libre solo en sectores LAP-120: paneles 2 y 3 de Guarida con airOS stock (13.61 y 10.04 por ciento de softirq; 15.719 y 15.445 MiB libres) y Panel1 OpenWrt (10.012 MB de MemAvailable), todas lecturas pasivas únicas.
- El banco OpenWrt LAP-120 tiene 4 ventanas con softirq de AP de 21.965 por ciento (brazo B) y MemAvailable cerca de 15 MiB; son otra plataforma y otra carga.
- Ningún recibo de PtP PowerBeam o LiteBeam guarda softirq ni MemFree/MemAvailable (13 recibos y los árboles 1175A y 1176A, 0 aciertos): las celdas de PtP de las tres opciones siguen sin dato.
- Las cifras de 722A son literales fijos en el script, a lo sumo SIMULATED_MODEL_ONLY; no se usan como medición.
- Cruce propuesto sobre 1280A: 18 celdas, 8 STILL_GAP, 5 FILLABLE_WITH_WARNING, 5 NOT_COMPARABLE; ninguna aplicada, los archivos de 1280A no cambiaron.
- Hueco concreto para esta prueba: tomar `/proc/stat` (dos lecturas) y `/proc/meminfo` antes y después en cada ventana; hoy no existe línea base de LiteBeam.

## 6. Reconciliación Wave 58 (1386A, 1387A, 1389A)

- Interop: la afirmación de que 509A a 518A y FMX-DISC-32 probaron que op_mode=0 y allow_80211=1 arreglan el descarte de 105A es REFUTED_AS_STATED (`artifacts/verification/stage1386a_hybrid_interop_509a_vs_105a_and_image_sha_reconciliation.json`). FMX-DISC-32 trata de VLAN 107, shaping BNG y superframe LTU. Lo único vivo con esas perillas es el negativo de 105A; prueba viva de que pase: ninguna. La ruta /proc del enunciado sigue sin fuente primaria y queda UNVERIFIED.
- Imágenes: la carpeta artifacts, subcarpeta openwrt_wa_24.10.4, del enunciado no existe. Las oficiales de OpenWrt están en `firmware/openwrt/` (LiteBeam Gen2: sha256 `dafd701bc80f544f...`, 6881944 bytes). Las OpenMax ajustadas son otro artefacto: la fijada por 132A (`public_release`) es `97ae94bf5a116ca7...`, y v3 y v4 tienen hashes propios (`c96b493b60bdb60b...`, `4a5d61eafb245f34...`). El hash del enunciado sigue sin aparecer en los 810 archivos hasheados por 1386A (no equivale a ausente de todo el disco).
- Cuál imagen: el prevuelo 1333A con `--auto-image` elige la OpenMax de `public_release`; el perfil del PtP-Colo (1346A) nombra la oficial stock. Conflicto abierto; ninguna se puede reempaquetar con el perfil porque la emisión propia sigue BLOCKED (988A).
- PtP-Colo (C13 y C14): 1344A a 1346A dan radiografía viva, backups de ambos extremos y perfil staged; la frecuencia es 6035 MHz, 20 MHz, countrycode 511. El requisito de 5865 MHz como máximo está SOURCED en la tabla ath10k (1346A y `mac.c`), es un límite del driver y no regulatorio. Mover el enlace es el Step-0: mutación de producción, solo del operador.
- Matriz 1389A (una lectura GET de UISP, 0 escrituras): de 15 filas, 13 con 5865 MHz como máximo, 2 por encima (C13 y C14), 0 UNKNOWN; 14 filas vivas y 1 offline (C15, copia del 2026-10-17). De las vivas, solo 2 caen en un canal de la tabla ath10k: estar por debajo del tope no significa poder unirse sin mover canal.
- Checklist 1387A (`tools/deploy/verify_ptp_colo_105_62_54_end_to_end_checklist.py`): NOT_READY; detalle en el documento 1388A enlazado arriba.

## 7. Fuentes leídas

`AGENTS.md`, `docs/STAGE1258A_TARJETA_OPERATIVA_PRIMER_PTP_PRODUCCION_Y_GUARIDA_PANEL2_ES.md`, `docs/STAGE1280A_COMPARATIVA_DEFINITIVA_AIRMAX_STOCK_VS_AIRMAX_TUNEADO_VS_OPENWRT_TUNEADO_ES.md`, `tools/uisp/discover_edificio_principal_ptp_litebeam_candidates.py` (opciones reales `--live`, `--offline-only`, `--out`), `tools/deploy/verify_litebeam_edificio_principal_hybrid_preflight.py`, `tools/deploy/backup_and_verify_production_ptp_mtd.py` y los documentos citados arriba.
