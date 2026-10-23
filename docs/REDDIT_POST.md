# Reddit Post Update (`r/wisp` / `r/Ubiquiti`) — Zero-Table Format (Clean Copy-Paste for Mobile & Desktop)

> **Why this format**: Reddit's composer and mobile app often mangle Markdown tables (`| col | col |`). This version uses **clean bullet cards + native code/quote blocks + optional `>! Spoiler !<` tags** so it renders cleanly on both desktop and mobile when pasted into Reddit's **Markdown Editor**.

---

## 🇬🇧 English Copy-Paste Block (for `r/wisp` / `r/Ubiquiti`)

```markdown
**Title:** openMAX Update: Live production sector results on Ubiquiti airMAX AC (~10x lower wireless ping, -80% to -94% bufferbloat, 0-touch stock airOS 8 interop & multi-vendor PtMP)

Hey r/wisp,

Quick, no-fluff update on **openMAX** (https://github.com/wolverin0/openmax) — our open-source project squeezing maximum real-world performance out of existing Ubiquiti `airMAX AC` hardware (`LiteAP 120`, `Rocket Prism 5AC Gen2`, `LiteBeam 5AC Gen2`, `NanoStation 5AC Loco`).

All the deep kernel docs, scripts, and benchmark JSONs are in the repo. Here is what we have working on real hardware and in live production:

* **Switch tower APs to OpenWrt while stock `airOS 8` CPEs keep connecting out of the box:** We migrated our live sector AP (`LiteAP 120`) to OpenWrt 24.10.4 (`Linux 6.6.110`) and customer CPEs running **100% unmodified stock `airOS 8.7.25`** connected automatically. Even if a customer's radio is powered off during cutover and turned back on days later, it associates with zero touch.
* **Run multi-vendor & mixed-generation clients on the same Ubiquiti AP:** We simultaneously connect **Ubiquiti 5AC (`LiteBeam Gen2`, `Loco 5AC`, `Rocket Prism`)**, legacy **Ubiquiti M5 (`airOS 6`)**, and **MikroTik (`SXT Lite5`)** CPEs on the same sector without a single weak/obstructed client dragging everyone else down.
* **Full channel-width flexibility (`20, 40, 80 MHz`, plus `5/10 MHz` between OpenWrt radios):** On a `20 MHz` channel, our airtime scheduler hits **`0.95` Jain fairness** and nearly **`4 bit/s/Hz`** spectral efficiency.
* **Full OpenWrt AP + OpenWrt CPE in live production:** Once the AP is running OpenWrt, we remotely upgrade CPEs over the air in ~4 minutes while preserving their management IP, WebUI, hardware-accelerated NAT (`flow_offloading=1`), and the exact DHCP lease of the customer's indoor Wi-Fi router.
* **Uncovered inside `Rocket Prism` & `LTU` (`v2.4.2`) firmware:** We mapped the hardware control table for **AirPrism** active RF filtering on `Rocket Prism 5AC Gen2`, and confirmed that LTU's greyed-out **`4096-QAM` (`12X`)** and **`OFDMA`** modes have real driver and rate-table routines compiled inside `v2.4.2` (being tested on our physical bench right now).

---

### 📊 Live Production Numbers (Same tower, same rooftop radios, `20 MHz` channel — Before vs. After)

* **Unloaded Wireless Sector Ping (`p50`):**
  * Stock `airOS 8.7.25`: `22.58 ms`
  * **openMAX (OpenWrt 24.10.4):** **`1.93 ms – 2.42 ms`** -> **~10x faster (-90% base latency)**
* **Wireless Ping Jitter / Spikes (`p95`):**
  * Stock `airOS 8.7.25`: `98.77 ms`
  * **openMAX (OpenWrt 24.10.4):** **`4.47 ms – 14.90 ms`** -> **6.6x to 22x more stable (-85% to -95% jitter)**
* **Ping Under Heavy Download (Bufferbloat DL):**
  * Stock `airOS 8.7.25`: `31.49 ms` (`p50`) / `54.40 ms` (`p95`)
  * **openMAX (OpenWrt 24.10.4):** **`8.43 ms – 9.86 ms` (`p50`)** -> **3.5x to 5x lower lag (-73% to -80%)**
* **Ping Under Heavy Upload (Bufferbloat UL):**
  * Stock `airOS 8.7.25`: `195 ms – 224 ms` *(caused by airOS tshaper's 127-packet SFQ queue)*
  * **openMAX (OpenWrt 24.10.4):** **`10.37 ms – 16.64 ms` (`p50`)** -> **12x to 18x lower lag (-91% to -94%)**
* **Usable `20 MHz` Sector Capacity (Real TCP Goodput):**
  * Stock `airOS 8.7.25`: `~35 – 45 Mbps` typical
  * **openMAX (OpenWrt 24.10.4):** **`69.80 Mbps` DL / `30.74 Mbps` UL** -> **1.5x to 1.8x more capacity (+50% to +80% more Mbps/MHz)**
* **CPE CPU Headroom (Routing + NAT):**
  * Stock `airOS 8.7.25`: Kernel `2.6.32` (software NAT)
  * **openMAX (OpenWrt 24.10.4):** Kernel `6.6.110` (`flow_offloading=1`) -> **~2.5x more CPU headroom (+150% packet/s capacity)**

> **Bottom line:** On the exact same rooftop hardware and `20 MHz` channel, wireless ping is **~10x faster (`~2 ms` vs `~22 ms`)**, lag under saturation drops by **80%–94%**, and usable sector capacity increases by **+50% to +80%**.

---

### 🔌 Next up: Native UISP Reporting (`udapi-bridge`) on OpenWrt

Moving a radio to pure OpenWrt stops Ubiquiti's `/bin/udapi-bridge` agent, so UISP marks it offline.
>!We unpacked `/bin/udapi-bridge` from `WA.v8.7.25`: it does not depend on the old kernel or TDMA module; it is a userspace WebSocket (`EVP_aes_256_gcm`) client that reads `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi`, and `/bin/wstalist`. We are packaging a lightweight OpenWrt wrapper so migrated radios stay Online and green inside UISP with their original device ID and live telemetry.!<

Full documentation, scripts, and benchmark receipts:
👉 https://github.com/wolverin0/openmax
```

