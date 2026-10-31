<!-- doc-head: Wave 376, costo fisico de coverage class 0 frente a 6 en banco PtMP -->
X-CC1 detenido en AA1 por RAM de la Loco; clase 0 y preimagen restauradas. Costo UNKNOWN.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Costo de coverage class en un enlace corto

**NO_GO: aborto de seguridad durante la primera carga A/A por memoria de la Loco.**
Costo clase 0 vs 6: UNKNOWN; cero ventanas completas y ninguna aplicacion de clase 6.
No habilita cambios en Panel1, Panel2, Panel3 ni otros equipos de produccion.

## Alcance y protocolo fijado antes de medir

- AP LAP-120 198.18.0.43 y Loco 198.18.0.47; identidad SSH fijada.
- La misma Loco tiene 198.18.0.67 sobre su bridge inalambrico.
- El controlador autorizo ese endpoint y un presupuesto de 200 minutos.
- A = clase 0; B = clase 6 en ambos extremos, mediante iw y solo en RAM.
- A/A primero; detener si el goodput difiere al menos 2% o el p95 al menos 5%.
- Si el A/A pasa: tres bloques A1-B1-A2-B2, 120 s de asentamiento y 600 s de carga por fase.
- Cuatro flujos TCP por direccion simultanea; goodput agregado = DL + UL.
- Ping AP a la direccion aerea de la Loco cada 200 ms durante la carga.
- Readback de clase, canal, ancho, potencia, AQL/FQ/BQL y firmware fijo.
- Piso de MemAvailable de 5120 KiB en ambos equipos; detener si hay crash,
  desasociacion, rechazo de clase, aumento de fq_overmemory o perdida de ventana >5%.
- Watchdog compartido de 45 s por equipo, renovado cada 10 s; preimagen clase 0.
- Alias y reglas NAT privadas del AP permiten entrada Ethernet del TCP desde el host.
- El AP no ejecuta iperf3. La Loco es el endpoint TCP, no un servidor externo cableado.
  Es la adaptacion aprobada del esquema W372; puede incorporar costo de CPU de la Loco.
- Se contrasta el caudal TCP con los contadores nativos TX/RX de la estacion aerea.
- No se modifican colas, RTS, potencia, firmware, UCI, flash ni persistencia.

## Interpretacion estadistica

Hay tres bloques independientes, no miles de pings independientes.
La permutacion bilateral exacta con n=3 tiene p minimo 0.25;
Sidak para dos hipotesis a 0.05 da alfa ajustado 0.0253206.
Por ello, aun completando las ventanas, no se demuestra formalmente no inferioridad.
Los margenes descriptivos previos son goodput >= -2% y p95 <= +5%.
El coordinador aprobo ejecutar y reportar INCONCLUSIVE sin aumentar n ni cambiar margenes.
Esta prueba corta mide costo; no demuestra beneficio ni alcance en enlaces largos.

## RTS y limite de evidencia

La salida completa de iw no muestra RTS threshold en los dos equipos.
RTS apagado se interpreta como INFERRED: [iw 6.9](https://kernel.googlesource.com/pub/scm/linux/kernel/git/jberg/iw/+/refs/tags/v6.9/info.c)
omite el valor UINT_MAX y [nl80211 Linux 6.12](https://raw.githubusercontent.com/torvalds/linux/v6.12/net/wireless/nl80211.c)
emite ese atributo. No se obtuvo el arbol compilado exacto porque WSL fallo;
no se reinicio WSL ni se escribio RTS para convertir esa inferencia en una afirmacion mayor.

## Trazabilidad

El recibo conserva fuente ejecutada, SHA256, identidad, ventanas, lecturas y restauracion.
El primer intento excedio el limite de salida SSH leyendo dmesg de la Loco.
No genero carga: se restauro clase 0 y se comprobaron colas y temporales propios.
Se conserva integro como intento 1; el segundo acoto dmesg a sus ultimas 120 lineas.
La fuente ejecutada del segundo intento queda congelada por SHA256 en el recibo.

## Resultado real y restauracion

- La segunda ejecucion comenzo a las 10:50:04 UTC del 30/10/2026.
- Tras los 120 s de asentamiento, TCP bidireccional inicio a las 10:52:12 UTC.
- MemAvailable antes de carga: AP 6284 KiB, Loco 7744 KiB.
- Primera lectura del AP con carga: 6284 KiB; la siguiente validacion de la Loco
  disparo `MEMORY_BELOW_5120`. No se completo siquiera AA1 ni se evaluo estabilidad A/A.
- Se cerro la carga inmediatamente y el receptor iperf3 termino. No se reinicio el ensayo.
- **Limite de trazabilidad:** el chequeo precedia a guardar la muestra fallida.
  Por ello se conoce el limite `<5120 KiB` y el equipo por el orden y traceback,
  pero el valor exacto observado no quedo conservado: es null, no un minimo inventado.
- La caida al iniciar iperf3 es temporalmente compatible con buffers/sockets de la Loco;
  su causa no fue aislada. No se atribuye a coverage ni se afirma una regresion de clase 6.
- Ambos equipos: clase 0, mismo boot, colas originales, rc.local y firmware sin cambios.
- Dos rondas frescas solo lectura confirmaron la restauracion y ausencia de iperf3.
- AP: MemAvailable 6284 / 6288 KiB; Loco: 8024 / 10068 KiB en esas rondas.
- NAT y alias propios retirados; handles, directorios y lock propios eliminados.
  Los archivos ajenos que ya existian en /tmp no se tocaron.
- El gate CONFIRMED acredita el aborto y la restauracion; **no** certifica no inferioridad,
  costo de coverage, A/A estable, 12 ventanas A/B ni autorizacion para produccion.
- Proximo paso propuesto: endpoint cableado externo en el lado CPE y registrador que
  conserve la lectura antes de validarla; requiere otro protocolo aprobado. No se ejecuto.

- [Recibo de medicion](../artifacts/autoresearch/wave376_coverage_class_cost_ab.json)
- [Gate](../artifacts/verification/wave376_lane1_coverage_class_cost_gate.json)
- [Especificacion X-CC1](STAGE3029A_COVERAGE_CLASS_PTMP_ES.md)
