<!-- doc-head: W408: PUT ui-url se procesa dentro de udapi-bridge y se traduce en GET/PUT services; RE offline del ELF fijado -->
ELF: 606816 B, SHA256 11c8f687586ef65fc0115966d3b6bded16f46b9f16568550692080aa5f01716e.
El companion no tiene por qué recibir PUT /tools/unms/ui-url: el callback interno llama al store airOS, que usa /services.
Un request idéntico al stock puede fallar por el backend local; esto no identifica todavía la rama ejecutada en el banco.
Solo análisis estático, sin dispositivos, cambios de configuración ni ejecución del ELF.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W408 — UI URL: rechazo interno y dependencia del backend

## Ruta y esquema

En el ELF exacto `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/bin/udapi-bridge`, `new_module_ui_url` (`0x4505b0`) registra el callback PUT interno en `0x44fe5c`. La URL de UI se maneja dentro del bridge; ese callback no reenvía el PUT original al companion.

El generador UISP 3.1.70 retenido lo confirma por el lado emisor: `device-ws.js:123700`, función `hzr`, llama a `Lue({uiURL:n})`; `Lue`, `jo`, `Xm` y `W8` (`:123652`) forman un RPC de socket `udapi`, método `PUT`, entidad `/tools/unms/ui-url`, versión `v1.0`, con `request:{"uiURL":"<valor>"}`. **La clave es `uiURL`, directamente bajo `request`**, no `url` ni un contenedor `body`. Los fragmentos, offsets de carácter y SHA están en `STAGE3068A_server_request_context.json`; el minificado exige ese offset además de la línea.

## Salidas error 4 del callback UI URL

| Guarda | Sitio VA | Resultado |
| --- | --- | --- |
| `request` presente con tipo distinto de object/array, antes del callback | `0x4434a0–0x4434e0` | El wrapper genera 4 |
| No existe el miembro `uiURL` | `0x44fecc` | Retorna 4 |
| Tipo JSON distinto de string (enum 6) | `0x44fefc` | Retorna 4 |
| Extracción de string devuelve NULL | `0x44ff2c` | Retorna 4 |
| El store callback devuelve falso | `0x44ff60` | Retorna 4; incluye errores del backend aun con cuerpo válido |

Las cuatro salidas del callback convergen en `0x44ff80`, con retorno 4 en `0x44ff8c`. El helper `0x442330` convierte el enum 4 en el JSON `statusCode:400` (`0x4423f8`) y `error:4` (`0x442438`). Es el estado de una respuesta UDAPI dentro del transporte RPC; no se observó un status HTTP de transporte en esta ola. Un puntero de store no instalado devuelve **6**, distinto de esos caminos. El recibo nativo fija el flujo de despacho, las direcciones de archivo y las guardas internas del store. La enumeración se limita a los caminos alcanzables por este PUT; no pretende enumerar errores de módulos ajenos.

El mensaje genérico del enum 4 es `A field is missing in the request`, incluso cuando la causa es el store/backend. Por tanto ese texto no demuestra que falte un campo en la petición UISP original.

## Qué hace el store de airOS

`unms_ui_url_store_airos` (`0x429d00`) usa el backend UDAPI local:

1. Solicita `GET /services`.
2. Exige una respuesta utilizable y el miembro `response.unms`.
3. Añade o sustituye `unms.uiURL` por la cadena recibida.
4. Envía `PUT /services` con el objeto de servicios completo modificado.
5. Una respuesta ausente o considerada error impide éxito y propaga falso al callback UI URL, que devuelve 4.

`is_udapi_response_error` (`0x4420ec`) exige que `response` sea un objeto. Dentro de ese objeto, `statusCode` ausente o no integer se considera no-error; si es integer, 200 es no-error y otro valor es error. Esta función no usa el miembro `error` como guarda. No se exige indebidamente que toda respuesta incluya `statusCode:200`.

La cadena y los objetos deben cumplir las comprobaciones del recibo; la presencia de `response.unms` no equivale a habilitar un servicio. El store comprueba presencia de `unms`, sin una guarda explícita de tipo object en ese punto; el comportamiento de la biblioteca con un tipo malformado queda `UNKNOWN`. No se debe inventar su estado para pasar la guarda. El recibo enumera 17 sitios de rama que hacen fallar el store, incluidos transporte y respuestas.

