<!-- doc-head: W432 PARTIAL confirmado por corte explicito del operador -->
NAT de gestion guardada en .110 y SSH RF a Rocket114 verificado con origen110 real.
No se acepta objetivo de dos estaciones ni ROCKET LISTO PARA LLEVAR.
Medicion y pendientes pasan a W441; no se reclaman nuevos ensayos de arranque.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W432: cierre parcial autorizado

Autoridad de cierre: `<orca-id>`. Gate: `artifacts/verification/wave432_lane4_ltu_ptmp_gate.json`.
Evidencia completa y fallos conservados: `artifacts/autoresearch/wave432_ltu_ptmp.json`.

- Rocket stock2.1.0 AP FMX-LTU NONE/20MHz, IP114 guardada; Lite1 stock2.4.0 asociada.
- .110 conserva LAN110 y WAN75. Alias propio110/32 y ruta114 por WAN quedaron guardados.
- Tras reboot AP, la NAT MASQUERADE impedia gestionar114 con retorno correcto. El alias AP254 temporal habia ocultado esa dependencia.
- Una excepcion NAT exclusivamente src110/dst114/outbr0 restauro SSH; la Rocket observo TCP desde110.
- Excepcion insertada antes del launcher en el RC, guardado nativo y bancos/archivo/permisos/protegidas verificados. SSH RF fresco confirmado.
- No se realizo reboot de la ultima correccion NAT: el operador ordeno cortar y medir.
- Lite2 no recibio preambulos durante el ensayo nativo, aun con campos de radio comparados iguales. Causa fisica no confirmada.
- Su guardia restauro System/hook originales y acceso55; se verificaron bancos y protegidas. Esa restauracion precede la nueva orden de banco persistente.
- Guardado final de Lite2 como CPE de banco y promocion de alias/rutas LAP/Loco quedaron pendientes por corte explicito.
- Alias de control LAP/Loco retenidos con TTL; no se afirman persistentes. Sesion cerrada sin restaurar los cambios confirmados.
- Sin flash de firmware ni acceso a produccion/PowerBeam. Sin benchmark W432; W441 es el siguiente trabajo.
- No declarar **ROCKET LISTO PARA LLEVAR**: falta la segunda Lite y la aceptacion completa.

El gate prematuro historico permanece archivado en `STAGE3092A_premature_gate_snapshot.json`; no fue el cierre aceptado.
