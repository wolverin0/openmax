<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1491A (ES): saneamiento de credenciales y datos personales del repo (1488A), matriz consolidada del PtP-Colo con su libro de contradicciones (1489A), caminos de despliegue LBE5AC 1 y 2 (1490A) y qué NO está probado; sin valores secretos ni nombres -->
# Stage 1491A: saneamiento, matriz consolidada PtP-Colo y despliegue LBE5AC

Estado: `DOC_NOT_EXECUTED`. Síntesis offline de tres recibos y de archivos del repo; no tocó ningún radio, router ni switch y no autoriza ningún cambio. Toda mutación de producción es del operador.
Etiquetas: CONFIRMED / INFERRED / UNKNOWN / REFUTED. Clases: CONFIRMED_LIVE_HARDWARE, CONFIRMED_STATIC_BINARY, SIMULATED_MODEL_ONLY, HYPOTHESIS, OFFLINE_ARTIFACT_INFERENCE.
Contexto previo: `docs/STAGE1437A_TOPOLOGIA_FISICA_PTP_COLO_DIRECCION_HIBRIDA_E_IMAGENES_LBE5AC_ES.md` (topología, dirección híbrida e imágenes), `docs/STAGE1388A_CHECKLIST_UNIFICADO_PTP_COLO_105_62_54_INFRA_Y_BACKUP_MTD_ES.md` (checklist, NOT_READY) y `artifacts/verification/stage1386a_hybrid_interop_509a_vs_105a_and_image_sha_reconciliation.json` (veredicto REFUTED_AS_STATED).

## 1. Saneamiento de credenciales y datos personales (1488A)

Recibo fuente: `artifacts/verification/stage1488a_repo_secrets_and_pii_sanitization_audit.json` (carpeta ignorada por git). Los valores de credenciales y los nombres NO se copian aquí: solo archivo, tipo y estado. Todo es lectura y edición locales; no se contactó ninguna máquina.

Qué se encontró: 55 hallazgos en 46 archivos. Estados: 26 FIXED, 8 FIXED_SOURCE_BUT_RESIDUAL_RISK, 19 REQUIRED_OPERATOR_ACTION y 2 OUT_OF_SCOPE_REPORTED. Tipos: 23 claves Wi-Fi, 15 contraseñas de host, 10 contraseñas en una línea de comandos, 6 contraseñas candidatas y 1 credencial de servicio.
- La pieza central: la contraseña de la VM de construcción SquashFS como literales `VM_USER` y `VM_PASS` en `tools/deploy/build_stage65a_true_squashfs_factory_repack.py` y en `tools/bench/get_router_creds.py`, además de los otros constructores de la misma familia. Esos archivos nunca estuvieron en git: sin historial que reescribir.
- gitleaks 8.21.2 dio 96 aciertos genéricos y todos eran falsos positivos; NO detectó ninguna de las contraseñas débiles reales, que salieron del escáner de patrones propio. Un escáner de entropía no sirve para esta clase de secreto.
- Exposición en el historial git: una contraseña de la familia de hosts estuvo en `tools/upload_mission_control.py` en el commit 37c14fe, alcanzable desde `origin/main` y otras ramas, y se quitó después. El remoto es público: asumir expuesta. El gate lo recomprueba con git. Estado: REQUIRED_OPERATOR_ACTION.

