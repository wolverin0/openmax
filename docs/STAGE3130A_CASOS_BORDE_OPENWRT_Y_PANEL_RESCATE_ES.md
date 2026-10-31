<!-- doc-head: Stage 3130A (W463) ES, trabajo de escritorio sin tocar equipos: 9 casos borde OpenWrt de nuestra red (crash o WEDGED de ath10k, poca RAM, radar DFS, corte de energia en un extremo del PtP, sysupgrade que pierde los kits 99-fmx, CPE airOS stock contra AP OpenWrt, reloj sin NTP, cambio de distancia o coverage class, bridge UISP caido) con que pasa hoy, evidencia, prueba de banco y que falta; sigue a EC-01..EC-08 de airOS. Estudio de panel de rescate en frio por sitio; ath10k-ct 6.10 no tiene canales de 5/10 MHz (CONFIRMED estatico) -->
Que cubre: casos borde OpenWrt con prueba de banco y panel de rescate con disparo medido.
Estado: estudio y plan; 0 escrituras en equipos. Datos maquina: artifacts/autoresearch/wave463_edge_cases_rescue.json.
Se apoya en: STAGE3136A (bugs y reinicios), STAGE3116A y STAGE3119A (ath10k-ct y 25.12), STAGE3124A (reinicio nocturno), STAGE2896A y STAGE2966A (memoria), STAGE3107A y STAGE3108A (distancia), STAGE1335A (hibrido stock/OpenWrt). No los repite.
Leer cuando: antes de un sysupgrade, de migrar un panel con CPEs airOS o de agregar un radio de respaldo.
<!-- /doc-head -->
# Stage 3130A: casos borde OpenWrt y panel de rescate (W463)

## 1. Punto de partida: EC-01..EC-08 de la era airOS

EC-01 a EC-06 (CASILLERO-04) y EC-08 (Stage 99A) se probaron sobre airOS:
- EC-01: CPE offline sin bloquear la interop.
- EC-02: arranque en frio en MCS0.
- EC-03: guarda LNA de campo cercano en -45 dBm.
- EC-04: VLAN con multiq.
- EC-05: falsa alarma de colector congelado.
- EC-06: CSA DFS de 4,38 s y supresion de alertas durante CAC.
- EC-08: churn de CPE a mitad de trafico.

Con los paneles de Guarida en OpenWrt 24.10.4 (ath10k-ct 6.10, kernel 6.6.110), esas pruebas no se traspasan. Los casos de abajo son los de OpenWrt; OW-03 y OW-06 son la continuacion de EC-06 y EC-01.

## 2. Casos borde OpenWrt

### OW-01 Crash de firmware o ath10k WEDGED
- **Hoy:** ath10k-ct 6.10 reinicia el firmware tras un crash. Si queda WEDGED no se recupera solo: los 3 fixes de recovery estan en ath10k 7.2 (STAGE3116A). Las imagenes 25.12 con esas guardas estan compiladas y no flasheadas (STAGE3119A). El reinicio nocturno por cron existe, probado solo en el LiteBeam de banco y con `enabled=0` (STAGE3124A).
- **Evidencia:** 10 nodos leidos desde su arranque: 0 "firmware crashed", 0 wedged, 0 SWBA, 0 tx hang, 0 OOM. pstore vacio en 10/10, asi que lo previo a un reinicio no se ve (STAGE3136A).
- **Banco:** LiteBeam de banco con `simulate_fw_crash` de debugfs (soft, hard, assert). Contar recuperaciones, tiempo hasta trafico y estado final. A/B contra la imagen con el backport (tarjeta 2 de STAGE3136A).
- **Sin probar:** recuperacion de un WEDGED real; si el watchdog de hardware reinicia la placa; que un CPE vuelva solo tras un reinicio del AP en produccion.

