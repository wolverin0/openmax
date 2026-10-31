<!-- doc-head: Wave267, meta acotada de ocho nodos y comparación válida de telemetría -->
La aceptación exige un mismo ciclo real, daemon vivo y una referencia histórica comparable.
Los errores y las referencias incompatibles permanecen explícitos; no se sustituyen por ceros.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Telemetría antes/después: ocho nodos y FQ overmemory

## Contrato congelado

La [prerregistración](../artifacts/autoresearch/stage2628a_wave267_preregistration.json)
fijó como máximo dos rondas y una fecha límite de 25 minutos o menos.
La meta exige simultáneamente daemon vivo, ocho nodos OpenWrt observados en un
mismo ciclo y al menos un porcentaje antes/después válido para L2 RF o core.
Una tabla con filas incompatibles o valores `null` no satisface esta última condición.

## Referencias históricas

La [auditoría de referencias](../artifacts/autoresearch/stage2629a_matched_reference_audit.json)
no encontró una pareja histórica válida. Las referencias stock de los CPE
terminados en `.41` y `.223` apuntaban a `198.18.0.132`; el core actual es
`198.18.0.2`. El sondeo L2 RF actual usa IPv6 link-local entre pares asociados.
Son recorridos distintos y no se intercambian sus nombres para calcular mejoras.
Además, no están ligados todos los detalles históricos de carga y algoritmo de cuantiles.

El monitor antiguo con 699 intervalos ya correspondía a OpenWrt. No constituye
una referencia stock ni prueba cobertura continua de 72 horas.
Los valores históricos pueden mostrarse como contexto descriptivo; su mera
presencia no habilita un porcentaje de mejora ni una afirmación causal.

## Identidad del octavo nodo

La [lectura autenticada](../artifacts/autoresearch/stage2628a/cpe80_documented_user_identity.json)
del equipo terminado en `.80` devolvió `WA.v8.7.25`, sin identificación OpenWrt.
Su autenticación está confirmada; su migración a OpenWrt no lo está.
Esta campaña no autoriza migrarlo y no lo cuenta como octavo nodo OpenWrt.

## Lecturas y límites

Las [rondas reales](../artifacts/autoresearch/stage2630a_wave267_rounds.json)
conservan instantáneas inmutables de cada ciclo y su proceso supervisor.
Ambas registraron siete nodos OpenWrt y el daemon vivo; ninguna tuvo una fila
antes/después válida. Se detuvo la campaña en `STOP_MAX_ROUNDS`, sin una tercera ronda.
El [diagnóstico](../artifacts/autoresearch/stage2631a_wave267_diagnostics.json)
documenta los errores y el estado de comparabilidad.
Los estados de error no representan latencia de cero ni pérdida cero.

`fq_overmemory` y `fq_overlimit` son nombres exportados por debugfs.
Las fuentes primarias revisadas muestran una inversión entre esos rótulos y
los campos internos. La correspondencia del backport exacto de los AP aún no
está confirmada: la atribución específica a presión de memoria queda `UNKNOWN`.
La revisión enlaza [debugfs de Linux 6.12](https://raw.githubusercontent.com/torvalds/linux/v6.12/net/mac80211/debugfs.c)
y la [implementación FQ de Linux 6.6](https://raw.githubusercontent.com/torvalds/linux/v6.6/include/net/fq_impl.h).
La versión de mac80211 leída en los AP fue `6.6.110.6.12.52-r1`.
Solo se calcula su incremento con dos muestras del mismo arranque, contadores
monótonos y un intervalo nativo conocido. La tasa por hora usa ese intervalo;
no convierte una lectura acumulada en un evento observado durante toda la vida del nodo.
La cola FQ global no demuestra aislamiento de memoria por CPE. Ninguno de esos
contadores se interpreta como bytes ni como denominador directo de pérdida de paquetes.
En la segunda ronda, Panel1 permaneció en 4055 eventos acumulados y Panel3 en
9062: ambos incrementos fueron cero durante intervalos nativos de 59,69 y
59,65 segundos, respectivamente. La primera ronda no tenía muestra previa:
su incremento permaneció `null`. Estos ceros conocidos no borran los eventos históricos.

Los sondeos RF identifican un segmento mínimo observado; no prueban el número
total de saltos enrutados. El ICMP desde el colector es extremo a extremo y
mantiene su recorrido distinto del sondeo remoto al core o del sondeo L2.

## Resultado verificable

El [gate de Wave267](../artifacts/verification/stage2633a_wave267_codex2_gate.json)
recalcula la meta a partir de las muestras, sin sumar nodos de ciclos distintos.
La identidad stock del octavo equipo y la ausencia de referencia comparable
impiden declarar la meta completa. El resultado es `PARTIAL`, aunque las pruebas
de integridad del recolector y del gate puedan pasar.

No se realizaron escrituras de configuración RF, migraciones ni cambios de canal.
La continuidad del proceso se certifica únicamente hasta la observación guardada;
no demuestra funcionamiento después de un reinicio sin sesión de usuario.
