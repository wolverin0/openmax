<!-- doc-head: Wave 298 ES: por que ath10k en OpenWrt no sintoniza 6035 MHz, que habria que parchear y por que el canal 161 rinde mas (analisis estatico, 0 equipos tocados) -->
Hay tres techos distintos, no uno de 5895: la tabla compilada de ath10k_core en OpenWrt 24.10 llega a ch173/5865 MHz; regulatory.db para AR corta en 5835 y retoma en 5925-7125 a 12 dBm solo interior; el firmware QCA988x acepta 4910-6100.
El limite 4910-6100 esta en firmware-2.bin (2461A), no en ubnt_poll_host.ko; wmi.c pasa la frecuencia sin tocarla y no es punto de parche.
Parches minimos: tabla ath10k_5ghz_channels + ATH10K_NUM_CHANS + ATH10K_MAX_5G_CHAN (mac.c/core.h; correccion W301) y la regla AR de regulatory.db; regd.c no aporta reglas propias en el ath.ko compilado.
El +21 dB de SNR del canal 161 NO esta medido en ningun recibo; lo verificable es 18 dB de techo EIRP (30 vs 12 dBm) + 0.34 dB de FSPL. El enlace PtP-Colo ya opera en 6035 con airOS 8 (2521A).
<!-- /doc-head -->
# Wave 298 - Superchannel 6035 MHz en ath10k: analisis tecnico

Modo: 100% lectura de artefactos locales. Sin SSH, sin red, sin escrituras a radios. Detalle maquina en
`artifacts/autoresearch/wave298_ath10k_superchannel_analysis_20261028.json`.

Etiquetas: `CONFIRMED_STATIC_BINARY` (leido de un binario local), `CONFIRMED_SOURCE` (codigo fuente
local ath10k-ct), `INFERENCE` (deduccion de un binario sin fuente), `UNVERIFIED_PREMISE` (dicho en el
pedido y sin evidencia local).

## 1. Correcciones a las premisas del pedido

| Premisa del pedido | Lo que dicen los artefactos | Etiqueta |
| :-- | :-- | :-- |
| 5 GHz restringido a 5150-5895 MHz | Son tres techos: tabla compilada 5865 (ch173), regdb AR 5835 (y 5925-7125 interior), fuente ct 6.x 5885 (ch177) | CONFIRMED_STATIC_BINARY |
| PLL 4900-6100 en `ubnt_poll_host.ko` / `ath_hal` | 4910/6100 LE estan en `firmware-2.bin` (0x2ce4/0x2ce8, 2461A). `ubnt_poll_host.ko` tiene 4900 como u16 (4 BE / 4 LE, ambiguo) y **ningun** 6100; `ath_hal.ko` tiene 4900 x7 y 6100 x2 como u16 BE | CONFIRMED_STATIC_BINARY |
| Parchear `regd.c` | `ath.ko` (6.6.110) tiene el codigo de regd (cadenas `ath_regd_init`, `EEPROM regdomain`) pero 0 aciertos de los limites kHz de las reglas world en ambos endian: las reglas efectivas salen de `regulatory.db` via cfg80211 | INFERENCE |
| Parchear `db.txt` | Se analizo el `regulatory.db` compilado (RGDB formato 20, fecha desconocida), no `db.txt`; los valores de regla son equivalentes | CONFIRMED_STATIC_BINARY |
| Parchear `wmi.c` | No hace falta: `ath10k_wmi_put_wmi_channel` copia `arg->freq` sin limite; el recorte usa `low/high_5ghz_chan` que reporta el firmware (4910-6100) | CONFIRMED_SOURCE |
| Canal 161 rinde +21 dB SNR | Ningun recibo compara 5805 vs 6035 en el mismo enlace. El RSSI de 1669A es del par de banco, no de PtP-Colo | UNVERIFIED_PREMISE |

## 2. Cadena de restriccion en OpenWrt 24.10 (kernel 6.6.110)

1. **Tabla estatica del driver** (`ath10k_core.ko`, 2460A/2478A): 27 entradas 5 GHz de 5180 a 5865 MHz,
   registro de 64 bytes, techo ch173 en 0x62108. Si la frecuencia no esta en la tabla, cfg80211 no la
   conoce y no hay regdb que la habilite. **Este es el bloqueo principal.**
2. **Recorte por capacidad HAL del firmware** (`ath10k-6.10/mac.c:4274-4285`): canales fuera de
   `low_5ghz_chan..high_5ghz_chan` se marcan `IEEE80211_CHAN_DISABLED`. Los valores llegan del evento
   service-ready (`wmi.c:5889-5890`, `5930-5931`, asignados en `wmi.c:5993`). El firmware declara
   4910-6100, asi que 6035 pasa este filtro sin cambios.
