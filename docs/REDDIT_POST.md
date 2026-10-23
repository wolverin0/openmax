# Reddit Post Update (`r/wisp` / `r/Ubiquiti`) — Concise, Zero-Fluff Production Update

> **How to use**: Copy either the **English** version (for `r/wisp` / `r/Ubiquiti`) or the **Spanish** version below and paste directly into Reddit's Markdown Editor.

---

## 🇬🇧 English Version (for `r/wisp` / `r/Ubiquiti`)

**Title:** `OpenMAX Update: Live production sector results on Ubiquiti airMAX AC hardware (~10x lower wireless ping, -80% bufferbloat, 0-touch stock airOS 8 interop & multi-vendor PtMP)`

Hey `r/wisp`,

Quick update on **openMAX** ([github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)) — our open-source R&D project squeezing the physical limits out of existing Ubiquiti `airMAX AC` hardware (`LiteAP 120`, `Rocket Prism 5AC Gen2`, `LiteBeam 5AC Gen2`, `NanoStation 5AC Loco`).

No walls of assembly or kernel theory here (all the raw code, packet captures, and independent audits are in the repo). Here is what we have proven so far — first on the bench, and now on a **live outdoor production WISP sector**:

### What works today (Proven on real hardware)

* **Stock `airOS 8` CPEs connect to an OpenWrt AP with zero customer reflashing:** You can upgrade a tower AP (`LiteAP` / `Rocket`) to OpenWrt 24.10.4 (`Linux 6.6.110`) and existing customer CPEs running **100% unmodified stock `airOS 8` (`v8.7.25`)** associate and pass traffic automatically (`WDS 4-addr`). No climbing roofs on cutover day, and if a powered-off customer turns their radio back on weeks later, it still connects out of the box.
* **True multi-vendor & mixed-generation sectors:** On the same Ubiquiti AC Access Point, we simultaneously connect **Ubiquiti 5AC (`WA`/`XC`)**, **legacy Ubiquiti M5 (`airOS 6` `802.11n`)**, and **MikroTik (`SXT Lite5` / `RouterOS` / `OpenWrt`)** clients without a single weak or obstructed station dragging down the rest of the sector.
* **Full channel-width agility (`20 / 40 / 80 MHz`, plus `5 / 10 MHz` on OpenWrt links):** Narrowing a noisy mixed sector to `20 MHz` with our airtime scheduler (`AQL` + `ATF` + `DiffServ VO` + `CoTSQ`) hit **`0.95` Jain fairness** and **`3.34–3.94 bit/s/Hz`** spectral efficiency.
* **Full OpenWrt AP + OpenWrt CPE (`STA-WDS` + `NAT Flow Offload` + `AQL`) in live production:** Once the AP is migrated, you can remotely upgrade individual CPEs over the air (`~4 minutes`, preserving the customer's LAN DHCP leases, router IP, and WebUI) to unlock the full Linux 6.6 queue and airtime stack on both ends.
* **Inside `Rocket Prism` & `LTU` (`v2.4.2`) firmware:** Our static binary audit mapped the hardware GPIO/SPI filter tables for **AirPrism** on `XC` boards, and proved that LTU's long-promised **`4096-QAM` (`12X`)** and subband **`OFDMA`** actually have real rate-table and driver routines compiled inside `v2.4.2` (next up on our physical RF bench).

---

### The Numbers: Stock `airOS 8.7.25` vs. `openMAX (OpenWrt 24.10.4)` on the Same Live `20 MHz` Production Sector

Measured today on the exact same physical radios (`LiteAP 120` AP + `NanoStation 5AC Loco` & `LiteBeam 5AC Gen2` CPEs) on a `20 MHz` channel (`5240 MHz`) before and after migration:

| Real-World Metric (`20 MHz` Channel) | Stock `airOS 8.7.25` (Before) | **openMAX / OpenWrt 24.10.4** (Now) | Multiplier (`x`) | Improvement (`%`) |
| :--- | :---: | :---: | :---: | :---: |
| **Unloaded Wireless Sector Ping (`p50`)** | `22.58 ms` | **`1.93 ms – 2.42 ms`** | **~10x faster** | **-90% base latency** |
| **Wireless Ping Jitter / Spikes (`p95`)** | `98.77 ms` | **`4.47 ms – 14.90 ms`** | **6.6x – 22x more stable** | **-85% to -95% jitter** |
| **Ping Under Heavy Download (Bufferbloat)** | `31.49 ms` (`p50`) / `54.40 ms` (`p95`) | **`8.43 ms – 9.86 ms` (`p50`)** | **3.5x – 5x lower lag** | **-73% to -80% loaded ping** |
| **Ping Under Heavy Upload (Bufferbloat)** | `195 ms – 224 ms` *(127-pkt SFQ queue)* | **`10.37 ms – 16.64 ms` (`p50`)** | **12x – 18x lower lag** | **-91% to -94% upload lag** |
| **Usable `20 MHz` Sector Capacity (TCP)** | `~35 – 45 Mbps` typical | **`69.80 Mbps` DL / `30.74 Mbps` UL** | **1.5x – 1.8x more capacity** | **+50% to +80% more Mbps/MHz** |
| **CPE CPU Load While Routing + NAT** | Kernel `2.6.32` (software NAT) | Kernel `6.6.110` (`nft flow_offloading=1`) | **~2.5x more CPU headroom** | **+150% packet/s headroom** |

> **Bottom line:** With the exact same radios bolted to the roof and the same `20 MHz` channel, wireless response time is **~10x faster (`~22 ms` down to `~2 ms`)**, lag under heavy traffic drops by **80%–94%**, and usable sector capacity jumps **+50% to +80%**.

---

### What we are building right now: Native UISP (`udapi-bridge`) Reporting on OpenWrt

One thing we noticed right after migrating the live CPEs to OpenWrt is that you lose native **UISP** reporting (since Ubiquiti's `/bin/udapi-bridge` daemon isn't running on vanilla OpenWrt).
* We already unpacked `/bin/udapi-bridge` from `WA.v8.7.25`: it is a pure userspace WebSocket (`EVP_aes_256_gcm`) binary that reads `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi`, and `/bin/wstalist`.
* We are currently packaging a lightweight OpenWrt `udapi-bridge` compatibility layer so OpenWrt-powered `airMAX AC` radios keep showing up **Online and green inside UISP** with their original device ID, signal, throughput, and station list.

All scripts, images, benchmark JSON receipts, and technical docs are 100% open source in the repo:
👉 **[https://github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)**
* **Live Production Sector & UISP Bridge Doc:** [docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md)
* **Zero-Touch Stock `airOS 8` Interop:** [docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md)
* **Multi-Vendor PtMP (`AC + M5 + MikroTik`):** [docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md)

Happy to answer any questions or share configs with other WISPs!

---

## 🇦🇷 Versión en Español (Lista para compartir o postear)

**Título:** `Actualización OpenMAX: Resultados reales en producción sobre equipos Ubiquiti airMAX AC (~10x menos ping en el aire, -80% a -94% de bufferbloat, compatibilidad multimarca y migración sin tocar el firmware del cliente)`

Hola a todos,

Les comparto un resumen corto y directo (sin humo ni paredes de código ensamblador, que para eso está toda la documentación técnica en [github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)) de lo que ya logramos probar y poner en producción real en nuestro WISP con el proyecto **openMAX / FuturaMAX**:

### Lo que ya logramos y está funcionando en hardware real:

* **Cambiar el AP del nodo a OpenWrt y que los CPEs con `airOS 8` original sigan conectando solos:** Podés pasar un panel (`LiteAP 120` / `Rocket`) a OpenWrt 24.10.4 y los clientes que tienen **el firmware original `airOS 8.7.25` de fábrica** se conectan solos sin tocarles nada. Si un cliente estaba desenchufado el día del cambio y prende la antena una semana después, se asocia automáticamente.
* **Hacer funcionar equipos de todas las marcas y generaciones contra el mismo AP Ubiquiti:** En un mismo panel conectamos al mismo tiempo equipos **Ubiquiti 5AC (`LiteBeam Gen2`, `Loco 5AC`, `Rocket Prism`)**, equipos viejos **Ubiquiti M5 (`airOS 6` `802.11n`)** y equipos **MikroTik (`SXT Lite5`)**, evitando que un cliente con mala señal o tapado por árboles arrastre al resto del panel.
* **Conectar en cualquier ancho de canal (`20, 40, 80 MHz`, y hasta `5/10 MHz` entre equipos OpenWrt):** En canales de `20 MHz` logramos un índice de equidad (Jain fairness) de **`0.95`** y casi **`4 bit/s/Hz`** de eficiencia espectral.
* **Migrar el sector completo (AP + CPEs) a OpenWrt 24.10.4 en vivo sin cortar al cliente:** Migramos remotamente por aire los CPEs (`NanoStation 5AC Loco` y `LiteBeam 5AC Gen2`) en ~4 minutos manteniendo su IP de gestión, su interfaz web (LuCI HTTP/HTTPS), su NAT con aceleración por flujo (`flow_offloading=1`) y el mismo lease DHCP del router Wi-Fi adentro de la casa del cliente.
* **Destapar lo que tienen adentro los firmwares de `Rocket Prism` y `LTU` (`v2.4.2`):** Mapeamos cómo se controla por hardware el filtro activo **AirPrism** en los `Rocket Prism 5AC Gen2`, y confirmamos que la famosa modulación **`4096-QAM` (`12X`)** y el **`OFDMA`** que Ubiquiti dejó grises en `LTU` sí tienen las tablas y funciones compiladas adentro del driver (lo próximo a medir en el banco).

---

### Los Números en Producción (Mismo panel, mismos equipos en el techo, canal de `20 MHz`, Antes vs. Ahora):

| Métrica Real en el Sector (`20 MHz`) | Con Stock `airOS 8.7.25` (Antes) | Con **openMAX / OpenWrt 24.10.4** (Ahora) | Multiplicador (`x`) | Mejora (`%`) |
| :--- | :---: | :---: | :---: | :---: |
| **Ping base en el aire (`p50`)** | `22.58 ms` | **`1.93 ms – 2.42 ms`** | **~10x más rápido** | **-90% de latencia base** |
| **Estabilidad / Picos de Jitter (`p95`)** | `98.77 ms` | **`4.47 ms – 14.90 ms`** | **6.6x a 22x más estable** | **-85% a -95% de jitter** |
| **Ping descargando a tope (Bufferbloat DL)** | `31.49 ms` (`p50`) / `54.40 ms` (`p95`) | **`8.43 ms – 9.86 ms` (`p50`)** | **3.5x a 5x menos lag** | **-73% a -80% de latencia en pico** |
| **Ping subiendo a tope (Bufferbloat UL)** | `195 ms – 224 ms` *(cola SFQ de 127 paq.)* | **`10.37 ms – 16.64 ms` (`p50`)** | **12x a 18x menos lag** | **-91% a -94% de lag al subir** |
| **Capacidad útil en `20 MHz` (TCP real)** | `~35 – 45 Mbps` típicos | **`69.80 Mbps` DL / `30.74 Mbps` UL** | **1.5x a 1.8x más capacidad** | **+50% a +80% más Mbps por MHz** |
| **Margen de CPU del CPE ruteando + NAT** | Kernel `2.6.32` (NAT clásico) | Kernel `6.6.110` (`nft flow_offloading=1`) | **~2.5x más margen de CPU** | **+150% margen de paquetes/s** |

> **En resumen:** Con exactamente las mismas antenas en el techo y el mismo canal de `20 MHz`, el enlace responde **~10 veces más rápido (`~2 ms` en vez de `~22 ms`)**, el lag cuando el cliente satura la conexión baja entre un **80% y un 94%**, y al panel se le saca entre **+50% y +80% más megas útiles**.

---

### Próximo paso en el que ya estamos trabajando: Que los equipos en OpenWrt sigan reportando nativamente a UISP

Algo clave para cualquier WISP: cuando pasás un equipo a OpenWrt puro, deja de correr `/bin/udapi-bridge` y UISP lo deja de ver.
* Ya desarmamos `/bin/udapi-bridge` de `WA.v8.7.25`: no depende del kernel viejo ni de TDMA; es un binario de usuario que habla por WebSocket encriptado (`AES-256-GCM`) leyendo `/etc/board.info`, `/tmp/system.cfg` (`unms.uri`), `/usr/www/status.cgi` y `/bin/wstalist`.
* Estamos armando el puente liviano para OpenWrt (`docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md`) para que los equipos migrados a OpenWrt sigan apareciendo **Online y en verde adentro de UISP** con su mismo ID, señal, tráfico y lista de clientes.

Toda la documentación detallada, scripts y pruebas están abiertos en el repo:
👉 **[https://github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)**