### OW-02 Poca memoria en placas de 64 MB
- **Hoy:** el AP de Panel1 (56 MB utiles) tuvo un incidente de memoria con causa y arreglo (STAGE2896A). Hay admitter con log acotado (STAGE2945A), dimensionado de colas (STAGE2966A) y guarda del daemon de 6144 KiB.
- **Evidencia:** memoria libre justo antes de los reinicios sueltos: 1,8 a 14,8 MB, sin A/A (STAGE3136A). `fq_overmemory` en ptp_colo_sta: 26 436 en 67 h.
- **Banco:** LAP-120 con las mismas colas, cargado con estaciones y trafico. Medir MemAvailable, Slab y el contador de OOM. Leer `vm.panic_on_oom` y `kernel.panic` para saber si un OOM termina en reinicio.
- **Sin probar:** el comportamiento ante OOM real y si los reinicios sueltos (7 de cpe_200_169) son por memoria.

### OW-03 Radar DFS
- **Hoy:** hostapd hace CAC antes de transmitir en canales DFS (60 s; 600 s en 5600-5650 en ETSI). Ante radar hace CSA a otro canal, o baja el AP si no tiene alternativa.
- **Exposicion:** Panel3 (5745) y PtP-Colo (ch153, 5765) estan fuera de DFS. Panel1 y Panel2 no se leyeron en esta pasada (UNKNOWN).
- **Evidencia:** EC-06 se probo solo en airOS (Stage 90A). En OpenWrt no hay prueba.
- **Banco:** AP de banco en un canal DFS. `dfs_simulate_radar` de debugfs de ath10k y `hostapd_cli chan_switch`. Medir el tiempo hasta que vuelve cada CPE (OpenWrt y airOS) y si el AP queda caido.
- **Sin probar:** todo el camino DFS en OpenWrt.

### OW-04 Corte de energia en un extremo del PtP
- **Hoy:** PtP-Colo es AP y STA OpenWrt con WDS. Si cae un extremo, el otro queda escaneando (STA) o sin estacion (AP) hasta que el par arranca.
- **Evidencia:** retorno de un LiteBeam tras reinicio suave en menos de 76 s, y cron a primer boot en 91 s; es una cota, no una calibracion (STAGE3124A). PtP-Colo sin reinicio desde la migracion; un deauth por inactividad con corte menor a 60 s (STAGE3136A). El 31/10 a las 14:27Z reiniciaron 10 equipos de Guarida en 61 s; su causa es UNKNOWN, compatible con un corte de energia de sitio no probado.
- **Banco:** par PtP de banco. Cortar la energia de un extremo desde el PoE del banco, nunca desde .200/.201 ni ether2-sw-poe200. A/A x3 por extremo, midiendo tiempo hasta trafico y orden de arranque (STA antes que AP y al reves).
- **Sin probar:** recuperacion medida en el PtP real; carrera de arranque entre extremos.

### OW-05 sysupgrade que pierde los kits 99-fmx
- **Hoy (CONFIRMED estatico):**
  - Los kits son scripts de uci-defaults: corren una vez y se borran. Instalan helpers en `/usr/sbin/fmx_*` (por ejemplo `fmx_qca_htt_tx_compl_guard.sh` y `fmx_ap_4addr_peer_healer.sh`) y ganchos en `/etc/rc.local` y `sysctl.conf`.
  - sysupgrade conserva `/etc/config/*`, los conffiles de base-files (`/etc/rc.local`, `/etc/sysctl.conf` y otros de `/etc`) y lo que liste `/etc/sysupgrade.conf`, que viene vacio.
- **Efecto INFERRED:**
  - Con una imagen sin los kits quedan los valores uci y sysctl, pero desaparecen los helpers. `rc.local` llama scripts que ya no existen y falla en silencio, sin guardas.
  - Con una imagen que trae los kits en `files/`, como la que arma `futuramax_openwrt_imagebuilder_packager.py`, uci-defaults vuelve a correr.
  - `/etc/crontabs/root` no esta en la lista: el cron del reinicio nocturno se perderia.