Qué se corrigió y cómo:
- Nuevo `tools/vm_creds.py`: lee `FMX_SQUASHFS_VM_USER` y `FMX_SQUASHFS_VM_PASSWORD` solo del entorno, sin valor por defecto ni pregunta interactiva, y falla cerrado (fail-closed) con un `RuntimeError` que nombra la variable; importar no lee el entorno. El recibo registra 13 variables de entorno en total. `tools/bench/get_router_creds.py` y los demás scripts de una conexión leen con `os.environ[...]` y fallan con `KeyError` antes de conectar; `sudo -S -p ''` recibe la contraseña por stdin del canal, no por argumentos.
- La contraseña NO salió de la línea de comandos en las cadenas de repaqueteo SquashFS (8 filas, estado residual): el valor viene del entorno pero se sigue enviando como `echo <valor> | sudo -S ...` por SSH y es visible en la lista de procesos de la VM mientras corre el comando. Riesgo residual sin reestructurar; lo correcto es `sudo` sin contraseña o una sola escritura por stdin.
- Las 19 filas de claves Wi-Fi del banco y del enlace PtP quedaron sin editar a propósito: están incrustadas en comandos de banco y en payloads de firmware emitidos, y cambiarlas altera hashes fijados. La clave debe rotarse y moverse a `FMX_PTP_WPA_PSK` o `FMX_BENCH_WIFI_PSK` cuando se reemitan los kits. Dos documentos con una clave en prosa, `docs/STAGE15_LTU_PTMP_3UNIT_OTA_BENCHMARK.md` y `docs/archive/2026-10-25_full_history/BENCH_PLAN.md`, están sin seguimiento y NO ignorados: depurarlos antes de cualquier commit.
- Cobertura de `.gitignore`: `artifacts/verification/` está ignorado (`.gitignore` línea 198) y `artifacts/backups/` tiene su propio `.gitignore` con `*`; el gate recomprueba con `git check-ignore` y con cero archivos con seguimiento en `artifacts/backups`.

Datos personales y cascada de hashes:
- La tabla del recibo trae 6 filas (radiografía 1344A, doc 1347A, token del gate 1391A y fixtures de las suites 1386A y 1434A) con 0 ocurrencias después. El nombre pasó a una etiqueta de rol del mismo largo, así los tamaños registrados siguen válidos. El escáner ya no guarda el nombre en archivos con seguimiento: carga los tokens en tiempo de ejecución de `artifacts/backups/pii_person_tokens.local.json` (ignorado por git) más una heurística genérica.
- Discrepancia hallada por el gate y corregida después: el recibo declaraba cero, pero dos fixtures de las suites 1386A y 1434A todavía contenían un token de la lista local. Ya salió de ambos archivos y esos fixtures leen el token de la lista local no versionada. Es un defecto del entregable 1488A, no un hallazgo nuevo del repo.
- Cascada: redactar cambia el sha256 y rompe los pines de olas posteriores. Se parchearon 19 dependientes directos y 14 transitivos más 1 parche(s) de pin adicional(es), con la redacción primero y los parches después. Los archivos inmutables (`preserved/`, `*.snapshot`) no se parchearon a propósito y conservan el sha previo; los recibos históricos 47B tampoco. 1489A y 1490A recalcularon sus ledgers después de la marca de fin de redacción.
- La suite 1386A sigue con dos fallos por deriva externa (otros carriles agregan archivos pesados bajo `artifacts/` y cambian el recuento de archivos hasheados): no vienen de esta etapa y el recibo los registra aparte. La suite 1434A pasa en el recibo (82 pruebas).

Acciones EXCLUSIVAS del operador (ninguna se ejecutó aquí):
- Acción 1: rotar la contraseña de host, VM, notebook, router y radio que vivió en las herramientas sin seguimiento y en el commit público; suponer que se reutilizó en varios hosts y exportar la nueva solo por `FMX_SQUASHFS_VM_PASSWORD` y variables hermanas.
- Acción 2: rotar las claves Wi-Fi del enlace PtP y del banco y la contraseña de la cuenta de servicio de MikroTik; reemitir kits y pines cuando los generadores pasen a leer del entorno.
- Acción 3: decidir si se reescribe el historial público del commit expuesto, depurar los dos documentos con clave en prosa y retirar las copias en `scratch/`, `.codegraph` y artefactos que guardan los valores.
- Acción 4: decidir si se redactan las MAC y el nombre de clientes en volcados y recibos ignorados por git (requiere volver a fotografiar recibos históricos inmutables).
- Revisar otras copias: el recibo lista copias del mismo tipo de secreto en `.codegraph`, `scratch/` y `artifacts/re_proofs_and_reports_20261021` (ignoradas o sin seguimiento, sin valores aquí) y no cubre el historial de la shell ni de los editores.

