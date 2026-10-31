<!-- doc-head: W455b Panel3 UISP: diseno ABAB (OFF,ON,OFF,ON,OFF, bloques de 30 min) y regla preregistrada sobre medianas de bloque, perdida y tasa de picos contra la variacion OFF-vs-OFF; regla congelada por sha256, evaluador offline y secuencia de lanzamiento con abortos y rollback -->
Pregunta: el pico de 43,4 ms de W455 fue efecto del bridge o ruido del camino con perdida de fondo.
Respuesta de diseno: alternar bridge OFF/ON y medir si el efecto se repite en cada bloque ON.
Estado: regla congelada y evaluador probado offline; NADA ejecutado contra radios en esta etapa.
Regla: artifacts/autoresearch/wave455b_rule.json. Evaluador: tools/uisp_bridge_openwrt/wave455b_evaluator.py.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 3122B: W455b, ABAB del bridge UISP en Panel3

El NO_GO de W455 se conserva tal cual; W455b es un experimento nuevo y nunca lo convierte en PASS.

## Huella de la regla (congelada antes de cualquier corrida)

- sha256 canonico: `fadd4b2324347cedfe9cae4f0f50e977e7570676568bc00bfab41d49876ef7e1`
- Metodo: sha256 de `json.dumps(regla, sort_keys=True, separators=(',',':'), ensure_ascii=False)`; no depende de saltos de linea.
- Calculo: `python -m tools.uisp_bridge_openwrt.wave455b_evaluator --print-sha`.
- El evaluador y el runner rechazan la regla si el sha no coincide; el recibo guarda el sha antes de activar nada.

## Diseno

| Bloque | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Bridge | OFF | ON | OFF | ON | OFF |

- Cada bloque analiza 30 minutos completos del sidecar core: 150 min de analisis, unas 2,8 h con transiciones.
- Fuente de 30 min y minimo OFF,ON,OFF,ON: despacho del orquestador. El quinto bloque OFF es decision de diseno: da tres OFF para medir el rango OFF-vs-OFF y encierra a cada ON en el tiempo.
- Mismas sondas que W455: `fmx_sidecar_e2e_minute`, nodo `panel3_ap`, origen `core`, 6 pings por minuto (collector.py, CORE_SOURCE).
- Ventana: primer limite de minuto posterior al evento (ON: primera lectura UISP aceptada; OFF: lectura final con servicio OFF). Igual que `first_core` de W455.
- Las transiciones (staging, preflight, restore) quedan fuera por evento, no por una constante de tiempo.
- Observacion simetrica: los ON sondean el AP por SSH cada 45 s (W455, `sleep(45)`); los OFF hacen una lectura solo-lectura al mismo ritmo. En el A/A de W455 no se sondeaba.

## Estadisticos por bloque

1. Mediana del p95 por minuto (metrica primaria de W455).
2. Mediana del p99 por minuto (con 6 pings por minuto el p99 es casi el maximo del minuto).
3. Perdida: 1 - recibidos/enviados del bloque. Es tasa y no mediana: la mediana de perdida por minuto es 0 casi siempre y no verifica nada.
4. Picos: minutos con p95 > S. Un minuto sin respuestas cuenta como pico.

S = Q3 + 1.5 IQR del p95 por minuto de todos los bloques OFF de ESTA corrida (cuantiles por interpolacion lineal). Fuente: Tukey 1977, Exploratory Data Analysis, valla superior; el 1,5 es la convencion publicada y no se ajusta. S sale de la distribucion OFF propia, no es un numero nuevo en ms. Es intramuestral para los OFF, lo que sesga contra el bridge (conservador).

## Regla de decision

- Cota por estadistico: `mediana(OFF) + rango(OFF)`, con rango = max(OFF) - min(OFF), la mayor diferencia OFF-vs-OFF medida en la misma corrida. Fuente: datos de esta corrida; sin piso ni cuanto agregado.
- Un bloque ON es adverso en un estadistico si lo supera de forma estricta.
- NO_GO: algun estadistico es adverso en TODOS los bloques ON (el efecto se repite).
- INCONCLUSIVE: hay adversos pero en ninguna metrica en todos los ON (el patron de W455: un evento de cola aislado). No pasa a PASS: se repite o se detiene.
- PASS: ningun bloque ON supera la cota en ningun estadistico.
- INVALID: sha de regla, cantidad u orden de bloques, solapes, minutos faltantes o con hueco, sent distinto de 6, series de otro nodo, o evidencia obligatoria ausente. Falla cerrado y cuenta como NO_GO para produccion.
- Si todos los OFF tienen 0 perdida o 0 picos, cualquier perdida o pico en un ON es adverso (misma dureza que W455: sin aumento de perdida).
- El informe incluye `minimum_detectable_effect` = rango OFF-vs-OFF: un PASS no excluye efectos menores.

