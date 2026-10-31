<!-- doc-head -->
*STAGE1994A — RE de ath-spectral-filter, ubntspecd y derivación de s2*
# STAGE 1994A — Spectral y s2

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de módulos WA/XC y de los binarios extraídos. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 1992A — el IRQ y sus símbolos
- `CONFIRMED`: `ath_dev.ko` contiene la cadena **`ath-spectral-filter`** y **9** símbolos espectrales, entre ellos `ath_spectral_filter_init`, `ath_spectral_filter_start`, `ath_spectral_filter_stop`, `ath_spectral_control` y `ath_dev_start_spectral_scan`.
- `CONFIRMED`: `umac.ko` contiene **31** símbolos espectrales, entre ellos `ol_if_spectral_enable`, `ol_if_spectral_setup`, `ol_spectral_info_write` y `wmi_send_vdev_spectral_enable_cmd`.
- `CONFIRMED`: se encontraron **2** binarios `ubntspecd` en los rootfs de WA y XC.
- `CONFIRMED`: `request_irq` **no** aparece como importación de `ath_dev.ko`. La registración no usa el símbolo con ese nombre en esta compilación.
- `UNKNOWN`: la máscara de interrupción de hardware y el ring buffer que usa el filtro.
- `UNKNOWN`: la ruta procfs o sysfs que lo desactiva en ejecución.

## 2. Stage 1993A — de dónde sale s2
Cadena medida en el prólogo del caso:
```
addu s0, a1, zero     ; s0 = net_device *
lw   s0, 16(s0)       ; s0 = dev->priv   (offset 0x10)
jal  <vtable>         ; accessor sobre dev->priv
addu s2, v0, zero     ; s2 = valor devuelto
```
- `CONFIRMED`: **s2 no es un campo de `net_device`**. Es el valor devuelto por una llamada por vtable sobre `dev->priv`.
- `CONFIRMED`: el offset de `dev->priv` es **0x10**.
- `CONFIRMED`: al filtrar los 142 sitios de escritura por registro base `s0` o `s2`, quedan **42** candidatos, repartidos entre WA y XC.
- `UNKNOWN`: cuál de esos 42 escribe realmente el contador que se copia.

## 3. Consecuencia
- El IRQ `ath-spectral-filter` vive en `ath_dev.ko`; el control de la exploración vive en `umac.ko` y viaja por WMI.
- La copia de 4624 bytes no sale de un campo del netdev: sale de una estructura obtenida por vtable, lo que explica por qué el estudio de offsets del netdev no la encontraba.
- Los 42 candidatos siguen sin atribución; el stage no inventa un escritor.

## 4. Stage 1995A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: máscara de IRQ y ring buffer.
- `UNKNOWN`: knob procfs/sysfs de desactivación.
- `UNKNOWN`: el escritor real entre los 42 candidatos.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1992A` | `tools/re/extract_stage1992a_ath_spectral_filter_irq_and_ubntspecd_re.py` y su recibo |
| `1993A` | `tools/re/reconcile_stage1993a_s2_netdev_priv_derivation_and_writers.py` y su recibo |
| `1995A` | `tools/verify/record_stage1995a_memorymaster_ingest.py` y su recibo |
| `1996A` | `tests/test_stage1992a_to_1997a_suite.py` |
| `1997A` | `tools/verify/verify_stage1997a_wave159_opencode_gate.py` y la compuerta de la wave |
