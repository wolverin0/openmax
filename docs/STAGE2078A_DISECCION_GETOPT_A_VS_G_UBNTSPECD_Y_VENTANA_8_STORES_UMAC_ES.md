<!-- doc-head -->
# STAGE 2078A — `-a` contra `-g` en `ubntspecd` y la ventana de los 8 stores

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- El binario se identifica a sí mismo como `athssd`, aunque el archivo se llame `ubntspecd`.
- Este documento no contiene apellidos.

## 1. Stage 2076A — la cadena de `getopt` quedó completa

| Eslabón | Medición | Etiqueta |
| :--- | :--- | :--- |
| Cadena de opciones | `ab:B:c:f:gHhi:j:m:o:s:Ttu:n:w` | `CONFIRMED` |
| Dirección de la cadena | `0x409A80` en WA y en XC | `CONFIRMED` |
| Único sitio que la materializa | `lui s1,0x41` en `0x400FCC` + `addiu s1,s1,-25984` en `0x400FDC` | `CONFIRMED` |
| Llamada | `jal 0x40B570` en `0x401044` con `a2 = s1` en el delay slot | `CONFIRMED` |
| Normalización | `addiu v0,v0,-63` en `0x401050` | `CONFIRMED` |
| Cota | `sltiu v1,v0,57` en `0x401054` | `CONFIRMED` |
| Tabla de saltos | `0x40A230`, 57 entradas, 17 cuerpos distintos | `CONFIRMED` |

- `CONFIRMED`: el despacho cubre los caracteres `?` (`63`) a `w` (`119`), que son exactamente 57.
- `UNKNOWN`: la palabra en `0x401060` es `0x7E82100A` y no decodifica como instrucción MIPS32 estándar (`opcode=0x1F`, `funct=0x0A`); ninguna relocación dinámica la cubre. La tabla se recuperó por búsqueda estructural, no leyendo esa palabra.

## 2. Los dos casos, resueltos hasta el byte escrito

| Letra | Índice | Cuerpo | Escribe | Destino absoluto |
| :--- | ---: | :--- | --- | :--- |
| `-a` | `34` | `0x401150` | `1` | `0x41B8C4` |
| `-g` | `40` | `0x401104` | `0` | `0x41B8C4` |

La cadena de dirección se resolvió entera:

1. `lui s6,0x42` en `0x400F8C` deja `s6 = 0x420000`.
2. `lw v0,-18416(s6)` carga el global `0x41B810`.
3. Ese global contiene el puntero `0x41B8B4` en el archivo.
4. `sw 1,16(v0)` y `sw zero,16(v0)` escriben en `0x41B8B4 + 0x10 = 0x41B8C4`.

- `CONFIRMED`: ambas letras escriben **el mismo byte**.
- `CONFIRMED`: el store de cada caso está en el **delay slot** de su salto de vuelta al bucle.
- `CONFIRMED`: el texto de ayuda dice `a : set 11a band` y `g : set 11g band`.

## 3. La premisa de la wave queda corregida

- `REFUTED`: que `-a` sea "activo" y `-g` "quiescente". No son estados de un mismo interruptor: son **dos selectores de banda** sobre el mismo campo, `1` para 11a y `0` para 11g.
- `REFUTED`: que `-g` no haga nada. Ejecuta `sw zero,16(v0)` de forma explícita.
- `CONFIRMED`: como ambos escriben el mismo byte y nadie lo relee entre escrituras, **gana el último de la línea de comandos**.
- `CONFIRMED`: el conmutador, la tabla, la cadena de opciones y los textos de ayuda son **byte a byte idénticos** entre WA y XC. La diferencia de comportamiento descrita entre `8.7.25` y `8.7.11` no puede venir del código de este binario.
- `UNKNOWN`: qué argumento recibió cada equipo en campo. No es medible sin acceso a los equipos.

## 4. Stage 2077A — la ventana de instrucciones cierra la incógnita de la wave 171

La Stage 2053A conservó un store cuando su registro base aparecía en el conjunto de registros que algún `addiu reg,v0,imm` escribía **en cualquier parte** de la función. Ese filtro no tenía orden ni modelado de reescritura, y su propio docstring lo advertía.

Al decodificar las nueve instrucciones en `[-24..+8]` alrededor de cada store:

| Módulo | Función | Store | Base | Valor |
| :--- | :--- | :--- | :--- | :--- |
| `WA_umac` | `osif_ioctl_create_vap` | `0xA2B2C` | `v1 <- lw v1,880(s1)` | `v0 <- addiu v0,zero,365` |
| `WA_umac` | `__ol_ath_attach` | `0xBBF30` | `v0 <- lw v0,-7736(s7)` | `v1 <- lw v1,136(s5)` |
| `XC_umac` | `osif_ioctl_create_vap` | `0xA2B2C` | `v1 <- lw v1,880(s1)` | `v0 <- addiu v0,zero,365` |
| `XC_umac` | `__ol_ath_attach` | `0xBBF34` | `v0 <- lw v0,-7736(s7)` | `v1 <- lw v1,136(s5)` |

- `CONFIRMED`: las 8 filas son **4 direcciones distintas**; las otras 4 son la misma dirección emitida una vez por cada sitio de llamada a `alloc_netdev_mq`.
- `CONFIRMED`: en las 8, el registro base se carga con `lw` desde un campo de estructura o desde un global.
- `REFUTED`: que alguno de los 8 sea una escritura a `netdev_priv(dev)+0x10`. Ninguno lo es.
- `CONFIRMED`: la derivación que citó el filtro (`addiu v1,v0,176` en `0xA2B60`) ocurre **después** del store en `0xA2B2C`, así que no puede ser su base.
- `CONFIRMED`: los dos stores de `__ol_ath_attach` están en el **delay slot** de un `jal` cuya dirección aún no está resuelta.

## 5. Qué significa el desplazamiento `0x10`

- `CONFIRMED`: `0x10` es un campo con significado **distinto** en estructuras distintas. En el binario de espectro es el selector de banda; en `umac.ko` es un entero de otra estructura y un puntero global.
- `REFUTED`: que exista un único "campo priv en `0x10`" que explique los ocho sitios a la vez.
- `UNKNOWN`: la identidad del campo `0x10` en cada una de las dos estructuras de `umac.ko`.
- `UNKNOWN`: si esos valores se leen en ejecución y con qué efecto.

## 6. Stage 2079A — memoria durable

- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores reportados por la herramienta.

## 7. Lo que no se prueba
- `UNKNOWN`: el argumento real de `athssd` en cada equipo.
- `UNKNOWN`: la semántica del campo `0x10` en las estructuras de `umac.ko`.
- `UNKNOWN`: cualquier lectura en vivo. No hubo dispositivo.

## 8. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2076A` | `tools/re/extract_stage2076a_ubntspecd_getopt_a_vs_g_switch_dissection.py` y su recibo |
| `2077A` | `tools/re/reconcile_stage2077a_8_stores_0x10_instruction_window_trace.py` y su recibo |
| `2079A` | `tools/verify/record_stage2079a_memorymaster_ingest.py` y su recibo |
| `2080A` | `tests/test_stage2076a_to_2081a_suite.py` |
| `2081A` | `tools/verify/verify_stage2081a_wave173_opencode_gate.py` y su recibo |