Riesgos residuales: los apellidos de otros clientes siguen en el conjunto de tokens del gate 1337A y en el texto de topología de `AGENTS.md` (con seguimiento), fuera del encargo; la radiografía 1344A conserva coordenadas con más de tres decimales; el escaneo es por patrones y puede perder una credencial de forma inusual; `docs/` y `tests/` solo se revisaron por coincidencia literal.

## 2. Matriz consolidada PtP-Colo (1489A)

Recibo `artifacts/verification/stage1489a_ptp_colo_consolidated_readiness_matrix.json`, generado por `tools/deploy/build_stage1489a_ptp_colo_consolidated_readiness_matrix.py` (solo lectura local, sin red). Reúne las olas 56, 58, 64, 66, 69 y 71 en una matriz de nueve dimensiones.

Veredicto del recibo: NOT_READY (etiqueta de evidencia, no un porcentaje ni una autorización). 68 celdas: 19 OK, 31 OPEN, 15 BLOCKER, 3 UNKNOWN; 21 bloqueos en total (15 celdas y 6 contradicciones abiertas bloqueantes). Entradas de la matriz con sha256 recalculado: 92.

| Dim | Tema | OK | OPEN | BLOCKER | UNKNOWN |
| --- | --- | --- | --- | --- | --- |
| D1 | Identidad y ubicación física de los extremos |3 | 4 | 0 | 1 |
| D2 | Backups mtd0/1/4/5, ART y cfg de ambos extremos |10 | 1 | 0 | 0 |
| D3 | MK2-RS e Infra: drenaje de mangles |1 | 6 | 1 | 0 |
| D4 | Plan de canal, opciones de Step-0 y techo de tabla |2 | 8 | 1 | 1 |
| D5 | Dirección híbrida A contra B |0 | 2 | 1 | 0 |
| D6 | Imágenes y estado de las tuberías |1 | 3 | 2 | 0 |
| D7 | Rollback y watchdog |0 | 0 | 2 | 1 |
| D8 | Compuertas (SG-01, SG-03 a SG-05) y go/no-go |1 | 1 | 1 | 0 |
| D9 | Lista previa a la ejecución del operador |1 | 6 | 7 | 0 |

Qué dice cada dimensión, con su estado:
- D1 identidad y ubicación: IPs, placa 0xe7f9 y firmware CONFIRMED (lectura viva de solo lectura, 1344A). El AP 198.18.0.91 en Edificio Principal es INFERRED, confianza MODERATE: ninguna tabla de MAC aprendidas ni ARP de MK2-RS nombra una MAC de los radios, y las olas 69 y 71 no lo mejoraron (releyeron la misma captura). Qué radio está cableado a `ether10-colo`: UNKNOWN.
- D2 backups: los ocho volcados mtd0/1/4/5 de ambos extremos coinciden en sha256 con 1345A y 1434A; la validez de la ART queda OPEN (solo estática).
- D3 Infra: el drenaje de mangles de MK2-RS está planeado y NO ejecutado (BLOCKER); vaciar de golpe puede cortar sesiones NAT; hay un conflicto abierto sobre qué ids (`*1BA`, `*1BB`, `*172`, `*19C`) se ejecutan.
- D4 canal: la frecuencia actual es 6035 MHz, fuera de toda tabla ath10k (BLOCKER); el tope de la tabla es 5865 en el árbol principal y 5825 en la copia ath10k-ct (OPEN, sin observación en un radio OpenWrt real).
- D5 dirección híbrida: B (AP airOS, STA OpenWrt) REFUTED_AS_STATED (BLOCKER); A solo tiene filas vivas en equipos PtMP, nunca en este par.
- D6/D7 imágenes y rollback: 988A bloquea emitir una imagen NUEVA con payload FMX; las 20 imágenes públicas existen. Los watchdogs solo corrieron en arnés simulado: ningún actuador de rollback probado en un radio.
- D8 compuertas: go/no-go sigue en NO_GO; ninguna ola lo cambió. SG-03..05 siguen siendo del operador.