## Ilustracion piloto con datos de W455 (no es evidencia de W455b)

| Dato | Valor |
| --- | --- |
| Mediana p95, OFF 15 min posteriores al corte (estabilidad / A/A) | 15,64 ms / 21,10 ms |
| Diferencia OFF-vs-OFF en bloques de 15 min | 5,46 ms |
| Efecto del candidato en W455 (mediana 20,09 vs 21,10) | -1,02 ms |
| Valla S sobre esos 30 min OFF | 39,11 ms |
| Picos sobre la valla: antes del corte / ON primera mitad / ON segunda mitad | 1 / 1 / 0 |

Lectura: la variacion OFF-vs-OFF es mayor que cualquier efecto medido; la banda sera ancha. Eso dicen los datos y se informa tal cual.

## Seguridad conservada

- Certificado, jail, allowlist RPC y negativas 6 de 6 (`_DENIED_126`): sin cambios, vienen del `run_stage` de W455.
- Parada de MemAvailable < 2048 KiB. Fuente: STAGE2896A linea 111 (thrash y fallas de fork bajo unos 2 MiB) y <orca-id> (alcance W455). Reusarlo en W455b requiere la autorizacion del operador (`--authority-ref`).
- Guarda compartida de 600 s (`fmx_watchdog.sh`, sha 2a125d4e...074f), renovada en cada lectura.
- Rollback persistente: `lease.sh restore` tras CADA bloque ON, pase o falle; init original 01e227a3...23bed, servicio y autorun OFF, verificado por lectura.
- Esperas heredadas de W455: arranque 180 s, aceptacion inicial 600 s, recoleccion 2040 s = 60 + 1800 + 180.
- Perdida y latencia son resultados, no abortos.

## Origen del runner

El runner de W455 no existe como archivos: son cadenas dentro de `wave455_panel3_uisp_acceptance.json`.
`wave455b_abab.py` verifica el recibo y cada fuente contra sus sha256 y las ejecuta sin cambios (run_stage, monitor, lease).
Lo nuevo: bucle de bloques, sham poll OFF, restore tras cada ON y monitor sin el criterio A/A.
El recibo W455b se siembra solo con la calificacion estatica de W455; los msg_ de autoridad copiados son los de W455.

## Lanzamiento (el operador ejecuta; nada se lanzo)

Plan sin SSH:

`python -m tools.uisp_bridge_openwrt.wave455b_abab --rule-sha256 fadd4b2324347cedfe9cae4f0f50e977e7570676568bc00bfab41d49876ef7e1`

Corrida real (unas 3 h, sin otra tarea sobre Panel3):

`python -u -m tools.uisp_bridge_openwrt.wave455b_abab --rule-sha256 fadd4b2324347cedfe9cae4f0f50e977e7570676568bc00bfab41d49876ef7e1 --execute --authority-ref <id-de-mensaje-del-operador>`

Evaluacion offline:

`python -m tools.uisp_bridge_openwrt.wave455b_evaluator --rule-sha256 fadd4b2324347cedfe9cae4f0f50e977e7570676568bc00bfab41d49876ef7e1 --out artifacts/verification/wave455b_abab_gate.json`

Secuencia: pines locales, politica UISP y lectura OFF (uptime >= 1800 s), OFF1, ON1 (run_stage de W455), OFF2, ON2 (segunda mitad de run_stage), OFF3, lectura final OFF.

## Abortos y rollback

- Cualquier require del monitor de W455 menos el criterio A/A: boot, memoria, guarda, negativas, init, archivos protegidos, identidad, UISP perdida, hueco del sidecar.
- Bloque OFF: servicio o autorun no verificados OFF, boot distinto, memoria baja, hueco del sidecar.
- Ante un aborto: `lease.sh restore`, recibo `ABORTED_*`, el evaluador devuelve INVALID. Si el runner muere, la guarda de 600 s restaura sola.
- Cierre esperado: init original exacto, servicio y autorun OFF, handle y runtime propios eliminados.

## Limites sin resolver

- Con 3 OFF el rango es una estimacion de pocos grados de libertad; es el costo de pedir bloques de 30 min.
- Deriva horaria y de trafico durante 3 h no se controla; se informa el rango OFF como techo de resolucion.
- Las ordenes remotas nuevas (lectura OFF, restart del segundo ON) se probaron solo con simulacion; son lecturas o copias de pasos de W455.
- La autoridad de W455 (<orca-id>) cubria solo esa ejecucion: W455b depende de la referencia del operador.

[Regla congelada](../artifacts/autoresearch/wave455b_rule.json).
[Recibo W455](../artifacts/autoresearch/wave455_panel3_uisp_acceptance.json). [Gate W455](../artifacts/verification/wave455_lane1_panel3_uisp_gate.json).