- **Arreglo propuesto, no aplicado:** listar `/usr/sbin/fmx_*`, `/etc/fmx/` y `/etc/crontabs/root` en `/etc/sysupgrade.conf`, o armar siempre la imagen con los kits.
- **Banco:** LiteBeam de banco con un kit, `sysupgrade` con conservar config a la misma imagen y a una sin kit. Comparar lista y hash de archivos, codigo de salida de `rc.local` y crontab.
- **Sin probar:** todo lo anterior en un equipo.

### OW-06 CPE airOS stock contra AP OpenWrt
- **Hoy:** Panel2 tiene mayoria de CPEs airOS. El WDS con airOS 8 necesita nuestro parche propio de mac80211 (strip ETH_P_TEB 0x6558), sin upstream, que hay que re-portar en cada salto de base (STAGE3136A #11). La regla SG-03..05 manda probar interop 100 % en banco antes de migrar un AP.
- **Evidencia:** CPE .80 hibrido airOS 8 con delta de fq_overmemory cero (nota 667). STAGE1335A dejo REFUTED_AS_STATED la interop afirmada antes.
- **Banco:** LAP .20 OpenWrt con LBE .240 airOS stock. Asociacion WDS, DHCP a traves del bridge, throughput, vuelta tras reinicio del AP y CSA. Repetir con la imagen 25.12 de STAGE3119A.
- **Sin probar:** airOS 8.7.25 contra 8.7.11 y la imagen 25.12 con CPE airOS.

### OW-07 Reloj sin NTP
- **Hoy:** estas placas no tienen RTC. Al arrancar, OpenWrt toma la hora del archivo mas nuevo de `/etc` y espera a NTP. En el banco el LiteBeam estaba unos 338 s atrasado (STAGE3124A).
- **Efecto INFERRED:**
  - Horas de logs y telemetria corridas.
  - El cron nocturno dispara a otra hora.
  - El bridge UISP valida certificado en produccion (decision del 30/10): un reloj fuera de la vigencia del certificado puede cortar TLS. WPA no depende del reloj.
- **Banco:** bloquear NTP en el LiteBeam de banco, reiniciar y medir la deriva. Probar el TLS del bridge con el reloj corrido.
- **Sin probar:** el efecto sobre el bridge y la deriva por dia.

### OW-08 Cambio de distancia o coverage class
- **Hoy:** el default de distancia deja coverage class 0. Un CPE mas lejos que la distancia configurada falla los ACK y cae a MCS0. Fue la causa de la regresion de Panel2 (STAGE3107A); Panel3 y Panel2 quedaron persistidos (STAGE3108A, STAGE3107A).
- **Caso borde:** un CPE nuevo mas lejos que la distancia actual, o bajar la distancia de un panel.
- **Banco:** el banco no reproduce la distancia (unos 150 m). La prueba es una regla de monitoreo: fallas de TX por paquete altas mas distancia UISP del CPE mayor que la configurada del panel, con ventana A/A como en W447/W448.
- **Sin probar:** la regla en vivo.

### OW-09 Bridge UISP caido
- **Hoy:** el bridge traduce OpenWrt a UISP (W361-W418). Si cae, UISP muestra los equipos caidos o viejos y sus alertas pasan a ser falsos positivos. El trafico no pasa por el bridge, asi que no deberia cortarse (INFERRED).
- **Banco:** parar el servicio del bridge del LiteBeam de banco. Medir que ve UISP, cuanto tarda en volver y que el trafico no cambia.
- **Sin probar:** duracion y alertas de una caida real.

## 3. Panel de rescate en frio por sitio

**Idea:** un segundo radio por sitio, energizado pero con la radio apagada hasta que falla el primario. Al activarse emite el mismo SSID y clave en otro canal y los CPEs se mudan solos.

**Que necesitan los CPEs**
- **OpenWrt STA:** wpa_supplicant escanea los canales permitidos y se asocia al BSS del SSID con mejor señal. Con el mismo SSID y clave no hace falta una segunda red. No tiene que haber BSSID fijo: la lectura de 3136A filtro uci y no muestra `bssid`, asi que es UNKNOWN y se verifica en banco.
  - Si se quiere orden explicito: varios bloques `network` con `priority` en wpa_supplicant. En uci de OpenWrt, una sola wifi-iface STA no los expone; hace falta config propia o travelmate (no instalado).
  - Con WDS, el AP de rescate tambien necesita `wds=1` y, para CPEs airOS, el mismo parche ETH_P_TEB.
- **airOS stock:** la lista de escaneo de frecuencias del CPE debe incluir el canal de rescate y no tener "lock to AP MAC". Si hay lista acotada, agregar el canal es un cambio en cada CPE.

**Disparo solo con valores medidos**
- **Condicion:** el primario no responde Y ninguna de sus CPEs se ve, durante mas que la caida normal mas larga medida en telemetria. Hoy esas caidas son el reinicio de 10 equipos en 61 s, el retorno de LiteBeam en menos de 76-91 s y la caida por migracion.
- **El numero no se inventa:** se fija con la distribucion de caidas sin falla de telemetry.db, como A/A. Si falta ese historial, el disparo queda manual.
- **Lado del rescate:** el radio de rescate encendido pero callado mira al primario por cable y solo entonces hace `wifi up`.
- **PoE prohibido:** nunca se activa con PoE de .200/.201 ni de ether2-sw-poe200, que estan en la lista de no tocar.
- **Vuelta atras:** al volver el primario, apagar el rescate. Los CPEs vuelven por perdida de señal del rescate; la histeresis tambien se mide.

**Interferencia**
- Apagado no interfiere.
- Encendido necesita un canal que no pise a los otros paneles del sitio ni a PtP-Colo. Con antenas co-ubicadas hay desensibilizacion por canal adyacente: medir con airView o escaneo antes de elegir.
- Riesgo principal: que primario y rescate queden los dos encendidos si el primario sigue emitiendo beacons pero no pasa trafico (WEDGED). El disparo debe exigir que las CPEs no se vean, no solo que el AP no responda.

**Canales de 5/10 MHz (CONFIRMED estatico: no existen)**
- En `tools/research/srccache/ath10k-ct/ath10k-6.10/mac.c`, `chan_to_phymode` solo mapea 20_NOHT/20/40/80/160/80P80. Cualquier otro ancho da MODE_UNKNOWN con WARN.
- El driver no anuncia `WIPHY_FLAG_SUPPORTS_5_10_MHZ`. `REGDMN_MODE_11A_HALF/QUARTER_RATE` existen solo como enum en wmi.h.
- Igual en el ath10k mainline del repo. El rescate usa como minimo 20 MHz.

**Cobertura:** el rescate cubre el azimut de un panel; un radio por panel critico (Panel2, 22 CPE) antes que uno por sitio. Decidirlo es del operador.

## 4. Plan de banco (tarjetas sin ejecutar, gate del operador)

1. Rescate:
   - LAP .20 como primario y un segundo AP de banco como rescate en otro canal.
   - CPEs: Loco .117 (OpenWrt) y LBE .240 (airOS).
   - Apagar el primario desde el PoE del banco (A/A x3) y medir tiempo hasta reasociar y tiempo hasta trafico por tipo de CPE, mas la vuelta.
   - Con los bancos de W457 y W460 libres.
2. OW-05 sysupgrade con y sin kits.
3. OW-01 `simulate_fw_crash`.
4. OW-03 `dfs_simulate_radar`.
5. OW-04 corte de energia de un extremo PtP.
6. OW-07 reloj sin NTP y TLS del bridge.
7. OW-09 bridge caido.

Cada tarjeta lleva A/A antes de sacar conclusiones y no introduce umbrales nuevos.