### 2.1 Libro de contradicciones (28 filas: 12 RESUELTAS + 16 ABIERTAS)

Ninguna se oculta: cada fila RESOLVED cita la evidencia que decide, y las ABIERTAS se listan con su dueño. Las cuatro que las olas ya conocían:

| Id | Tema | Estado | Evidencia decisiva |
| --- | --- | --- | --- |
| CT-01 | `agents_step1_direction` | OPEN | AGENTS.md prescribe la dirección B; 1386A y 1435A la dan por REFUTED_AS_STATED |
| CT-02 | `ath10k_5ghz_max_mhz` | OPEN | tope 5865 del árbol principal frente a 5825 de ath10k-ct; las imágenes usan ath10k-ct y la tabla binaria nunca se extrajo (1391A, 1381A) |
| CT-09 | `pin_105a_factory_ap_241` | OPEN | 105A cita hashes de imágenes que ya no coinciden con los archivos del kit (1386A, 1436A C3); es el banco PBE, no el par PtP-Colo |
| CT-11 | `ptp_colo_ap_ip` | RESOLVED | IPs reales 198.18.0.91 y .54 por lectura viva (1344A) y compuerta G3 de 1387A; el nombre `51_50` quedó solo en nombres de archivo |

El extremo local sigue INFERRED (no CONFIRMED) por la celda D1.03, que además recalcula por qué las olas 69 y 71 no lo subieron. Otras abiertas con peso:
- CT-01 (bloqueante, ABIERTA): el Step 1 documentado en AGENTS.md contradice la evidencia (dirección B refutada).
- CT-04 (bloqueante, ABIERTA): qué reglas de mangle se deshabilitan: lo decide Infra con el operador.
- CT-07 (bloqueante, ABIERTA): distancia GPS cerca de 1,8 km contra 450 m de timing y 600 m del perfil preparado: sin resolver.
- CT-13 (bloqueante, ABIERTA): AGENTS.md prohíbe pedir acceso físico al extremo remoto y la evidencia dice que el arranque de las imágenes públicas solo se recupera por cable.
- CT-16 (bloqueante, ABIERTA): las olas favorecen opciones distintas de Step-0 (ver 2.2).

### 2.2 Opciones de Step-0 y qué favorece cada ola

Step-0 es mover ambos extremos airOS de 6035 MHz a un canal de la tabla antes de cualquier prueba OpenWrt. Todo es modelo simulado sobre inventario UISP, no un barrido de espectro (clase SIMULATED_MODEL_ONLY).

| Opción | Canal | DFS | Qué se sabe |
| --- | --- | --- | --- |
| K1a | 149 (5745 MHz) | no | primera de la ola 56; solo seleccionable si el ancho de `ptp-abeni-ap` es 20 MHz o menos, y ese ancho es UNKNOWN |
| K1b | 165 (5825 MHz) | no | alternativa no DFS; en el tope de la copia ath10k-ct |
| K2 | 56 (5280 MHz) | sí, 60 s de CAC y watchdog de 120 s | la ola 64 la llama el movimiento único más limpio si se acepta DFS |
| K3 | 149 más mover `ptp-abeni-ap` a 56 DFS | mixto | dos enlaces; mayor probabilidad de completar en la simulación |

La ola 56 pone el canal 149 primero; la ola 64 favorece K2 y condiciona K1a; la ola 69 no elige y deja las cuatro opciones y cuatro decisiones al operador; las olas 58, 66 y 71 no eligen. La simulación ordena la probabilidad de completar K3, K2, K1a, K1b, pero K2 tiene mayor mediana de parada (cerca de 459 s frente a 340 s) con parámetros supuestos. Es un desacuerdo de objetivos, no un error de hecho, y queda ABIERTO y bloqueante: decide el operador.

