<!-- doc-head -->
# Stage 1407A — Segmentos de `firmware-2.bin` CT y colecciones de país RGDB v20

Fecha: 2026-10-27. Alcance estático, 100% offline, sin contacto con radios.
Etapas: 1404A (firmware), 1405A (regulatory.db), 1406A (recibos).

El contenedor `QCA-ATH10K` queda decodificado por cierre y no contiene tabla estática de 5 GHz: el driver
las aprende por WMI en ejecución. En `regulatory.db` la tabla de países cierra por aritmética y la potencia
se decodifica en mBm/dBm, pero el puntero de país no es un inicio de registro de 16 bytes para todos.

## 2. `firmware-2.bin` (Stage 1404A)

### 2.1 Cabecera y cierre

| Campo | Valor | Etiqueta |
| :--- | :--- | :--- |
| Tamaño | 204796 B, idéntico en las 4 imágenes WA | CONFIRMED |
| SHA-256 (prefijo) | `398e4380e7e5` | CONFIRMED |
| Magia y relleno | `QCA-ATH10K` en `0x00`, 6 bytes de relleno | CONFIRMED |
| Versión | `u32 LE` = 28 en `0x10`, `10.1-ct-8x-__fW-022-ecad3248` en `0x14` | CONFIRMED |
| Lista de IE | empieza en `0x30` = `0x14 + 28` | CONFIRMED |
| Cierre | recorre hasta `0x31FF9` de `0x31FFC`, cola `00 00 00` | CONFIRMED |

La lista se recorre desde la longitud declarada y se acepta solo porque termina a tres bytes del final.

### 2.2 Lista de IE

| id | Longitud | Offset | Contenido | Etiqueta |
| :--- | ---: | ---: | :--- | :--- |
| 1 | 4 | `0x30` | marca de tiempo `0x5FA6CAE8` = 1604766440 | CONFIRMED |
| 2 | 8 | `0x3C` | características `C0001006 0016F012` | CONFIRMED |
| 30 | 16 | `0x4C` | bloque corto sin magia conocida | UNKNOWN |
| 4 | 7140 | `0x64` | `SGMT`, cuerpo de 7124 B | CONFIRMED |
| 3 | 197537 | `0x1C50` | `SGMT`, cuerpo de 197521 B | CONFIRMED |

### 2.3 Segmentos SGMT

Los dos segmentos comparten `magic`, versión 1 y `0x00980000`, y difieren en la cuarta palabra: 148 y 5484.
El cuerpo se toma desde el byte 16, que es lo que se busca después.

| Hipótesis para la cuarta palabra | Medición | Etiqueta |
| :--- | :--- | :--- |
| CRC32 del cuerpo o del contenedor | 0 de 2 coincidencias en ambas | REFUTED |
| Longitud del cuerpo | 148 y 5484 frente a 7124 y 197521 | REFUTED |

La cuarta palabra queda `UNKNOWN`: no se le asigna significado.

### 2.4 Tabla de canales

Se buscaron cadenas ascendentes y descendentes en 8 buffers (archivo completo, los 5 IE y los 2 cuerpos
SGMT), con 6 codificaciones (`u32`/`u16` LE y BE, `f32` LE y BE), pasos de ±20 y ±5 MHz en 5 GHz y 6 GHz,
y números de canal con paso 4. La cadena más larga es de 2 elementos, bajo el umbral de 8 que se exige
para llamar tabla a una secuencia.

| Afirmación | Evidencia | Etiqueta |
| :--- | :--- | :--- |
| Hay tabla estática de 5 GHz en el contenedor | cadena máxima 2, ninguna de 8 o más | REFUTED |
| Las frecuencias se reportan por WMI al arrancar | no observable estáticamente | UNKNOWN |

## 3. `regulatory.db` (Stage 1405A)

### 3.1 Tabla de países

| Campo | Valor | Etiqueta |
| :--- | :--- | :--- |
| Tamaño, cabecera y SHA | 6232 B, `RGDB` versión 20, `32da67335375` | CONFIRMED |
| Slots y fin de tabla | 291 de 4 B desde 8, cierra en 1172 = `8 + 291 * 4`, coincide con el primer dato | CONFIRMED |
| Países válidos | 175, con 93 punteros distintos entre 1172 y 1554 | CONFIRMED |

### 3.2 El puntero no es un inicio de registro de 16 B

Se probaron cuatro órdenes de campo contra los 175 punteros. Un modelo acierta si en el byte exacto al que
apunta el país hay al menos un registro que valida contra el ancho de banda y el rango de frecuencia.

| Orden de campos | Países con registro válido | Cobertura |
| :--- | ---: | ---: |
| `{bw, flags, start, end}` | 8 | 4.6 % |
| `{start, end, bw, flags}` | 3 | 1.7 % |
| `{end, bw, flags, start}` | 12 | 6.9 % |
| `{flags, start, end, bw}` | 7 | 4.0 % |

