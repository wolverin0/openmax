<!-- doc-head: Stage 3128A (W461) ES: vigilancia semanal de upstream OpenWrt, solo lectura con gh api, sobre openwrt/openwrt, openwrt/mt76 y greearb/ath10k-ct. Filtra issues y PRs de los ultimos 7 dias que tocan ath10k, ath10k-ct, ath79, mac80211, nuestras 5 placas o los temas abiertos WEDGED, airtime y keep list de sysupgrade. Clasifica en alta, media y baja, marca como conocidos los ya revisados en 3113A, 3116A y 3136A, y escribe artifacts/openwrt_watch/AAAA-MM-DD.json y su resumen. Tarea FuturaMAX-OpenWrtWatch-3128A, lunes 08:00 ART; primera corrida 31/10 -->
Que cubre: que mira el script, como clasifica, donde deja los resultados y la primera corrida.
Estado: instalado y corrido. 0 escrituras en GitHub y en equipos.
Codigo: tools/openwrt_watch/openwrt_watch.py y tools/openwrt_watch/run_openwrt_watch.ps1. Resultados: artifacts/openwrt_watch/.
Leer cuando: cada lunes, al abrir el resumen nuevo, o antes de cambiar la base OpenWrt o el driver ath10k-ct.
<!-- /doc-head -->
# Stage 3128A: vigilancia semanal de OpenWrt (W461)

## 1. Que hace

- **Consulta:** `gh api repos/<repo>/issues?state=all&since=<hace 7 dias>` paginado. La API de issues incluye los PRs.
- **Repos:** openwrt/openwrt, openwrt/mt76 y greearb/ath10k-ct.
- **Terminos:** se buscan en titulo, cuerpo y etiquetas.
  - Driver: ath10k, ath10k-ct, ath79, mac80211.
  - Placas: lap-120, litebeam-ac-gen2, nanostation-ac-loco, powerbeam-5ac-gen2 y powerbeam-5ac-500, por id de imagen y por nombre comercial.
  - Temas abiertos: WEDGED o recovery de firmware, airtime, y la keep list de sysupgrade (`sysupgrade.conf`, keep list, `keep.d`).
- **Regla anti-ruido:**
  - En openwrt/openwrt y mt76, ath10k, ath79 y mac80211 solo cuentan si estan en el titulo, salvo que tambien haya una placa o un tema. Si no, cada `DEVICE_PACKAGES` con kmod-ath10k-ct coincide.
  - "recovery" sin contexto de crash o driver no cuenta, porque es texto comun de soporte de equipos (modo recovery de U-Boot). Tampoco cuenta "sysupgrade ... keep settings".
- **Relevancia:**
  - Alta: ath10k en el titulo, nuestras placas, keep list, o el repo greearb.
  - Media: target ath79, nucleo mac80211, o airtime/wedged en otro driver.
  - Baja: otros drivers dentro del paquete mac80211; quedan solo en el JSON.
- **Conocidos:** los items ya revisados quedan marcados con su doc de origen y van al final.
  - STAGE3113A: openwrt #22748, #24806, #26177, #22344, #26037, #25646 y mt76 #1132.
  - STAGE3136A: openwrt #25416, #6937, #7016, #22301, #10225, #17234, #23986 y ath10k-ct #236, #140, #196, #233, #212.
  - Los commits de STAGE3116A (fcbdb70, bb84e159, ac71b14d) son codigo, no issues.
- **Salida:** `artifacts/openwrt_watch/AAAA-MM-DD.json` (fecha ART) y `AAAA-MM-DD_resumen.md` en español. Cada corrida agrega una linea a `watch.log`. Si un repo falla, se registra en `errors`, los otros siguen y el codigo de salida es 1.
- **Tarea:** `FuturaMAX-OpenWrtWatch-3128A`, semanal, lunes 08:00 ART. Ejecuta powershell oculto con `run_openwrt_watch.ps1`, tiene un tope de 30 min y arranca al primer momento disponible si se perdio el horario. Usa la sesion de `gh` del usuario y, como la tarea 2581A, necesita sesion iniciada.

## 2. Primera corrida (31/10/2026, ventana 24/10-31/10)

- **Escaneados y coincidentes:** openwrt/openwrt 44 de 434; mt76 3 de 17; ath10k-ct 1 de 1.
- **Sin revisar antes:** alta 4, media 25, baja 17. Conocidos: 2 (ath10k-ct #236 y openwrt #24806).
- **Alta:**
  - openwrt #26263 (ath10k-ct: CONFLICTS entre variantes).
  - openwrt #26262 (conflicto ath10k contra ath10k-ct).
  - openwrt #26253 (ath10k-ct: repartir las interrupciones PCIe de Wi-Fi entre CPUs). Toca nuestro driver; la utilidad en ath79 de un nucleo es UNKNOWN.
  - openwrt #22793 (crashes en ath10k_ahb en ipq40xx con 25.12.2): otra placa, pero mismo driver y salto de base que STAGE3119A.
- **Detalle completo:** `artifacts/openwrt_watch/2026-10-31_resumen.md`.
- **Corrida desde la tarea:** `Start-ScheduledTask` 13:28 ART, LastTaskResult 0, misma salida en `watch.log`. Proxima corrida: 02/11 08:00.

## 3. Limites

- La API de issues trae los cambios de la ventana, incluidos comentarios. Un issue viejo con un comentario nuevo aparece; `new_this_window` dice si se abrio en la ventana.
- Siguen colandose items de prioridad media por texto del cuerpo, como RAK7289 por "wedged". Se aceptan antes que perder un caso real; ajustar los terminos en `TERMS` si molesta.
- No lee commits sueltos de las ramas ni la lista de correo. `--selftest` cubre el filtro y la clasificacion.

## Decision del operador 31/10
- La tarea de Windows `FuturaMAX-OpenWrtWatch-3128A` se borro (31/10 ~17:10 ART). La vigilancia pasa a ser una fuente del bot de Hermes que carga el hyperresearch, cuando este listo; hasta entonces no corre nada.
- El script queda como insumo reutilizable: `python tools/openwrt_watch/openwrt_watch.py` (JSON + resumen en `artifacts/openwrt_watch/`). Mejora pendiente: relevancia por placa y bus (ath79 de un nucleo, QCA988x por PCIe).