### 2.3 Chequeos que quedan al operador (lista D9 del recibo)

- D9.01 [BLOCKER] (compuerta del operador): elegir la opción de Step-0 (K1a, K1b, K2 o K3) y decidir si se acepta DFS (60 s de CAC y watchdog de 120 s).
- D9.02 [OPEN]: confirmar el ancho de canal de `ptp-abeni-ap` (UNKNOWN; decide si K1a es elegible).
- D9.03 [OPEN]: correr airView en ambos extremos a 5745, 5825 y 5280 MHz (la ocupación del inventario no es un barrido).
- D9.04 [OPEN]: elegir el techo de planificación (5825 de ath10k-ct o 5865 del árbol principal) u observar la tabla en un radio LiteBeam con OpenWrt.
- D9.05 [BLOCKER] (compuerta del operador): Infra: drenar los mangles WAN COLO de MK2-RS (decidir el conjunto de ids: primero `*1BA` y `*1BB`, `*172` y `*19C` condicionales) con ventana de mantenimiento.
- D9.06 [BLOCKER] (compuerta del operador): Step-0: reconfigurar AMBOS extremos airOS (primero la lista de exploración del STA, luego el AP) al canal elegido, con watchdog de 45 s o 120 s.
- D9.07 [OPEN]: tras Step-0 releer mtd4 de ambos extremos y reverificar mtd0, mtd1 y mtd5 contra los hashes de G1 (mtd4 cambia legítimamente).
- D9.08 [OK]: verificación de backups antes de cualquier flasheo: 8 de 8 volcados con sha256 igual al de 1345A (repetir en la máquina que los guarda).
- D9.09 [BLOCKER] (compuerta del operador): organizar la recuperación cableada en el extremo flasheado (primer arranque con radio apagado, LAN 198.18.0.50/24, sin DHCP); choca con la regla de no pedir acceso físico.
- D9.10 [BLOCKER] (compuerta del operador): una transacción nativa de rollback revisada para este enlace (los actuadores del kit están retirados).
- D9.11 [BLOCKER] (compuerta del operador): flashear los extremos en servicio (Step-1 y Step-2 híbridos) NO está autorizado; la emisión de imágenes propias está bloqueada por 988A y solo existen las imágenes de la tubería A.
- D9.12 [OPEN]: leer la tabla de MAC aprendidas o ARP en MK2-RS para confirmar qué radio está cableado a `ether10-colo` (subiría la ubicación del AP de INFERRED).
- D9.13 [OPEN]: resolver el parámetro de distancia (GPS entre 1,7 y 1,8 km contra 450 m de timing y 600 m del perfil preparado) antes de hornear cualquier perfil.
- D9.14 [BLOCKER] (compuerta del operador): aprobación del operador para mutar los extremos stock de producción (SG-03 a SG-05); ningún par puede otorgarla.

## 3. Despliegue LBE5AC: Camino 1 contra Camino 2 (1490A)

Recibo `artifacts/verification/stage1490a_lbe5ac_squashfs_repack_pipeline_audit.json`, herramienta `tools/verify/build_stage1490a_lbe5ac_squashfs_repack_pipeline_audit.py`. Placa `ubnt,litebeam-ac-gen2` (0xe7f9). Auditoría estática y local: la prueba de repaqueteo corrió en un directorio temporal fuera del repo, sin red, sin SSH y sin tocar ningún radio.