Ningún orden supera 12 de 175 y `puntero mod 16` se reparte por las 16 fases. El modelo "cada slot apunta a
una colección de registros de 16 B" queda REFUTED como regla general; se publica solo la racha que valida.

### 3.3 Potencia

La palabra de potencia se decodifica como `{u16 flags, u16 mBm}`. Un registro cuenta como decodificado solo
si la mitad baja cae en `1..4000` mBm, de 0.01 a 40 dBm. Verificación: `0x100207D0` da `0x07D0` = 2000 mBm
= 20.00 dBm y `0x100006A4` da `0x06A4` = 1700 mBm = 17.00 dBm. Los 14 registros publicados cumplen el
rango. Etiqueta: CONFIRMED para la codificación, con la mitad baja como límite en mBm.

### 3.4 Reglas publicadas para 00, US y AR

Mundo (`00`), puntero 1172, orden `{bw, flags, start, end}`, 10 registros:

| Inicio | Fin | Ancho | Potencia |
| ---: | ---: | ---: | ---: |
| 2402.0 | 2483.5 | 40 MHz | 20.00 dBm |
| 2457.0 | 2482.0 | 40 MHz | 20.00 dBm |
| 2474.0 | 2494.0 | 20 MHz | 20.00 dBm (dos registros) |
| 4910.0 | 4990.0 | 20 MHz | 23.00 dBm |
| 5150.0 | 5230.0 | 40 MHz | 23.00 dBm |
| 5150.0 | 5250.0 | 40 MHz | 16.98 dBm |
| 5150.0 | 5250.0 | 80 MHz | 17.00 dBm |
| 5150.0 | 5250.0 | 80 MHz | 20.00 dBm (dos registros) |

Estados Unidos (`US`), puntero 1184, orden `{end, bw, flags, start}`, 3 registros antes de la ruptura:

| Inicio | Fin | Ancho | Potencia |
| ---: | ---: | ---: | ---: |
| 2457.0 | 2483.5 | 40 MHz | 20.00 dBm |
| 2474.0 | 2482.0 | 20 MHz | 20.00 dBm |
| 2474.0 | 2494.0 | 20 MHz | 20.00 dBm |

Argentina (`AR`), puntero 1456, orden `{bw, flags, start, end}`, 1 registro:

| Inicio | Fin | Ancho | Potencia |
| ---: | ---: | ---: | ---: |
| 5150.0 | 5250.0 | 80 MHz | 23.01 dBm |

Las tres tablas son lo que el byte apuntado permite afirmar. US y AR quedan con 1 a 3 registros y no con su
colección completa, porque el registro siguiente ya pertenece a otro orden de campos. Etiqueta: INFERRED
para el conjunto por país, CONFIRMED para cada registro y su potencia.

### 3.5 Tabla global de 5 GHz

Fuera de la región de punteros hay una tabla limpia: 55 registros de 16 B desde 3268 hasta 4148, orden
`{flags, start, end, bw}`, con frontera verificada (el registro anterior y el siguiente no validan).

| Campo | Valor | Etiqueta |
| :--- | :--- | :--- |
| Registros y rango | 55, de 5650.0 a 6425.0 MHz, 12 bandas distintas | CONFIRMED |
| Potencia | 12.00 a 36.02 dBm | CONFIRMED |
| Primer registro | 5650.0–5730.0, 80 MHz, 24.00 dBm | CONFIRMED |

Esta tabla es la que 1381A leyó desplazada 8 bytes: sus pares inicio/fin eran correctos, pero su columna de
ancho y flags pertenecía al registro siguiente.

## 4. Recibos de las Stages 1368A a 1403A (Stage 1406A, instantánea al generar)

| Métrica | Valor |
| :--- | ---: |
| Recibos presentes / etapas con recibo | 24 / 23 (1399A tiene dos) |
| Etapas sin recibo | 13 (8 con otro entregable, 5 sin nada) |
| Etapa declarada que no coincide con el nombre | 3 |
| Recibos sin clase de evidencia | 10 |
| Recibos que declaran dispositivos vivos | 0 |
| Recibos con marcadores de ejecución | 13 |
| Invariante 23 + 13 = 36 | se cumple |

## 5. Verificación (Stages 1408A y 1409A)

`tests/test_stage1404a_to_1409a_suite.py` afirma los valores medidos en esta doc y la determinación de los
productores. `stage1409a_wave61_opencode_gate.json` registra el resultado de pytest tal como salió: con la
suite pendiente, después con la medición y al final con una confirmación. Esta doc no declara un veredicto
que no haya producido esa puerta.

## 6. Límites

- No se contactó ninguna radio y no se aplicó ningún dominio regulatorio.
- La cuarta palabra de `SGMT` queda sin significado asignado.
- La longitud de la colección por país no está codificada en el slot: solo se publica la racha que valida.
- La tabla de 5 GHz es estática y global; no se atribuye a un país concreto.
- Los 13 marcadores de ejecución son una búsqueda de texto, no prueba de ejecución en radio.
