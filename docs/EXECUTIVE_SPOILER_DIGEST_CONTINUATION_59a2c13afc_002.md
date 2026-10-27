<!-- doc-head: EXECUTIVE_SPOILER_DIGEST.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](EXECUTIVE_SPOILER_DIGEST.md) | Part 2/2
<a id="-futuramax--centro-de-comando-ejecutivo-snippets--spoilers"></a> [📡 FuturaMAX — Centro de Comando Ejecutivo (Snippets + Spoilers)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-futuramax--centro-de-comando-ejecutivo-snippets--spoilers) | <a id="-0-resumen-directo-logramos--falló--próximas-pruebas"></a> [⚡ 0. Resumen Directo: Logramos · Falló · Próximas Pruebas](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-0-resumen-directo-logramos--falló--próximas-pruebas) | <a id="-lo-que-logramos-actualizado-hasta-stage-31a--champion-v8-en-5-ghz--stage-27-en-24-ghz--s24f-r1-en-ltu-lite-v240--agente-netjsonopenwisp"></a> [✅ Lo que logramos (Actualizado hasta Stage 31A — `Champion v8` en 5 GHz + `Stage 27` en 2.4 GHz + `S24F-R1` en `LTU-Lite v2.4.0` + `Agente NetJSON/OpenWISP`)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-lo-que-logramos-actualizado-hasta-stage-31a--champion-v8-en-5-ghz--stage-27-en-24-ghz--s24f-r1-en-ltu-lite-v240--agente-netjsonopenwisp) | <a id="-lo-que-falló-o-descartamos-y-qué-aprendimos-con-evidencia-física"></a> [❌ Lo que falló o descartamos (y qué aprendimos con evidencia física)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-lo-que-falló-o-descartamos-y-qué-aprendimos-con-evidencia-física) | <a id="-estado-actual-en-ram-y-servidor-en-vivo-del-command-center"></a> [⏭️ Estado Actual en RAM y Servidor en Vivo del Command Center](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-estado-actual-en-ram-y-servidor-en-vivo-del-command-center) | <a id="-1-semáforo-ejecutivo-en-30-segundos-todo-el-contexto-actual"></a> [🚦 1. Semáforo Ejecutivo en 30 Segundos (Todo el Contexto Actual)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-1-semáforo-ejecutivo-en-30-segundos-todo-el-contexto-actual) | <a id="-2-reportes-por-tarjetas-leé-el-snippet-o-abrí-el-spoiler"></a> [📋 2. Reportes por Tarjetas (Leé el Snippet o Abrí el Spoiler)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-2-reportes-por-tarjetas-leé-el-snippet-o-abrí-el-spoiler) | <a id="-tarjeta-1--solución-al-uplink-hammering-y-nodos-ocultos-en-ptmp-modo-a-vs-modo-b-tdma"></a> [📌 Tarjeta 1 — Solución al "Uplink Hammering" y Nodos Ocultos en PtMP (`Modo A` vs `Modo B TDMA`)](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-tarjeta-1--solución-al-uplink-hammering-y-nodos-ocultos-en-ptmp-modo-a-vs-modo-b-tdma) | <a id="-tarjeta-2--auditoría-72h-de-torre-guarida-y-aislamiento-del-troncal-almafuerte--edificio"></a> [📌 Tarjeta 2 — Auditoría 72h de Torre Guarida y Aislamiento del Troncal `Almafuerte ↔ Edificio`](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-tarjeta-2--auditoría-72h-de-torre-guarida-y-aislamiento-del-troncal-almafuerte--edificio) | <a id="-tarjeta-3--superficie-física-completa-en-banco-r1r122-100-m-a-14-km--autopiloto-procd"></a> [📌 Tarjeta 3 — Superficie Física Completa en Banco (`R1..R122`, `100 m` a `14 km`) + Autopiloto `procd`](EXECUTIVE_SPOILER_DIGEST_CONTINUATION_59a2c13afc_001.md#-tarjeta-3--superficie-física-completa-en-banco-r1r122-100-m-a-14-km--autopiloto-procd)

<!-- stage822a-payload-begin -->

---

### 📌 Tarjeta 4 — Ingeniería Inversa de `ubnt_poll_host.ko`, `Rocket Prism AirPrism` y `LTU 4096-QAM (12x)`
- **🎯 Qué probamos**: Cómo afinar en caliente el scheduler TDMA de `airOS 8` (`ubnt_poll_host.ko`) en paneles densos (`Panel2-Guarida`) y por qué `LTU` bloquea `4096-QAM (12x)`.
- **⚡ Resultado clave**: En `ubnt_poll_host.ko`, `cms_bias=0` (default) deja que clientes a `-70/-74 dBm` (`FRANCO_Debora`, `Marilina SEVERO`) quemen el `100%` de reintentos; pasar a **`cms_bias=6, voip_bias=6, daprot=2, sta_priority=0`** reduce un **`-38.8%` el impuesto de aire TDMA**. En **`LTU` (`ame_core.ko`)**, `4096-QAM` (`12x`, `MCS 31`) está deshabilitado por tabla (`table_ptpPwrRange = (0,0)`) en `60, 80 y 100 MHz` y sólo opera en **`10..50 MHz`**, `2x2 MIMO`, con backoff lineal a **`16 dBm`** (`LTU-Rocket`) / **`10–12 dBm`** (`CPE`) y **`97%` de codewords LDPC limpios en `10x`**.
- **🛠️ Decisión práctica**: Implementado el optimizador [`controller/ltu_12x_and_uph_runtime_optimizer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/ltu_12x_and_uph_runtime_optimizer.py) (`25/25 pytest PASS`).

<details>
<summary><b>🔽 Spoiler: Abrir las 6 compuertas de LTU 4096-QAM (12x) y los comandos sysctl de Panel2-Guarida</b></summary>

1. **Comandos Modo B (`ubnt_poll_host.ko`) para `Panel2-Guarida` (`22 CPEs`, `ADVISORY_ONLY`)**:
   ```sh
   echo 6 > /proc/sys/dev/uph_wifi0/cms_bias
   echo 6 > /proc/sys/dev/uph_wifi0/voip_bias
   echo 2 > /proc/sys/dev/uph_wifi0/daprot
   echo "1 -52 4 22" > /proc/sys/dev/uph_wifi0/atpc
   ```
2. **Las 6 Compuertas Obligatorias en `ame_core.ko` para que un enlace LTU levante `4096-QAM` (`12x`, `MCS 31`)**:
   - **Compuerta 1 (Silicio)**: ASIC `LTU` (`amesoc3` `0xea10`/`0xea12`).
   - **Compuerta 2 (Ancho de Canal)**: **`10, 20, 30, 40 o 50 MHz`** (en `60, 80 y 100 MHz` la tabla `.data+0x1f8` `table_ptpPwrRange` tiene `(0, 0)` y bloquea `12x` por hardware).
   - **Compuerta 3 (`2x2 MIMO`)**: Desbalance entre cadenas $\le 2.5\text{ dB}$ (`autoMcsAllSisoTbl` limita SISO a `MCS 23` = `1024-QAM 10x`).
   - **Compuerta 4 (Backoff de Potencia TX)**: $\le 16.0\text{ dBm}$ en `LTU-Rocket`/`AF-5XHD` y $\le 10.0\text{–}12.0\text{ dBm}$ en `LTU-Lite`/`Pro`/`LR` (`mcs_txpwr_freq_ptp`).
   - **Compuerta 5 (Sensibilidad & CINR)**: $\text{RSSI} \ge -57\text{ dBm}$ (en `50 MHz`) a $-66\text{ dBm}$ (en `10 MHz`) y $\text{CINR} \ge 32\text{–}34\text{ dB}$.
   - **Compuerta 6 (Histéresis LDPC)**: `startThrd_4096 = 97%` de bloques LDPC sin error en `10x` para promover, `stayThrd_4096 = 90%` para sostener.

- **Archivos completos**: [`STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md), [`STAGE12_LTU_12X_AND_UPH_RUNTIME_CONTROLLER.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE12_LTU_12X_AND_UPH_RUNTIME_CONTROLLER.md).

</details>
<!-- stage822a-payload-end -->
