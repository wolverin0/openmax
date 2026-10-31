<!-- doc-head: Wave 174 (2082A-2087A) carril 3. La comparativa en vivo del modo -a contra -g de ubntspecd en el banco .198 (2082A) no se ejecuto en esta wave; queda como decision del operador. Correccion de 2058A: en .198 ubntspecd lo lanza init desde /etc/inittab (respawn), no un binario. Ciclo finito de 3 iteraciones wmem_default/tcp_keepalive_time en RAM en .198/.253/.110 con filas en las dos tablas de resultados. Leer antes de retomar la comparativa -a/-g o tocar el arranque de ubntspecd. -->

# Stage 2084A: modo -a contra -g de ubntspecd y ciclo wmem_default

## 1. Alcance y seguridad

Carril 3, hardware real. Ningun AP de produccion recibio escrituras. En el banco solo se escribieron
sysctls en RAM con watchdog de 60 s y relectura final del valor original. Cero Flash, cero RF, cero
canal, cero GPIO, cero atpc, cero knobs PROTECTED.

## 2. 2082A: la comparativa -a contra -g no se ejecuto

El plan era correr en el mismo radio (`.198`, XC 8.7.25) el modo de arranque `-a` contra `-g`, para
separar la opcion de la version de firmware, que en 2058A iban juntas. Esta etapa no se ejecuto en
esta wave: no hay herramienta, recibo ni captura de 2082A, y ningun recibo declara un resultado. Queda
pendiente como decision del operador.

Lo que si se obtuvo al preparar la etapa, solo leyendo `.198`:

- Correccion de 2058A: ubntspecd no lo lanza un binario. Lo lanza init desde `/etc/inittab` con la
  linea `null::respawn:/bin/ubntspecd -w -t -a -i wifi1 -j airview1 -m 4 -f 20 -s 200` (su padre es
  el pid 1). La busqueda de 2058A con `grep -r` no lo encontro, probablemente porque `/etc/inittab`
  se alcanza por un enlace. Consecuencia: si el proceso termina, init lo vuelve a lanzar con `-a`.
- Otras entradas `respawn` de init en `.198`: syslogd, iwevent, udhcpc, wpa_supplicant, dropbear,
  lighttpd, ubnt-gps-reader, udapi-bridge, udapi-server, ulogger, ustatsd e infctld.
- En `.198` hay un servidor iperf3 escuchando en el puerto 5201, previo a esta wave.

Referencia estatica de otro carril (Stage 2076A): en el binario, `-a` escribe 1 y `-g` escribe 0 en el
mismo campo de configuracion. Es analisis del binario, no una medicion en vivo.

## 3. Ciclo finito de 3 iteraciones (2083A, STOP_MAX_ITERATIONS)

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 XC | net.core.wmem_default | 131072 -> 163840 -> 131072 | 0,09 Mbps | 29,9 ms | 0,864 | keep |
| 2 | .253 XC | net.ipv4.tcp_keepalive_time | 7200 -> 3600 -> 7200 | 0,02 Mbps | 16,8 ms | 0,655 | keep |
| 3 | .110 LTU | net.core.wmem_default | 163840 -> 131072 -> 163840 | 0,10 Mbps | 26,9 ms | 0,870 | discard |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. Son knobs de
sockets de gestion: el ciclo prueba escritura y restauracion seguras, y keep o discard refleja el
trafico ambiente del enlace `.84`, no el knob. cpe_80 estuvo entre MCS6 y MCS7, sin perdida.

## 4. Tablas de resultados

- `artifacts/autoresearch/results.tsv` (tabla de 12 columnas con fmx_loss): 3 filas
  `s2083a_iter1_198`, `s2083a_iter2_253` y `s2083a_iter3_110`. Filas anteriores intactas, encabezado
  unico.
- `orchestration/autoresearch/results.tsv` (libro de etapas de 4 columnas, CRLF, sin encabezado, que
  llevan otros carriles): 3 filas `S2083A_ITER...` en su mismo formato, con knob, base, valor B,
  restauracion, fmx_loss y la ruta del recibo. Las filas de los otros carriles quedaron intactas.

## 5. Verificacion

2083A pasa `enforce_5pillar_research_gate.py --opus55-strict --require-live-hardware` sin senales de
juego. El gate `tools/verify/verify_stage2087a_wave174_opus1_gate.py` reporta 2082A como abandonada,
no como aprobada. Pilar E: claims FMX-2083A y la correccion del arranque en MemoryMaster. Sin workers
codex: la suite `tests/test_stage2082a_to_2087a_suite.py` y el gate los escribio y corrio el carril.
