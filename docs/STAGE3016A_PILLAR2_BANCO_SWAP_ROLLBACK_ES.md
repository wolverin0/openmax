<!-- doc-head: Wave356 P4 — swap RAM-only del modulo PPDU-end en el banco, rollback automatico y causa exacta del no-carga -->

# STAGE3016A — Pillar 2 en banco: swap ejecutado, rollback limpio y por que el modulo no carga

Operacion real sobre el banco `.20` (LAP-120, espejo de Panel1), RAM-only, bajo watchdog. Sin flash, sin produccion.

## 1. Resultado en una linea

El swap se ejecuto, el modulo **no cargo**, el rollback automatico devolvio el equipo a servicio en 14 s y el
banco quedo verificado sano. No hay captura PPDU porque sin modulo cargado no existe el nodo debugfs.

## 2. Lo que si quedo demostrado

| item | estado | evidencia |
|---|---|---|
| banco alcanzable y con cliente asociado | CONFIRMED | SSH `:22`, SSID `FuturaMAX-LAB`, 1 estacion a -46 dBm |
| la copia del repo es el modulo del banco | CONFIRMED | sha256 `1ef8144f…` identico en ambos |
| variante correcta identificada | CONFIRMED | el equipo corre `smallbuffers`; el `.ko` guardado era `regular` |
| parche presente en el binario | CONFIRMED | 10 marcas `fmx_ppdu_end` tras quitar debug |
| transferencia integra al equipo | CONFIRMED | sha256 local = remoto |
| rollback automatico ante fallo | CONFIRMED | `insmod` rc=255 → `restore_core_rc=0`, `restore_pci_rc=0` |
| banco restaurado y en servicio | CONFIRMED | modulos por hash, SSID arriba, cliente re-asociado, `/tmp` limpio |
| modulo cargado | **REFUTED** | el kernel lo rechaza antes de resolver simbolos |
| captura PPDU y analisis EVM | NO EJECUTADO | depende del modulo cargado |

## 3. El error exacto del kernel

```
module ath10k_core: .gnu.linkonce.this_module section size must match the kernel's built struct module size at run time
```

Esto no es un fallo del parche. `struct module` lo define el kernel: la comprobacion anterior a cualquier
resolucion de simbolos de ath10k. Nuestro modulo se compilo contra el kernel del **SDK oficial**, y el equipo
corre una **imagen propia** (el paquete instalado lleva el sufijo `fmxaggr1`), cuyo kernel no tiene la misma
configuracion. La consecuencia es incomoda pero clara. **ninguna build hecha con el SDK oficial puede cargar
en esta imagen, con parche o sin el**.

La diferencia esta medida: `.gnu.linkonce.this_module` ocupa **384 B en el `.ko` del banco** y **352 B**
en el nuestro. 32 B de desajuste, que es exactamente lo que el kernel rechaza. La seccion la genera el
kernel, no ath10k: por eso este numero prueba que el problema es la configuracion del kernel y no el parche.

Tamano de la seccion `.gnu.linkonce.this_module` medido en los tres binarios: {"shipped_banco": 384, "nuestro_smallbuffers": 352, "nuestro_strip": 352}

## 4. Dos hallazgos que valen por si solos

### 4.1 Nuestro `.ko` guardado era la variante equivocada

W359 dejo en el repo el `.ko` de la variante `regular` (`5001e8cb…`, 2 561 928 B). El banco corre
`kmod-ath10k-ct-smallbuffers` y `ath10k_core.ko` **si difiere** entre variantes (`0cb65268…`, 2 562 436 B):
el paquete pasa `-DCONFIG_ATH10K_SMALLBUFFERS` a todo el modulo. Se uso el par smallbuffers, que ya estaba
construido, y se guardo en `artifacts/ground_up/pillar2_build/ath10k_core.fmx_ppdu_end.smallbuffers.ko`.

### 4.2 El par core/pci esta acoplado y no se puede mezclar

El parche anade `void *fmx_ppdu_end;` a `struct ath10k_debug`, dentro de `struct ath10k`. Por eso un
`ath10k_pci.ko` de fabrica (sin parche) **no es intercambiable** con un `ath10k_core` parcheado. Se subio y se
uso el par emparejado de la misma build, y el watchdog restaura el par original completo. La combinacion
cruzada no se probo, y no conviene probarla.

## 5. Por que no hay captura

Sin `insmod` correcto no hay registro del driver y, por tanto, no existe
`/sys/kernel/debug/ieee80211/*/ath10k/fmx_ppdu_end/`. El nodo se crea en `fmx_ppdu_end_init()`, llamada desde
`ath10k_debug_register()`. No se activo nada, no se leyeron registros y `ppdu_evm_ranging.py` no se ejecuto.

## 6. Estado del banco al cerrar

- Modulos por hash original: core `1ef8144f…`, pci `9e758ff4…`.
- SSID `FuturaMAX-LAB` arriba, 1 estacion asociada, `MemAvailable` 9 856 kB (linea base 9 988 kB).
- `/tmp` sin ficheros propios; watchdog muerto y verificado (`procesos=0`, `sleep_600=0`).
- Cero reinicios, cero escrituras en flash. La unica diferencia cosmetica es el nombre de interfaz
  `phy2-ap0` en lugar de `phy0-ap0`, porque el indice de phy sube con cada re-registro; vuelve a `phy0` al reiniciar.

Incidencia de higiene, dicha entera: el equipo no tiene `pkill`, asi que tras el rollback quedaron dos
watchdogs vivos. Se mataron por PID y se verifico que no quedaba ninguno antes de cerrar.

## 7. El input que falta, nombrado

Para que esto funcione hace falta la **configuracion exacta del kernel de la imagen** que corre el equipo.
Hoy no esta en el repo (solo hay `config.buildinfo` de 534 y 847 B, que son semilla y no kernel), ni en WSL
(solo esta el SDK, sin arbol OpenWrt completo), ni en el equipo (`/proc/config.gz` no existe).

Via propuesta: extraer el blob `IKCFG_ST` del kernel descomprimido que ya se uso en la investigacion
anterior (sha256 `d369bc6e…`), o reconstruir con el arbol de build que produjo la imagen `fmxaggr1`.

## 8. Lo que este documento no afirma

- No afirma que el parche este mal: el rechazo ocurre antes de tocar ath10k.
- No afirma que la captura PPDU funcione: no se llego a cargar el modulo.
- No afirma que el `.ko` construido sea equivalente al de fabrica: solo que el vermagic coincide y que el
  rechazo es por configuracion de kernel.