3. **Base regulatoria** (`regulatory.db`, cfg80211). Para `AR` (dfs_region 1):

| Rango MHz | Ancho max | EIRP max | Flags |
| :-- | :-- | :-- | :-- |
| 5170-5250 | 80 | 17 dBm | AUTO_BW |
| 5250-5330 | 80 | 24 dBm | DFS + AUTO_BW |
| 5490-5730 | 160 | 24 dBm | DFS |
| 5735-5835 | 80 | 30 dBm | - |
| 5925-7125 | 320 | 12 dBm | NO_OUTDOOR |

   No hay regla entre 5835 y 5925. 6035 cae en 5925-7125: permitido solo en interior a 12 dBm.
4. **`regd.c` (`ath.ko`)**: con la EEPROM en dominio world, ath aplicaria sus reglas propias; en el
   modulo compilado no aparecen esas constantes (0/22 sondas), asi que la base efectiva es regdb (INFERENCE).
5. **WMI** (`ath10k-6.10/wmi.c:1797`): `ch->mhz = arg->freq`; sin tabla ni clamp. No es punto de parche.
   Correccion Wave 301: el RX de management (`wmi.c:2757`) descarta canales > `ATH10K_MAX_5G_CHAN` (173, en `core.h`); hay que subir esa constante.

## 3. Parches que requeriria un build custom (solo puntos, sin diff nuevo)

| Archivo | Cambio necesario | Estado en el repo |
| :-- | :-- | :-- |
| `ath10k/mac.c` | Agregar entrada `CHAN5G(207, 6035, 0)` (y 203/6015 para VHT40) a `ath10k_5ghz_channels[]` | Ya preparado en binario: 2478A/2490A reemplazan 169/173 por 203/207 (12 bytes, sin mover relocs) |
| `ath10k/core.h` | Subir `ATH10K_NUM_CHANS` (41 en el modulo compilado; 42 en ct 6.x) o falla el `BUILD_BUG_ON` de `mac.c:11243` | Solo aplica en build desde fuente; la via binaria de 2478A evita el cambio reemplazando entradas |
| `regulatory.db` / `db.txt` | Regla AR 5925-7125 que permita uso exterior y EIRP del enlace | 2490A ya lo hizo: 12 -> 30 dBm y borro NO_OUTDOOR (sha 12ef0edf...) |
| `ath/regd.c` | Ninguno si la EEPROM no es world o si el build trae reglas world desactivadas (caso observado) | - |
| `ath10k/wmi.c` | Ninguno: el firmware ya acepta 4910-6100 | - |

**Bandera de cumplimiento:** la base de 2490A sube AR 5925-7125 en 18 dB sobre lo que dice
wireless-regdb y quita NO_OUTDOOR. Para un PtP exterior eso excede la regla AR tal como la codifica
regdb. Esta wave no genera ningun parche nuevo; el estado legal ante ENACOM no se verifico.

Hueco abierto heredado (2504A): hw 207 dentro de la banda 5 GHz vs la numeracion 6 GHz de cfg80211
no esta probado; netifd con `option freq 6035` evita depender del numero de canal (2539A).

## 4. Por que el canal 161 (5805 MHz) rinde mejor

- **Techo EIRP regulatorio:** 30 dBm (5735-5835) vs 12 dBm interior (5925-7125) = **18 dB** a favor
  de ch161 cumpliendo la regla AR.
- **Perdida de espacio libre:** 20*log10(6035/5805) = **0.34 dB** extra en 6035; despreciable.
- **Total explicable con evidencia:** ~18.3 dB. El +21 dB del pedido no se reproduce; los ~2.7 dB
  restantes podrian venir de caida de ganancia de antena, filtro o PA por encima de 5.85 GHz, pero
  nada de eso esta medido (UNVERIFIED_PREMISE).
- **Sin parche:** ch161 corre con la tabla, regdb y firmware de serie; 6035 en OpenWrt exige modulo
  y base modificados y queda fuera de la regla AR exterior.

## 5. Estado real del enlace

PtP-Colo (.62 AP / .54 STA) ya transmite en 6035 MHz con airOS 8 WA.v8.7.25 (2521A): `umac.ko`
trae 6035 de serie, por eso nunca necesito parche. El pedido no identifica que enlace esta hoy en
ch161; no se inventa uno.

## 6. Evidencia leida

2460A, 2461A, 2478A, 2479A, 2490A, 2504A, 2508A, 2521A, 2539A, 1669A; fuente `tools/research/srccache/ath10k-ct/`;
binarios `ath.ko` (2520A), `ubnt_poll_host.ko` y `ath_hal.ko` (WA 8.7.25), dos `regulatory.db`. Hashes en el JSON.