| Dimensión | Camino 1: flashear imagen pública y instalar por SSH | Camino 2: imagen repaquetada con payload |
| --- | --- | --- |
| Veredicto | AVAILABLE_UNPROVEN | BLOCKED |
| Requisitos | acceso cableado L2 a 198.18.0.50, SSH, decisión de Step-0 | bootstrap activo revisado, árbol de payload y `rc.local`, host POSIX root con herramientas con hash (tubería B) o cambio del constructor (tubería A) |
| Probado (recibo) | seis imágenes fijadas por 132A/144A/170A e idénticas a sus `_repro`; el flujo LED vivo es del banco PBE (1446A) | un repaqueteo NULO sin payload es reproducible; los tests de watchdog son offline |
| No probado | cualquier arranque, SSH, paso uci/radio o watchdog en un LiteBeam; mac80211 modificado en hardware | cualquier imagen con payload emitida o arrancada; vendor signature |
| Acceso cableado | SÍ para el primer arranque (radio apagado, LAN 198.18.0.50/24, sin DHCP) | SÍ salvo que el bootstrap habilite un camino de radio seguro, que no existe |
| Alcance de 988A | no lo cubre: 988A bloquea emitir imágenes NUEVAS con payload FMX; las 20 existentes son de la tubería A | lo bloquea directamente (tubería B) |

Camino 2 tiene 5 bloqueos en el recibo: bootstrap retirado rechazado por la tubería B, anfitrión no root sin hashes fijados de las herramientas, el conjunto requerido no admite el overlay LED ni el watchdog v17, la tubería A necesitaría un cambio del constructor y no existe recibo de arranque de ninguna imagen en un LiteBeam.

Prerrequisitos medidos: WSL Ubuntu trae `mksquashfs` y `unsquashfs` 4.6.1 pero el usuario no es root y `sudo` pide contraseña, así que la tubería B no puede correr; `squashfs-tools-ng` 1.3.2 de la tubería A está presente con el hash fijado. Las imágenes públicas NO traen el watchdog ni los scripts FMX en su rootfs (releído y coincidente con 1436A): el bootstrap, las variantes por rol y el cargador PHY son stubs retirados de 974 bytes; solo los watchdogs v1 y v17 y los scripts LED son scripts reales.

Consecuencia del acceso cableado: las imágenes públicas arrancan con el radio deshabilitado y sin canal, así que un extremo remoto flasheado queda recuperable solo por cable. Eso choca con la regla de `AGENTS.md` de no pedir acceso físico al extremo remoto; el recibo lo registra como contradicción bloqueante, no como resuelta.

Alcance de 988A: `docs/STAGE988A_SQUASHFS_WATCHDOG_AND_REPO_HYGIENE_GATE.md` deja la emisión nativa en NOT_EXECUTED y BLOCKED para una imagen NUEVA con payload; no invalida las imágenes de la tubería A. Ver `docs/STAGE1437A_TOPOLOGIA_FISICA_PTP_COLO_DIRECCION_HIBRIDA_E_IMAGENES_LBE5AC_ES.md` (sección 3.1).

## 4. Qué NO está probado

- Que alguna imagen LBE5AC (v1, v3, v4 o una repaquetada) arranque, asocie o pase tráfico en un LiteBeam real: no existe recibo de flasheo ni de arranque de ninguna imagen LiteBeam.
- Qué radio está cableado a `ether10-colo` y por tanto cuál extremo está en Edificio Principal: INFERRED, no CONFIRMED.
- Que la dirección B (AP airOS, STA OpenWrt) funcione; que la dirección A funcione con un STA PtP stock en este par.
- Que un watchdog de rollback corra o restaure en un radio: solo hay pruebas offline y de arnés simulado.
- Que OpenWrt pueda sintonizar el canal elegido: el tope de la tabla (5825 o 5865) nunca se observó en un radio real.
- El estado actual de radios, MK2-RS y UISP: todo es de la hora de captura de cada recibo; esta etapa no leyó nada en vivo.
- Que la tubería A pueda reconstruir hoy las imágenes públicas, ni que una repaquetada con payload cumpla las reglas de la tubería B.
- Que las credenciales expuestas no se hayan copiado fuera de este árbol de trabajo: el repo no lo puede demostrar.
- Ausencia de otras copias del dato personal redactado: solo se limpiaron los archivos citados; el historial git no se buscó por el nombre del cliente más allá del árbol con seguimiento.
- Que la rotación de credenciales se haya hecho: es una acción del operador y el repo no puede demostrarla.
