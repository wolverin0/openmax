<!-- doc-head: Wave 394; banco LAP-120/Loco, calificacion adversa de MCS forzado y ensayo AQL de un peer con restauracion exacta -->
Estado: hallazgos y restauracion CONFIRMED; promocion NO_GO. H3 y fairness UNKNOWN.
Evidencia: artifacts/autoresearch/wave394_h1_h3_ab.json.
Solo banco autorizado; sin produccion ni cambios persistentes.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 3054A: bajada, agregacion y AQL en banco

## Prioridad y alcance

- W398 midio Panel2: bajada 49,6%, subida 8,0%, aire ajeno/no decodificado 19,9%.
- Eso debilita la explicacion centrada en subida lenta; no demuestra la causa de la bajada.
- Banco: AP .20, Loco logica .250 / RF .200.41; SSH IPv6 con claves de host fijadas.
- AP en 5180 MHz/VHT20. No se accedio a .198 ni a radios de produccion.
- El coordinador aprobo un solo peer: fairness entre estaciones queda UNKNOWN.

## Calificacion previa: resultado adverso real

- Getter nativo `htt_max_amsdu_ampdu 3 64`; candidato del ledger `2 64`.
- Primer campo A-MSDU, segundo A-MPDU. No es una prueba de A-MPDU 64 contra 2.
- Se guardaron los diez campos originales de `set_rate_override` y se armo watchdog de 45 s.
- Una activacion VHT/MCS0/NSS1: `active=1 mcs=0 nss=0 pream=3`; los otros campos se conservaron.
- `retries=0` se codifica como 1: ese perfil no conserva los reintentos automaticos.
- Crash CT a los 0,330740 s; GUID `<uuid>`.
- Se conservan timeout, dump nativo y advertencia mac80211 posterior a la recuperacion.
- El watchdog restauro por vencimiento; una desautenticacion controlada recupero 5/5 pings.
- La fuente confirma NSS cero-based y palabra `0x21c08000`; causa interna UNKNOWN.
- No se repitio el override. Comparacion de agregacion a MCS bajo y H3 sin medir.

## H1 parcial: AQL aislado, MCS automatico

- Host cableado hacia receptor Loco: TCP downlink, cuatro flujos, buffers 16 KiB, ventanas 20 s.
- ICMP AP a Loco cada segundo; no son datos bidireccionales ni Triple-Play.
- Trafico RF contrastado con bytes del peer y receptor; Ethernet de Loco no explica la carga.
- A: cuatro AC 5000/12000 us. B: cuatro AC 1500/3000 us.
- Agregacion 3/64, override inactivo y `aql_threshold=24000` constantes, readbacks por ventana.
- Seis A/A nuevas y tres rondas A1-B1-A2-B2: 18 ventanas completas.
- Cuatro A/A de una pasada pausada por seguridad se conservan y no se mezclan.

| Mediana de ventanas A/B | A | B | Cambio B/A |
| :-- | --: | --: | --: |
| Goodput recibido Mbps | 63.968 | 64.115 | +0.229% |
| RTT p50 ms | 3.989 | 3.893 | -2.43% |
| RTT p95 ms | 7.366 | 9.345 | +26.88% |
| RTT p99 ms | 8.010 | 10.098 | +26.07% |
| tx duration / tx packets reportados, us | 2166.066 | 2165.790 | -0.0127% |

- A/A: goodput 62,602..64,120 Mbps; p95 7,478..13,826 ms.
- Tres pares A/A, cambio goodput -0,261..+2,096%; el +0,229% de B cabe dentro.
- Cambios p95 por ronda: +60,10%, -5,45%, +42,74%; no hay mejora consistente.
- Pings 359/360; la perdida unica fue en A/A, no en A/B.
- Minimos muestreados MemAvailable: AP 9312 KiB, CPE 3428 KiB.
- Sin nuevos crashes ni OOM en H1; sin pisos RAM numericos nuevos.

## Seguridad y cierre

- Revision detecto carrera entre comprobar ARMED y escribir: se pauso y restauro antes de B.
- Fuente reanudada: mismo `action.flock` que restore, adquisicion acotada y token pendiente.
- Dentro del bloqueo: propietario, boot, estado y vencimiento verificados antes de escribir.
- SHA256 revisado `4c5c392360ea23f671d3e36298c15dbc9f1ab57b3496546fdb20afcc8aa2e250`.
- Cierre: preimagen completa, 10/10 pings, procesos propios ausentes y boot sin cambio.
- `release` conserva auditorias: cuatro handles terminales archivados y quitados.
- Cuatro workspaces, cuatro handles y bloqueo global ausentes; cero escrituras en flash.

## Limites y decision

- Tres rondas y 20 pings/ventana: percentiles descriptivos, sin certificacion de cola extrema.
- us/paquete reportados no son fraccion fisica calibrada de airtime ni prueba de agregacion.
- Memoria muestreada, no minimo continuo ni piso portable.
- NO_GO de promocion; no trasladar a Panel2 ni afirmar fairness o H3.
- Uplink MCS0/1 opcional no ejecutado; no se reutilizo el perfil que produjo crash.
- Diez pruebas locales de integridad/tamper pasan: replay del recibo, no nuevas ventanas RF.
- Gate `artifacts/verification/wave394_lane1_h1_h3_gate.json`.
