<!-- doc-head: Wave366b P3b — X07 corregido: fichero NRCC de Candela descargado, identificado y documentado; X05 aplazado -->

# STAGE3026B — X07 corregido: el firmware NRCC, no el que ya corremos

Descarga offline. Sin acceso a equipos. W366 habia traido `firmware-2-ct-full-community-22.bin.lede.022`,
que es exactamente el fichero que ya llevamos; este wave trae la variante NRCC, que es la candidata de verdad.

## 1. El fichero

| campo | valor |
|---|---|
| fichero | `firmware-2-ct-full-nrcc-community-22.bin` |
| URL | `https://www.candelatech.com/downloads/firmware-2-ct-full-nrcc-community-22.bin` |
| HTTP | 200, `Content-Length` 202 844, `Last-Modified` 2021-11-08 20:52:18 GMT |
| bytes | 202844 |
| sha256 | `cdc1af3c3df3d56134f4c6d3b5326ce2682314ee4288cc4f41012cfb0dd76b2d` |
| hash publicado | **ninguno** (ver abajo) |
| cabecera | `QCA-ATH10K..........10.1-ct-8x-_AfW-022-d8dab8e8........G..a....` |
| version interna | `10.1-ct-8x-_AfW-022-d8dab8e8` |
| en `firmware_bad.txt` | no, 0 coincidencias exactas a nivel raiz |

### No hay hash publicado, y lo digo claro

Candela no publica sumas para estos ficheros: `firmware_status.txt` pesa **0 bytes** y las notas de release
no mencionan md5, sha ni checksum en ninguna linea. A diferencia del fichero no-NRCC, que si tiene `HASH:=`
en el paquete de OpenWrt, **aqui la integridad no se puede anclar en un hash publicado**. Lo que si queda
anclado: tamano exacto, fecha del servidor, cabecera `QCA-ATH10K`, cadena de version interna y la
comprobacion de que el fichero no aparece en la lista de ficheros corruptos de Candela.

## 2. Correccion de premisa: los dos son 10.1

| fichero | bytes | version interna |
|---|---|---|
| NRCC (candidato) | 202844 | `10.1-ct-8x-_AfW-022-d8dab8e8` |
| community-22 (el que corremos) | 204796 | `10.1-ct-8x-__fW-022-ecad3248` |

Mismo release 22 y misma rama `10.1-ct-8x`. Lo que cambia el NRCC **no es la rama**, es la cache de
rate-ctrl. Decir que pasariamos de 10.2 a 10.1 seria falso: ya estamos en 10.1.

## 3. Que cambia el NRCC, segun Candela

De `ath10k_release_notes.txt` (Release 22, 8 de noviembre de 2021), lineas 382-400, citado literal:

> I am also now compiling a firmware variant that has no rate-ctrl caching (nrcc) at all. This appears
> to scale well up to 100 plus peers. This option should be good for most users (8 vdevs, 128 peers, etc),
> but it uses too much RAM to be used by users wanting 64 vdevs.

En corto: **sin cache de rate-ctrl**, escala mejor con muchos peers y cuesta RAM, hasta el punto de que
Candela lo desaconseja para 64 vdevs. Candela anade que su 10.1 supera al stock 10.2.4 build 70 y al CT 10.2.

Estas cuatro frases son **afirmaciones del fabricante**, no medidas nuestras. Se etiquetan INFERRED y no
se presentan como resultado: para eso haria falta una comparacion en banco con CPEs reales.

## 4. X05: aplazado, sin construir nada

`ag71xx_legacy` queda **DEFERRED**. La razon ya estaba medida: `CONFIG_AG71XX_LEGACY=y` lo enlaza dentro
del kernel, no existe `ag71xx_legacy.ko` y las fuentes no estan en el arbol de build. Obtener las dos
variantes de peso NAPI exige reconstruir el kernel completo, no compilar un modulo.

Se suma un dato de W356 que cambia el plan: una build del SDK oficial no carga en la imagen propia del
equipo, porque `struct module` mide 384 B en el banco y 352 B en el SDK. Cualquier rebuild del kernel
tiene que partir de la configuracion exacta de esa imagen, que hoy no tenemos.

## 5. Artefactos

- `artifacts/ground_up/x05_x07_build/firmware-2-ct-full-nrcc-community-22.bin` — el candidato NRCC
- `artifacts/ground_up/x05_x07_build/ath10k_release_notes.txt` — notas de release, fuente de la cita
- `artifacts/ground_up/x05_x07_build/manifest_x07_nrcc.json` — manifiesto con todo lo anterior
- `artifacts/ground_up/x05_x07_build/firmware-2-ct-full-community-22.bin.lede.022` — el fichero de W366, que es el que corremos

## 6. Lo que no se afirma

- No se afirma que el NRCC mejore nada en nuestro despliegue: solo se documenta que cambia y que dice Candela.
- No se afirma que el fichero sea autentico por hash: no hay hash publicado; se ancla por tamano, fecha,
  cabecera, version interna y ausencia en la lista de corruptos.
- No se afirma nada sobre comportamiento en runtime: no hubo acceso a equipos en este wave.

