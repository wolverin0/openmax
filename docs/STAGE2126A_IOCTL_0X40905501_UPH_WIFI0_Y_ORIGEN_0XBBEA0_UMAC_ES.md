<!-- doc-head -->
# STAGE 2126A — El ioctl `0x40905501` del dispositivo `uph` y el origen de `0xBBEA0` en `umac`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2124A — el pedido, del lado del usuario

La palabra `0x40905501` se decodificó por bits, sin usar cabeceras:

| Campo | Valor | Etiqueta |
| :--- | :--- | :--- |
| Dirección | `write` (`_IOC_WRITE`) | `CONFIRMED` |
| Tamaño | `144` = `0x90` | `CONFIRMED` |
| Tipo | `0x55` = `'U'` | `CONFIRMED` |
| Número | `1` | `CONFIRMED` |

- `CONFIRMED`: es `_IOW('U', 1, 0x90)`, exactamente como decía el encargo.
- `CONFIRMED`: el buffer que se pasa al `ioctl` tiene **144** bytes.

### El nombre del dispositivo sí es fijo

- `CONFIRMED`: la cadena pasada al manejador es `wifi0`, en `0x409854`.
- `CONFIRMED`: la ruta construida es por tanto **`/dev/uph_wifi0`** en las dos familias.
- `REFUTED`: la lectura de la Stage 2088A de que el nombre fuese variable. El **formato** es variable, pero el **argumento** es la constante `wifi0`, así que la ruta efectiva no cambia en este binario.

### Grafo de llamadas

| Nodo | Llamadores |
| :--- | :--- |
| `0x406550` (hace el `ioctl`) | `0x405C20` |
| `0x405BF8` (abre, ioctla, cierra) | `0x401DC8`, `0x402298`, `0x4077BC` |
| `0x4064E0` (construye la ruta y abre) | `0x405C10`, `0x407850` |

- `CONFIRMED`: el helper del `ioctl` tiene **un solo** llamador por familia, y vive dentro de un envoltorio que también abre y cierra.
- `CONFIRMED`: ese envoltorio tiene **tres** llamadores por familia. Es el punto de entrada real del camino, no el helper.
- `CONFIRMED`: el buffer de 144 bytes llega al helper como el `a0` del envoltorio y se reenvía sin transformación.

## 2. Stage 2124A — el pedido, del lado del kernel

`ubnt_poll_host.ko` existe en las dos familias, pesa 189880 bytes y registra un dispositivo de caracteres (`register_chrdev_region`).

| Medición | WA | XC |
| :--- | ---: | ---: |
| Materializaciones de `0x40905501` | 1 | 1 |
| Dirección | `0x1E90` | `0x1E90` |
| Destino del `beq` | `0x1ED0` | `0x1ED0` |

- `CONFIRMED`: el módulo **compara** el comando contra `0x40905501` y salta a `0x1ED0`. El pedido del usuario y el del kernel son el mismo número.
- `REFUTED`: que el dueño de esa comparación sea `ubnt_poll_host_uninit_char_dev`. Ese símbolo empieza en `0x1DD0` y mide 12 bytes, así que no cubre `0x1E90`.
- `CONFIRMED`: la comparación vive en una función **sin símbolo** que empieza en `0x1E58` con el prólogo `addiu sp,sp,-24`.
- `CONFIRMED`: el cuerpo en `0x1ED0` llama con `a0 = *(v0+96)` y `a1 = a3`, y devuelve `-22` cuando el argumento es nulo.

### La familia de comandos

- `CONFIRMED`: además de `0x40905501`, el módulo compara contra `0xC0015502` y `0xC6945503`, que decodifican como `_IOWR('U', 2, 1)` y `_IOWR('U', 3, 1684)`.
- `CONFIRMED`: los tres pedidos de la familia `'U'` (números 1, 2 y 3) están cubiertos por el mismo despacho.
- `REFUTED`: que la constante `0x10325476` sea un pedido de la familia `'T'`. Por bits daría eso, pero es el cuarto valor inicial de MD5 y no un `ioctl`. Se descarta como falso positivo.

## 3. Stage 2125A — el origen de `s7` en `0xBBEA0`

- `CONFIRMED`: el sitio está en `__ol_ath_attach`, entrada `0xBBDC4` en WA y `0xBBDC8` en XC.
- `CONFIRMED`: `s7 = s0 + fp` y `fp` se carga con `lui fp,0x2`, es decir **`0x20000`**.
- `CONFIRMED`: `s0` **no** es un argumento directo. Se define como `addu s0,v0,zero` en `0xBBE3C` (WA) y `0xBBE40` (XC), justo después de la llamada en `0xBBE30` y `0xBBE34`. El valor viene de un retorno.
- `CONFIRMED`: los argumentos se aliasan aparte, en el prólogo: `s3 = a1`, `s4 = a0`, `s5 = a2`, `s6 = a3`.
- `CONFIRMED`: el desplazamiento `-7752` es `-0x1E48`, y `0x20000 - 0x1E48` da **`0x1E1B8`**. La aritmética negativa y el campo positivo de la Stage 2112A coinciden.
- `REFUTED`: que `s7` se derive directamente de `a0`. Se deriva de un retorno de llamada, con el `0x20000` sumado después.

### Funciones hermanas

- `CONFIRMED`: en todo `umac.ko` hay **2** escrituras por familia con esos desplazamientos: `sw s5,-7744(v0)` y `sw zero,-7752(s7)`, y las dos están en `__ol_ath_attach`.
- `CONFIRMED`: **ninguna** otra función del módulo toca `-7756`, `-7752`, `-7748` ni `-7744`. La lista de hermanas está vacía.
- `REFUTED`: que existan funciones hermanas que inicialicen el mismo sub-objeto. No las hay en este módulo.

## 4. Lo que queda abierto
- `UNKNOWN`: el diseño del buffer de 144 bytes campo por campo. El usuario lo pasa opaco y no lo rellena en el punto observado.
- `UNKNOWN`: el nombre de la función del kernel en `0x1E58`; no tiene símbolo.
- `UNKNOWN`: el destino de la llamada de `0xBBE30`, que produce el `s0` del que sale `s7`.
- `UNKNOWN`: quién más, fuera de `umac.ko`, escribe el campo `0x1E1B8`.

## 5. Stage 2127A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2124A` | `tools/re/extract_stage2124a_uph_ioctl_0x40905501_user_and_kernel_re.py` y su recibo |
| `2125A` | `tools/re/reconcile_stage2125a_umac_0xbbea0_s7_origin_and_attach_re.py` y su recibo |
| `2127A` | `tools/verify/record_stage2127a_memorymaster_ingest.py` y su recibo |
| `2128A` | `tests/test_stage2124a_to_2129a_suite.py` |
| `2129A` | `tools/verify/verify_stage2129a_wave181_opencode_gate.py` y su recibo |
