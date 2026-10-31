<!-- doc-head: W466 reinicio semanal Guarida con permiso de un uso y comprobaciones A/B/C -->
Banco A/B/C y un reinicio soft confirmados; .116 liberada para W460, producción pendiente de revisión del Master.
Se conserva el límite KIT_ABSENT; Guarida sin cambios y recheck integral actual retenido por RAM del host.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W466: reinicio semanal protegido de Guarida

Estado: **BANCO A/B/C CONFIRMADO**, producción pendiente de revisión del Master.
Recibo: [wave466_night_restart_guarida.json](../artifacts/autoresearch/wave466_night_restart_guarida.json).
Gate: [wave466_lane1_night_restart_guarida_gate.json](../artifacts/verification/wave466_lane1_night_restart_guarida_gate.json).

## Autoridad y límites

El operador autorizó habilitar el cron semanal cuando los 16 nodos estén OBSERVED y estables durante 30 minutos.
El orquestador autorizó código nuevo en `tools/ops/fmx_night_restart/wave466/` mediante `<orca-id>`.
El runtime W458 se conserva byte por byte, SHA-256:
`5734f128d09b77f6cd1888f4bab6ee8dee9f4a5965c5b3b764765d49e91128bd`.
Se excluyen Colo, cambios RF, PoE, switches, archivos UISP y reinicios de producción durante la instalación.
El watchdog por fallas queda apagado y no se suprimen alertas del monitor ni Dude.

## Protecciones implementadas

- **A, freno encadenado:** sitio sano antes de la ventana; permiso SSH de un uso ligado a nodo, boot, minuto y preimagen; siguiente nodo solamente tras retorno, asociación, panel sano y postchecks. Fallo o ambigüedad cancela el resto de esa noche; no hay reintento ni recuperación tardía.
- **B, reloj:** consultas NTP nativas frescas, sysntpd habilitado y corriendo, TZ ART-3 y concordancia contra una consulta SNTP fresca desde el coordinador. Si falta cualquier evidencia se omite el reinicio. Kernel UNSYNC/TIME_ERROR/maxerror se conservan como diagnóstico, sin modificar bits. Perfil autorizado por `<orca-id>` y `<orca-id>`.
- **C, retorno:** compara cobertura/distancia, hashes de kits 99-fmx, estado y hash de clave UISP donde aplique, frecuencia/canal/ancho/DFS y asociación. Desajuste registra alerta y frena la cadena.

Los permisos se consumen en un journal durable antes de un único intento SSH.
No se instalan claves SSH en radios. El guard nativo no reinicia sin permiso válido.
La validación UTC del permiso evita un reinicio fuera de horario aunque la caché TZ de cron sea desconocida; esto no prueba la caché de cron y puede ocasionar un SKIP seguro.
La clave UISP y las MAC se comparan por hash; nunca se publican sus valores.

## Calendario objetivo y readback pendiente

Primer lunes previsto: **2026-11-02**, hora ART. Tabla de planificación; ninguna fila constituye readback de instalación.
Cada nodo debe verificar cron, enabled, reloj, kit/rol, próximo horario y `/etc/fmx-night-restart/snapshots`.

| Nodo | Hora ART | Instalación/readback W466 |
|---|---|---|
| cpe_200_169 | 03:10 | Pendiente |
| cpe_200_183 | 03:13 | Pendiente |
| cpe_200_213 | 03:16 | Pendiente |
| cpe_200_223 | 03:19 | Pendiente |
| cpe_200_41 | 03:22 | W458 deshabilitado según recibo previo; habilitación pendiente |
| cpe_200_80 | 03:25 | Pendiente |
| cpe_210_166 | 03:28 | Pendiente |
| cpe_210_21 | 03:31 | Pendiente |
| cpe_210_235 | 03:34 | Pendiente |
| cpe_210_238 | 03:37 | Pendiente |
| cpe_210_239 | 03:40 | Pendiente |
| cpe_210_83 | 03:43 | Pendiente |
| cpe_210_9 | 03:46 | Pendiente |
| panel1_ap | 03:49 | Pendiente |
| panel2_ap | 03:52 | Pendiente |
| panel3_ap | 03:55 | Pendiente |

## Coordinador y recuperación

El host utiliza Windows Task Scheduler, con el principal Limited de la tarea operativa existente.
La tarea propuesta empieza el lunes 02:40 ART para comprobar el sitio antes de emitir permisos.
No se registró ni arrancó todavía. Sin sesión operativa del principal no hay permisos y los radios omiten el reinicio.
El hook meteorológico está conectado pero deshabilitado hasta autorización separada.
Las copias de configuración se guardan bajo `/etc/fmx_rollback/`; no dependen de RAM tras reboot.
Se eliminan del cron las entradas antiguas del runtime y sus wrappers antes de habilitar el runtime base.
El instalador conserva sin reescribir el runtime aceptado de cpe_200_41 y verifica su hash.

## Evidencia y pendientes