El wiring airOS queda fijado por `config_parse` (`0x40c410`): copia la tabla `0x459c4c` a `config+0xb8`; la entrada `tabla+0x10` contiene `0x429d00` y queda en `config+0xc8`. El módulo se registra si ese callback no es NULL (`0x441728–0x441744`). No se deduce la selección airOS únicamente del nombre del ELF.

## Cruce con el companion de W406

El C de 20366 B fijado por SHA256 `4a77a6c6d1cfaefc06347b124cabe186d9463c32f1ca790af851232d6b1241f8` tiene, en `udapi_cache_server.c:206–214`, una excepción no-op únicamente para `PUT /tools/unms/ui-url`. Cualquier `PUT /services` cae en `405`, con `error:405`. Ese no-op no satisface la ruta interna descrita arriba.

`udapi_cache_mapper.py:35,227–243` permite datos de `unms.enabled` cuando vienen de hechos de entrada; no garantiza que cada caché contenga `unms`. Un GET de servicios sin ese miembro puede fallar antes del PUT posterior. Los pines y fragmentos están en `STAGE3068A_companion_context.json`.

Esto ofrece al menos dos fallos locales distinguibles: falta de `response.unms` y rechazo del PUT de servicios. La ausencia del PUT original en la auditoría no demuestra que el companion no recibiera GET/PUT de **otra entidad**. W400 conserva el 400/4 en vivo, pero esta ola no accedió a sus cuerpos privados ni al dispositivo: la rama efectivamente ejecutada sigue `UNKNOWN`.

## Validación, sanitización y requisitos locales

La validación comprobada en el callback es presencia/tipo/extracción de `uiURL` y resultado del store. No se encontró un validador de scheme/host URL en esa cadena. El helper de string `0x422640` corrige UTF-8 inválido mediante U+FFFD: eso no valida ni sanitiza una URL. El nombre del RPC `setSanitizedUispUrl` no demuestra saneamiento de credenciales ni autenticación adicional. El recibo nativo distingue estas comprobaciones de la autenticación de la conexión exterior y de cualquier validación del backend.

No se encontró una guarda adicional de autenticación/sesión en el callback PUT ni en el store. El wrapper transporta contexto de sesión/origen; eso no prueba ausencia de autenticación en toda la conexión. La autorización end to end y las reglas del backend quedan fuera de esta prueba estática de la ruta. Tampoco hay lectura/escritura directa de `system.cfg`, `running.cfg` ni ejecución de un helper de configuración en esta cadena: el estado se delega al backend de servicios.

Para que el store tenga éxito necesita un backend local accesible con GET de servicios, datos reales de `unms` en la forma esperada y aceptación coherente del PUT de servicios. Usa el socket de `context+0x94`, por defecto `/var/run/ubnt-udapi-server.sock` (asignación `0x40c8b0`). La cadena síncrona `edgeos_socket_roundtrip` (`0x41bf08`) → `edgeos_socket_open` (`0x41b904`) pasa los parámetros de bind local en NULL: **no usa el bind `/run/udapi-bridge-stream.sock.<PID>` en esta ruta**. Ese bind de W387 pertenece al forwarder separado. No basta crear un fichero regular con el nombre del socket: debe existir un listener compatible y su directorio padre.

No se implementó un writer de configuración ni se amplió la API del companion en esta ola. Una eventual emulación RAM de esta transacción debe definir su semántica y restauración en el contrato de lane_2; una respuesta de éxito no debe presentarse como persistencia o configuración aplicada si es un no-op.

## Evidencia y entrega

`artifacts/autoresearch/wave408_uiurl_static.json` es el recibo principal; `docs/STAGE3068A_native_*` conserva inventario, código de análisis y desensamblados. El gate separa RE estática, inferencia sobre W400 y aceptación física. El primer aviso crítico se envió exclusivamente al orquestador mediante `<orca-id>`. Tras entregar W408 se retoma W402.
