<!-- doc-head: Wave 263 (2616A-2621A) nota 665 ES: metodo last30days rotulado como hipotesis, veredicto vivo de dos rondas en Guarida (2610A) y estado de telemetry.db -->
last30days: tres patrones convertidos en hipotesis falsables A1-B1-A2-B2; su paso de busqueda web/scholar no se corrio (wave offline).
Guarida 2610A (captura de solo lectura de otra lane): 6 de 6 estaciones RF_UP_QUALIFIED en Panel1 .84 y Panel3 .83, pero ningun envio a Kuma: causa de sitio UNKNOWN.
telemetry.db: el escritor es intermitente y no hay ninguna comparacion antes/despues calculada.
El hook ahora inyecta las reglas una vez por conversacion; tras una compactacion no se reinyectan. Tablero :8787 banda 1536A..2621A HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #665: metodo last30days, veredicto vivo de Guarida y telemetry.db

**Wave 263 - Etapas 2616A-2621A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se escribio la nota evergreen #665 con tres partes: la skill last30days tomada como metodo, el veredicto vivo de dos
rondas que otra lane capturo en Guarida (2610A, solo lectura, 0 escrituras de radio o configuracion) y el estado de
tools/observability/telemetry.db, leida solo en modo lectura. Se corrieron `hyperresearch sync` e `hyperresearch index
build` (ambos devolvieron 0), el tablero :8787 se amplio a 1536A..2621A y se agrego una linea al final de CURRENT_STATE.md.

Titular honesto: **no se midio nada nuevo y no hay campeon**. Lo vivo es la captura 2610A de otra lane.

## (A) last30days: metodo rotulado, no adoptado

- La skill (sin seguimiento en git, de otra lane) no cita ninguna URL, DOI ni paper; sus "3x+" y "4x" son texto propio
  sin fuente. Su paso 1 (barrido web y scholar de los ultimos 30 dias a 6 meses) **no se ejecuto**: la wave es offline.
- Cada patron queda como hipotesis falsable, con la ruta a verificar primero, prueba A1-B1-A2-B2 de ventana fija con
  watchdog de 45 s / 120 s y destino de telemetria en telemetry.db:
  - Presupuesto NAPI (netdev_budget, netdev_budget_usecs, dev_weight, threaded por interfaz) en un AP de 64 MB: rotulo
    UNKNOWN.
  - Bucle evolutivo de ventana fija: rotulo INFERRED, coincide con nuestro arnes; aplica a la pregunta RTS 512 de Panel3.
  - Presion de memoria fq de mac80211 en placas de 64 MB: rotulo UNKNOWN; primero comprobar que el contador exista.
- Ningun numero prometido. El cuarto patron (decompilacion de binarios por MCP) no se uso: no se abrio ningun binario.

## (B) Veredicto vivo de dos rondas en Guarida (2610A)

| Estacion | Ronda 1 | Ronda 2 | Veredicto | Envio a Kuma |
| :--- | :--- | :--- | :--- | :--- |
| panel1-84-cpe-001 | 0 % | 0 % | RF_UP_QUALIFIED | bloqueado |
| panel1-84-cpe-002 | 0 % | 0 % | RF_UP_QUALIFIED | bloqueado |
| panel1-84-cpe-003 | 0 % | 0 % | RF_UP_QUALIFIED | bloqueado |
| panel3-83-cpe-001 | 0 % | 0 % | RF_UP_QUALIFIED | bloqueado |
| panel3-83-cpe-002 | 0 % | 0 % | RF_UP_QUALIFIED | bloqueado |
| panel3-83-cpe-003 | 40 % | 20 % | RF_UP_QUALIFIED | bloqueado |

- Los dos AP en solo lectura; 2 rondas de 5 pings tras 5 de base; el manifiesto de vecinos coincide con el despliegue
  2588A; peers asociados 3 -> 3 en ambos AP.
- Todos los envios quedan bloqueados porque la causa de sitio es UNKNOWN (falta telemetria de backhaul y de los vecinos
  de torre); el puente quedo en EVALUATED_PAYLOAD_ONLY y no hizo ningun envio HTTP.
- panel3-83-cpe-003 sigue en UP con 40 % y 20 % de perdida: la regla heredada mira el progreso RF/L2, no la perdida ICMP.
  Eso habla de la regla, no da por sana a esa estacion.
- `bridge fdb show` devolvio 127 (no existe) en ambos AP, 1 de 96 comandos en cada uno.

## (C) telemetry.db

- Cuatro tablas; agent_runs y tool_telemetry vacias; las muestras antes/despues son OBSERVED o ERROR, de varias corridas
  cortas de hoy (conteos exactos en el recibo 2616A).
- El escritor es intermitente: en esta sesion hubo unos cuatro minutos sin proceso y sin filas nuevas, y luego arranco una
  corrida nueva que si escribe. El recibo guarda las dos observaciones.
- **Cero comparaciones antes/despues calculadas**: change_pct nulo en todos los nodos, deltas sin muestra previa, y
  ninguna referencia de stock marcada como comparable con el estado vivo en reposo.

## (D) Cambio del hook durante la wave (informado, no editado)

- Otra lane hizo que el hook inyecte el bloque de reglas prohibidas de olvidar una sola vez por conversacion, con un archivo
  de marca. Ningun hook del repo borra esa marca, asi que despues de una compactacion no se vuelve a inyectar; sin id de
  conversacion todas las llamadas comparten una sola marca. El contrato 2604A sigue en verde porque mira el texto, no la
  frecuencia de entrega. El gate 2609A se ajusto para registrar esos cambios ajenos en lugar de fallar por ellos.

## Etapas 2617A a 2621A

- 2617A: tablero reconstruido hasta 2621; HTTP 200 con la banda nueva; 0 apellidos y 0 alias en la pagina; las tarjetas
  2610A y 2616A sin IP, sin MAC y sin nombres.
- 2618A: este documento y la linea final de CURRENT_STATE.md (196 lineas, por debajo de 220).
- 2619A: dos claims en MemoryMaster (project:futuramax) y filas CRLF en results.tsv.
- 2620A: suite tests/test_stage2616a_2621a_note665_gate.py con pruebas negativas.
- 2621A: gate tools/verify/verify_stage2621a_gate.py -> artifacts/verification/stage2621a_wave263_opus2_gate.json.

## Aclaraciones del pedido

- El nombre de la nota tiene 98 caracteres; hyperresearch corta el id del vault a 80, asi que el id es el nombre truncado.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin medicion nueva en esta wave; no se abrio ningun binario.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteo de PII.

## Que sigue (decision del operador)

- Decidir si el hook debe reinyectar las reglas tras una compactacion.
- Juntar telemetria de backhaul y de vecinos de torre para que la causa de sitio deje de ser UNKNOWN.
- Repetir rondas temporizadas sobre panel3-83-cpe-003 antes de tocar Panel3.
- Correr el paso 1 de last30days con busqueda real en una wave con red, antes de probar cualquiera de las tres hipotesis.

Recibos: `stage2616a_last30days_and_guarida_verdict_note665_receipt.json`, `stage2617a_command_center_1536a_2621a_refresh_receipt.json`,
`stage2619a_memorymaster_ingest_receipt.json`, `stage2621a_wave263_opus2_gate.json`.