---

## 🇦🇷 Bloque Listo para Copiar y Pegar en Español (Sin tablas que se rompan)

```markdown
**Título:** Actualización openMAX: Qué logramos en producción real sobre equipos Ubiquiti airMAX AC (~10x menos ping en el aire, -80% a -94% de lag bajo carga, multimarca y migración sin tocar al cliente)

Hola a todos,

Les comparto un resumen corto y al grano de lo que ya tenemos funcionando en producción real en nuestro WISP con **openMAX** (https://github.com/wolverin0/openmax). Toda la evidencia cruda y los scripts están en el repo; acá va lo concreto que logramos en la cancha:

* **Cambiar los AP a OpenWrt y que los CPEs con `airOS 8` original sigan conectando solos:** Podés migrar un panel (`LiteAP 120` / `Rocket`) a OpenWrt 24.10.4 y los clientes que tienen **su firmware original `airOS 8.7.25` de fábrica** se conectan solos sin tocarles nada. Si un cliente estaba apagado el día del cambio y enchufa la antena una semana después, conecta derecho.
* **Hacer funcionar equipos de todas las marcas y generaciones contra el mismo AP Ubiquiti:** En un mismo panel conectamos en simultáneo equipos **Ubiquiti 5AC (`LiteBeam Gen2`, `Loco 5AC`, `Rocket Prism`)**, equipos viejos **Ubiquiti M5 (`airOS 6`)** y equipos **MikroTik (`SXT Lite5`)**, sin que un cliente con mala señal o tapado por árboles tire abajo al resto del sector.
* **Conectar en distintos anchos de canal (`20, 40, 80 MHz`, y hasta `5/10 MHz` entre equipos OpenWrt):** En canales de `20 MHz` logramos repartir el aire de forma pareja (`0.95` de equidad Jain) sacándole casi **`4 Mbps por cada MHz` de espectro**.
* **Migrar el sector completo (AP + CPEs) a OpenWrt en vivo sin cortar al cliente:** Una vez migrado el AP, actualizamos los CPEs por aire en ~4 minutos manteniendo su IP, su interfaz web, su NAT acelerado y la misma IP del router Wi-Fi adentro de la casa del cliente.
* **Destapar lo que traen oculto los firmwares de `Rocket Prism` y `LTU` (`v2.4.2`):** Mapeamos cómo manejar el filtro activo **AirPrism** en los `Rocket Prism 5AC Gen2`, y confirmamos que la modulación **`4096-QAM` (`12X`)** y el **`OFDMA`** que Ubiquiti dejó deshabilitados en `LTU` tienen las tablas y funciones reales adentro del firmware (probándose ahora mismo en el banco).

---

### 📊 Los números reales en producción (Mismo panel, mismas antenas en el techo, canal de `20 MHz` — Antes vs. Ahora)

* **Ping base en el aire (`p50`):**
  * Antes (`airOS 8.7.25`): `22.58 ms`
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`1.93 ms – 2.42 ms`** -> **~10x más rápido (-90% de latencia base)**
* **Estabilidad / Picos de ping (`p95`):**
  * Antes (`airOS 8.7.25`): `98.77 ms`
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`4.47 ms – 14.90 ms`** -> **6.6x a 22x más estable (-85% a -95% de jitter)**
* **Ping descargando a tope (Bufferbloat DL):**
  * Antes (`airOS 8.7.25`): `31.49 ms` (`p50`) / `54.40 ms` (`p95`)
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`8.43 ms – 9.86 ms` (`p50`)** -> **3.5x a 5x menos lag (-73% a -80% en hora pico)**
* **Ping subiendo a tope (Bufferbloat UL):**
  * Antes (`airOS 8.7.25`): `195 ms – 224 ms` *(por la cola SFQ de 127 paquetes de airOS)*
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`10.37 ms – 16.64 ms` (`p50`)** -> **12x a 18x menos lag (-91% a -94% al subir)**
* **Capacidad útil en `20 MHz` (TCP real):**
  * Antes (`airOS 8.7.25`): `~35 – 45 Mbps` típicos
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** **`69.80 Mbps` DL / `30.74 Mbps` UL** -> **1.5x a 1.8x más capacidad (+50% a +80% más megas útiles)**
* **Margen de CPU del CPE ruteando + NAT:**
  * Antes (`airOS 8.7.25`): Kernel `2.6.32` (NAT clásico)
  * **Ahora (`openMAX / OpenWrt 24.10.4`):** Kernel `6.6.110` (`flow_offloading=1`) -> **~2.5x más margen de CPU (+150% paquetes/s)**

> **En resumen:** Con exactamente los mismos equipos en el techo y el mismo canal de `20 MHz`, el enlace responde **~10 veces más rápido (`~2 ms` en vez de `~22 ms`)**, el lag cuando el cliente satura la línea baja entre un **80% y un 94%**, y al panel se le saca entre **+50% y +80% más capacidad útil**.

---

### 🔌 Próximo paso en marcha: Puente nativo a UISP en OpenWrt

Al pasar un equipo a OpenWrt puro, deja de correr el agente de Ubiquiti (`udapi-bridge`) y UISP lo deja de ver.
>!Ya desarmamos `/bin/udapi-bridge` de `WA.v8.7.25`: es un cliente WebSocket (`AES-256-GCM`) de espacio de usuario que lee `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi` y `/bin/wstalist`. Estamos armando el wrapper liviano para que los equipos con OpenWrt sigan reportando Online y en verde adentro de UISP con su mismo ID, señal, tráfico y clientes.!<

Todo el código, las pruebas y la documentación están abiertos acá:
👉 https://github.com/wolverin0/openmax
```
