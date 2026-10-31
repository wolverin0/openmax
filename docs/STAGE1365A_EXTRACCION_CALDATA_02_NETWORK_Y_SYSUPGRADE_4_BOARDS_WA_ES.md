<!-- doc-head: Stage 1365A - el QCA9882 de las cuatro placas WA lee su calibracion de art+0x5000 por celdas nvmem del arbol de dispositivo, no por script; 02_network mapea lan=eth0 en las cuatro; sysupgrade escribe la particion firmware; auditoria 1320A..1355A -->
# Stage 1365A — Caldata, `02_network` y sysupgrade en las 4 placas WA

- **Caldata**: [`stage1362a_wa_squashfs_caldata_and_sysupgrade_re.json`](../artifacts/verification/stage1362a_wa_squashfs_caldata_and_sysupgrade_re.json)
- **Red**: [`stage1363a_wa_squashfs_02_network_map.json`](../artifacts/verification/stage1363a_wa_squashfs_02_network_map.json)
- **Auditoría**: [`stage1364a_waves47_to_52_receipt_audit.json`](../artifacts/verification/stage1364a_waves47_to_52_receipt_audit.json)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún equipo.

## 1. La calibración del QCA9882 no la extrae un script

La pregunta era de qué offset de `art` (`mtd5`) lee OpenWrt el caldata PCIe. La respuesta medida:
**de `art + 0x5000`, 2.116 bytes**, y no lo hace ningún script — lo hace el kernel.

El nodo `wifi@0,0` del árbol declara:

```
compatible       = "qcom,ath10k"
nvmem-cell-names = "calibration"
nvmem-cells      = <16>
```

Y el phandle 16 resuelve, en las cuatro placas, a la celda `calibration@5000` de `art`:

| Celda | Phandle | Offset | Tamaño | Consumidor |
| :--- | :-: | -: | -: | :--- |
| `macaddr@0` | 7 | `0x0000` | **6 B** | MAC base |
| `calibration@1000` | **13** | `0x1000` | **1.088 B** | `wmac@18100000` (2,4 GHz) |
| `calibration@5000` | **16** | `0x5000` | **2.116 B** | `wifi@0,0` (QCA9882) |

El bloque de 2,4 GHz usa el mismo mecanismo con phandle 13. Las cuatro placas coinciden en los tres
phandles.

## 2. Los scripts existen, pero no cubren estas placas

Extraje los cuatro ficheros del `rootfs` de las cuatro imágenes. Los cuatro están presentes en las
cuatro y son **byte a byte idénticos** entre placas (el `rootfs` es compartido):

| Fichero | Bytes | ¿Cubre las WA? |
| :--- | -: | :--- |
| `lib/upgrade/platform.sh` | 3.070 | sí, por la rama por defecto |
| `lib/functions/caldata.sh` | 4.852 | es infraestructura genérica |
| `etc/hotplug.d/firmware/11-ath10k-caldata` | 546 | **no** |
| `etc/hotplug.d/firmware/10-ath9k-eeprom` | — | **no** |

`11-ath10k-caldata` solo tiene ramas para `dlink,dir-842-c1`, `c2` y `c3`; para cualquier otra placa
hace `exit 1`. La búsqueda de los cuatro tokens `ubnt,*` en ese fichero da **0 coincidencias** en las
cuatro imágenes. Por eso el camino real es la celda `nvmem` y no el script.

Esto importa para el plan: **no existe un paso de usuario que haya que ejecutar** para poblar el
caldata. Si el árbol está bien, el kernel lo lee; si la celda apunta mal, no hay script que lo arregle.

## 3. `02_network`: lan es eth0 en las cuatro

El fichero tiene 21.651 bytes y es idéntico en las cuatro imágenes. Las cuatro placas caen en **un solo
bloque de patrones** (la primera rama del primer `case`, líneas 1–138, **126 patrones**) cuya acción es:

```sh
ucidef_set_interface_lan "eth0"
```

| Placa | ¿Rama encontrada? | `lan` | `wan` | switch |
| :--- | :-: | :--- | :-: | :-: |
| PBE-5AC-Gen2 | sí | **`eth0`** | ninguno | no |
| LBE-5AC-Gen2 | sí | **`eth0`** | ninguno | no |
| LAP-120 | sí | **`eth0`** | ninguno | no |
| NS-5AC-Loco | sí | **`eth0`** | ninguno | no |

Sin `wan` y sin switch definido. Eso concuerda con el árbol de la Wave 50: el switch interno está
`status = "disabled"` y la placa usa el GMAC `eth@19000000`. `eth1` existe como controlador pero
`02_network` no lo nombra nunca.

## 4. Sysupgrade: siempre la partición `firmware`

`platform.sh` fija `PART_NAME=firmware` y ninguna rama del `case` de `platform_do_upgrade` lista una
placa WA, así que caen en la rama por defecto:

```sh
*)
	default_do_upgrade "$1"
```

Es decir: el `sysupgrade.bin` se escribe en la partición `firmware`, la misma que la Wave 50 midió en
**`0x00050000`, `0x00f60000` bytes**. No hay ruta de sysupgrade que toque `u-boot`, `u-boot-env`, `cfg`
ni `art` — coherente con los `read-only` del árbol y con el límite de seguridad del proyecto.

## 5. Auditoría 1320A..1355A

| Medida | Valor en el corte final |
| :--- | -: |
| Números de etapa | **36** |
| Etapas con recibo | **23** (24 ficheros; una etapa tiene dos) |
| Etapas sin recibo | **13** |
| Recibos sin clase de evidencia | **14** |
| Recibos que declaran dispositivos vivos | **2** |
| Recibos con marcador de runtime en el texto | **16** |

La ventana **ya no es puramente estática**: `1344A` (radiografía PtP read-only) y `1345A` (respaldo
mtd y sha256 del `art`) declaran dispositivos tocados. Son de otro lane y aterrizaron durante la wave,
así que el recibo es la fuente de las cifras y no esta tabla.

Los marcadores de runtime son una **búsqueda de texto** (`dmesg`, `iw dev`, `ssh`, `/sys/class`), no
prueba de ejecución. Que 14 de 24 recibos no declaren clase de evidencia sí es un hueco de forma: sin
ella no se pueden graduar.

## 6. Consecuencia operativa

1. El respaldo de calibración que importa es **`art` completo** (64 KiB); los dos rangos que el kernel
   consume son `0x1000`+1.088 B y `0x5000`+2.116 B.
2. Si el árbol de una placa no declarase esas celdas, el caldata no se cargaría: comprobarlo es leer
   `nvmem-cells` del nodo wifi, no buscar un script.
3. Un `sysupgrade` no necesita escribir `art` ni `u-boot`; si alguna vez lo hiciera, sería un fallo.
4. La red de las cuatro es **una sola interfaz**, `lan = eth0`: no hay `wan` que proteger.

## 7. Huecos

- **CONFIRMED** — offsets, phandles y ficheros medidos en las cuatro imágenes.
- **UNKNOWN** — el contenido real de `art` en cada unidad; esta etapa no leyó `mtd5` de ninguna radio, aunque el recibo `1345A` de otro lane sí respaldó ese `mtd`.
- **UNKNOWN** — si el `rootfs` de una placa ya actualizada difiere del que trae la imagen.
- **Límite conocido** — los scripts son los de la imagen, no los de un `rootfs` en ejecución.
- **No intentado** — arrancar una placa y leer `/etc/config/network` o `/sys/class/leds/`.
