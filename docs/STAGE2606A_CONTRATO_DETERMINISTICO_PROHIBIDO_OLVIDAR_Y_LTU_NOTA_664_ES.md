<!-- doc-head: Wave 261 (2604A-2609A) nota 664 ES: contrato deterministico de reglas prohibidas de olvidar en hook, AGENTS.md, CURRENT_STATE y doc 2594A, y contrato del banco LTU-Lite .110 -->
Un verificador (2604A) falla cerrado si alguna de las 9 reglas falta en alguno de los 4 portadores o si un sitio cambia de octeto.
Hoy pasa 9 de 9 en los 4; AGENTS.md quedo en 5990 bytes y CURRENT_STATE en 195 lineas.
LTU-Lite .110: alcanzado en vivo en 2473A solo con sysctl en RAM restaurado; el snapshot calibrado sigue BLOQUEADO (1135A).
Contrato de texto: no se sondeo ningun equipo, no hay medicion nueva ni campeon; tablero :8787 banda 1536A..2609A HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #664: contrato deterministico anti-amnesia y banco LTU-Lite .110

**Wave 261 - Etapas 2604A-2609A - 2026-10-28 - trabajo 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se construyo `tools/verify/enforce_prohibited_to_forget_contract.py` (2604A). Lee como texto cuatro portadores: el hook
PreInvocation de agy (nunca se importa ni se ejecuta), AGENTS.md, docs/CURRENT_STATE.md y el doc STAGE2594A. Una regla
cuenta como presente solo si todas sus palabras clave aparecen en la misma linea. El recibo guarda booleanos, numeros
de linea, ultimos octetos y huellas SHA-256; nunca copia texto de los portadores, asi que no arrastra nombres ni IPs
completas.

Titular honesto: **es un contrato de texto**. Prueba que las reglas estan escritas igual en los cuatro lugares; no prueba
que el admitidor, el demonio o el stack Site-Aware esten corriendo en ningun equipo.

## Las 9 reglas y donde estaban antes

| Regla | Antes de la wave | Ahora |
| :--- | :--- | :--- |
| R01 admitidor hibrido fijo siempre | faltaba en CURRENT_STATE y 2594A | 4 de 4 |
| R02 demonio Antes/Despues en SQLite | faltaba en AGENTS, CURRENT_STATE y 2594A | 4 de 4 |
| R03 Site-Aware / Peer-Buddy + fmx_site_neighbors.json + Prometheus/Grafana/Kuma | faltaba en AGENTS, CURRENT_STATE y 2594A | 4 de 4 |
| R04 banco LTU-Lite .110 | solo en el hook | 4 de 4 |
| R05 PtP-Colo .62 / .54 | faltaba en AGENTS | 4 de 4 |
| R06 Panel1 .84 | 4 de 4 | 4 de 4 |
| R07 Panel3 .83 | faltaba en AGENTS | 4 de 4 |
| R08 Panel2 .82 | faltaba en hook y AGENTS | 4 de 4 |
| R09 tablero :8787 | faltaba en AGENTS | 4 de 4 |

Ademas el verificador exige el mismo octeto por sitio en los cuatro: Panel1 .84, Panel3 .83, Panel2 .82, PtP-Colo .62 y
LTU-Lite .110. Presupuestos: AGENTS.md menos de 6000 bytes y sin CR; CURRENT_STATE.md y el doc 2594A menos de 220 lineas.

## Cambios en los portadores

- Hook: se agrego .82 a Panel2 en dos lugares; nada mas.
- AGENTS.md: estaba en 5959 bytes. Las reglas entraron en la fila anti-amnesia existente con enlace al verificador, mas
  .82 y .83 en la linea de topologia. Para pagarlo solo se quitaron comillas invertidas decorativas y se cambio el simbolo
  LaTeX de doble flecha por `<->`; queda en 5990 bytes, la linea 21 sigue con allow_80211 y todos los enlaces previos
  siguen.
- CURRENT_STATE.md: la seccion final suma una linea por regla y el verificador; las lineas 1 a 179 no cambiaron; 195
  lineas.
- Doc 2594A: nueva seccion "Reglas prohibidas de olvidar"; 119 lineas; el gate 2597A sigue en verde.

## Contrato del banco LTU-Lite .110

- 1023A: observacion pasiva de contadores nativos, sin escrituras de configuracion, sin acceso a nodos de dispositivo
  propietarios, sin carga.
- 1135A (27-10): **BLOQUEADO** - la clave provista fue rechazada, 0 snapshots, nada escrito.
- 1145A: auditoria offline de los scripts que podrian tocar /dev/ame*: COMPLIANT, 0 violaciones.
- 2473A (28-10): .110 fue el tercer host de un ciclo A1-B1-A2-B2 en RAM: tcp_keepalive_intvl 75 -> 60 -> 75, restaurado
  y verificado, RF estacionada, 0 escrituras de flash, 0 reinicios del driver ame. Sin carga, **sin efecto medido**.
- Reglas del banco: solo sysctl en RAM con restauracion verificada y watchdog; cero escrituras a /dev/ame*; RF estacionada
  salvo una corrida de RF autorizada aparte; el snapshot calibrado va antes de cualquier afirmacion sobre LTU.

## Advertencias del hook (informadas, no editadas)

- Panel3 dice "rts=512 + AQL Champion": el 2534A hizo un solo ciclo RTS 512 revertido, sin escritura persistente; no hay
  campeon.
- Panel3 dice "0% DUP": ninguna fuente cuenta respuestas DUP (nota #663).
- Cita una etapa 2598A para el LTU: no existe ningun artefacto con ese numero.

## Etapas 2605A a 2609A

- 2605A: nota evergreen #664 creada; `hyperresearch sync` (1 agregada) e `hyperresearch index build` devolvieron 0. El
  tablero se reconstruyo hasta la banda 2609 y responde HTTP 200 con la banda nueva y 0 apellidos en la pagina.
- 2606A: este documento y la seccion final de CURRENT_STATE.md.
- 2607A: dos claims en MemoryMaster (project:futuramax) y filas CRLF en results.tsv.
- 2608A: suite pytest tests/test_stage2604a_2609a_prohibited_to_forget_gate.py con pruebas negativas.
- 2609A: gate tools/verify/verify_stage2609a_gate.py -> artifacts/verification/stage2609a_wave261_opus2_gate.json.

## Aclaraciones del pedido

- El pedido nombra tools/command_center/serve_command_center_8787.py; no existe. El :8787 lo sirve
  tools/serve_command_center_live.py (ya corriendo) y la banda vive en tools/build_command_center_html.py. No se creo
  ningun servidor nuevo.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin ninguna medicion nueva en esta wave; no se abrio ningun binario.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteo de PII.

## Que sigue (decision del operador)

- Decidir si se corrigen las tres advertencias del hook.
- LTU-Lite .110: conseguir acceso valido para el snapshot calibrado antes de cualquier campana con carga.
- Sondear en vivo, con autorizacion, que el admitidor, el demonio y fmx_site_neighbors.json esten activos.

Recibos: `stage2604a_prohibited_to_forget_contract_receipt.json`, `stage2605a_command_center_1536a_2609a_refresh_receipt.json`,
`stage2607a_memorymaster_ingest_receipt.json`, `stage2609a_wave261_opus2_gate.json`.