Última suite completa ejecutada: **214 aprobadas**, JUnit `final_before_extra_authority_attempt22.xml` en `tools/ops/fmx_night_restart/wave466/`; es evidencia previa a los últimos cambios del lector host.
Regresiones del lector final: **31 aprobadas**, JUnit `readonly_receipt_completion_attempt25.xml`; la integración afectada de transporte/captura pasó 47 tests en `resume_probe_metadata_attempt23.xml`.
El recheck integral final no comenzó: el semáforo retuvo la ejecución por RAM libre de 1.1–1.8 GiB, por debajo del piso 2 GiB. No se declara PASS integral de la revisión actual.
Los primeros intentos fallidos permanecen en XML y recibo; los tests usan fixtures y no prueban comportamiento físico.
El ELF MIPS de reloj está compilado; no se presenta el ensayo WSL incompleto como aceptación nativa del radio.
El Master liberó .116 en `<orca-id>`. Las pruebas negativas de reloj y desajuste inyectan evidencia en archivos propios/copias y se etiquetan como tales.
La prueba positiva requiere cron real, boot nuevo, retorno asociado y snapshot coincidente; después .116 queda deshabilitado.
La prueba real terminó con un único reinicio soft y retorno asociado. No se repitió el reboot para completar evidencia.

El daemon se reanudó desde 17:25Z, tras el hueco real 16:30–17:25Z confirmado por el Master.
En .116 se observó UCI local sin el objeto ubus uci y dos radios configurados; se corrigió el descubrimiento para elegir por asociación netifd/interfaz activa.
Los CPE productivos cpe_200_183 y cpe_210_235 tienen el mismo modelo LiteBeam AC Gen2 pero ningún archivo 99-fmx en las rutas de persistencia consultadas; no hubo una fuente nativa byte-idéntica para copiar.
El Master autorizó en `<orca-id>` registrar KIT_ABSENT en ese caso: se comprueba ausencia antes y después, sin inventar ni instalar un kit RF.
La ausencia sólo es aceptable en el banco identificado; el instalador de producción sigue exigiendo prueba con hash 99-fmx real y revisión del Master.
El PC estaba unos 42 s atrasado frente a NTP; no se modificó su reloj global. Windows Time está detenido; el Master excluyó su reparación del alcance y autorizó usar el offset SNTP medido con anclaje monotónico para los permisos.
La tolerancia de reloj es menor a 60 s, derivada de la comparación HH/MM del runtime W458, líneas 191–199; el permiso además vence en su minuto exacto.
La prueba real de reloj alternativo pasó en .116. La denegación nativa sin permiso produjo SKIP y mantuvo el boot original.
La comprobación posterior al negativo detectó que `iw phy` imprime `5180.0 MHz`; se corrigió el parser y una captura completa real de sólo lectura pasó con 5180 MHz, 20 MHz y un peer asociado.
El arnés quedó deshabilitado, sin cron de prueba ni permiso publicados y con cero reinicios. El Master autorizó la reanudación adicional y las reparaciones aisladas de esta ronda mediante `<orca-id>`, conservando los recibos previos.
En .116 se configuró persistente ART3 con respaldo previo de system. No se alteraron network ni wireless, y los hashes protegidos coincidieron en los readbacks.
La duración estable exige también 1800 s de uptime creciente del mismo boot, además de timestamps y frescura.
La ventana se ancla a la última muestra fresca y se amplía hacia atrás si el uptime todavía no acredita 1800 s; no se redondea por jitter ni por el desfase del PC.
La última evaluación sigue retenida por muestras no OBSERVED en cpe_200_169 y cpe_210_21; el regreso general del sitio no sustituye esa comprobación individual.

## Cierre físico de .116

- A: sin permiso, el guard produjo SKIP; tras el permiso válido, la STA volvió asociada.
- B: negativos de TZ y ausencia de respuesta NTP denegados; positivo con NTP nativo y SNTP del host frescos. Kernel UNSYNC quedó registrado sin forzarlo.
- C: snapshot posterior igual en distancia/cobertura, canal, kits presentes/ausentes y UISP donde aplica; cambio inyectado en una copia produjo STOP_CHAIN y se recuperó su alerta real de logread.
- Reboot único: `<uuid>` → `<uuid>`.
- W458 registró `BENCH_ONCE` a las **16:35:51 ART**, dentro del minuto autorizado, en `snapshot.1`; la selección ya verifica ambos slots por nodo, boot anterior y minuto.
- El primer lector asumía slot 0; el recibo fallido se conserva. La terminación posterior fue sólo lectura, sin nuevo permiso/reboot ni cambio en código nativo. Se conservan por separado pins de ejecución original y de lectura corregida.
- Final: runtime y guard deshabilitados, sin permiso pendiente ni proceso NTP de consulta huérfano, TZ ART-3 y asociación activa. .116 queda liberada para W460.
- El límite KIT_ABSENT permanece explícito; no se certifica un hash 99-fmx inexistente ni readiness de los 16 nodos.

Resta revisión del Master antes de cualquier instalación en Guarida. El scheduler host y los 16 cron productivos siguen sin desplegarse.
