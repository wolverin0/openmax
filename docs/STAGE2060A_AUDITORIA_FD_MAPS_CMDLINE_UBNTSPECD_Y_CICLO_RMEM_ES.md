<!-- doc-head: Wave 170 (2058A-2063A) carril 3. Auditoria 100 por ciento solo-lectura del proceso ubntspecd en 6 radios (Panel1 .84 OpenWrt, Panel2 .82 y Panel3 .83 airOS WA, banco .198/.253 XC, .110 LTU): cmdline, descriptores abiertos, maps, estado y config airview/spectral. Todos tienen los mismos archivos abiertos (incluido /dev/uph_wifi0); lo unico que separa a los activos (.198/.82/.83, opcion -a, 100 a 130 despertares/s) del quieto (.253, opcion -g, 2/s) es la opcion de arranque, confundida con la version de firmware. Mas un ciclo finito rmem_default/tcp_fin_timeout en RAM. -->

# Stage 2060A: fd, maps y cmdline de ubntspecd, y ciclo rmem

## 1. Alcance y seguridad

Carril 3, hardware real. 2058A fue solo lectura en los seis radios: cada comando pasa la guarda
`assert_read_only` de produccion, no se mando ninguna senal a ningun proceso y no se escribio nada. De
`/tmp/system.cfg` solo se leyeron las lineas `airview` y `spectral`, que no llevan credenciales. De los
sockets se guardo puerto y estado, nunca la direccion remota. En 2059A solo se escribieron sysctls en
RAM con watchdog de 60 s. Cero Flash, cero RF, cero canal, cero GPIO, cero atpc.

## 2. Que se leyo (2058A)

Por cada proceso ubntspecd: `/proc/<pid>/cmdline`, `ls -l /proc/<pid>/fd`, `/proc/<pid>/maps`, estado,
hilos, memoria, cambios de contexto y `wchan`; estado repetido 10 s despues para medir actividad. Del
sistema: tablas de sockets para resolver los inodos, modulos cargados, md5 del binario, la cadena de
opciones (getopt) que acepta el binario, y las IRQ y softirq en la misma ventana.

## 3. Huella del proceso

| Radio | Firmware | Opcion | Despertares/s | IRQ radio/s | Abiertos |
| :-- | :-- | :-- | :-- | :-- | :-- |
| .198 XC | 8.7.25 | -a | 129 | 608 | /dev/uph_wifi0, /dev/null, pipe, TCP 50841, 1 socket |
| Panel2 .82 | WA 8.7.25 | -a | 112 | 2839 | igual |
| Panel3 .83 | WA 8.7.25 | -a | 100 | 3181 | igual |
| .253 2XC | 8.7.11 | -g | 2 | 53 | igual |
| Panel1 .84 | OpenWrt 24.10.4 | no corre | - | 134 | - |
| .110 LTU | afltu 2.4.0 | no corre | - | 0 | - |

Linea completa en los activos: `/bin/ubntspecd -w -t -a -i wifi1 -j airview1 -m 4 -f 20 -s 200`. En
`.253` es la misma linea con `-g` en lugar de `-a`.

Lo que es igual en los cuatro radios airOS: los descriptores abiertos, el puerto TCP 50841 en escucha,
las 5 librerias mapeadas, el `wchan` (`poll_schedule_timeout`) y los modulos `ath_spectral`,
`ubnt_poll_host`, `umac`, `asf` y `ubnthal`. El demonio habla con la radio por `/dev/uph_wifi0`, el
dispositivo de `ubnt_poll_host`. Esto encaja con lo de 2016A: es trabajo de consulta a la radio, no la
IRQ spectral.

## 4. Por que .253 esta quieto

El unico campo que separa a los tres activos del quieto es la opcion de arranque: `-a` contra `-g`.
Ambos binarios aceptan las dos opciones (misma cadena getopt `ab:B:c:f:gHhi:j:m:o:s:Ttu:n:w`), aunque
el md5 es distinto. Ningun script de texto en `/etc` o `/usr/etc` nombra a ubntspecd, asi que lo lanza
un binario del firmware.

Limite: la opcion y la version de firmware van juntas (todos los `-a` son 8.7.25, el unico `-g` es
8.7.11). Con estos datos no se puede separar si la carga viene de la opcion o de la version del
binario. Para separarlo habria que relanzar el demonio con la otra opcion en un radio de banco, una
escritura que esta wave no hizo.

Config: `airview.status=enabled` aparece en Panel2 y Panel3. En Panel1 OpenWrt tambien aparece,
como resto de su firmware anterior, sin demonio que lo use. En el banco no hay lineas airview.

Durante la auditoria el enlace de produccion `.84` siguio sano (cpe_41 p95 34,1 ms, cpe_223 23,6 ms,
cpe_80 en MCS6 sin perdida). Es solo control de salud.

## 5. Ciclo finito de 3 iteraciones (2059A, STOP_MAX_ITERATIONS)

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 XC | net.core.rmem_default | 131072 -> 163840 -> 131072 | 0,01 Mbps | 13,9 ms | 0,720 | keep |
| 2 | .253 XC | net.ipv4.tcp_fin_timeout | 15 -> 30 -> 15 | 0,01 Mbps | 28,4 ms | 0,894 | discard |
| 3 | .110 LTU | net.core.rmem_default | 163840 -> 131072 -> 163840 | 1,98 Mbps | 18,4 ms | 0,696 | keep |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. El `.253` tiene
`tcp_fin_timeout` en 15, no en el 60 tipico de los otros radios. Son knobs de sockets de gestion: el
ciclo prueba escritura y restauracion seguras, y keep o discard refleja el trafico ambiente de `.84`,
no el knob. cpe_80 se mantuvo en MCS7 sin perdida.

## 6. results.tsv

Se agregaron 3 filas finitas `s2059a_iter1_198`, `s2059a_iter2_253` y `s2059a_iter3_110`. Las
filas de waves anteriores quedaron intactas y el encabezado sigue siendo unico.

## 7. Verificacion

2058A y 2059A pasan `enforce_5pillar_research_gate.py --opus55-strict --require-live-hardware` sin
senales de juego. En 2058A las rondas A1 a B2 son las de la medicion paralela de `.84` (A=cpe_41,
B=cpe_223), no una intervencion. Pilar E: claims FMX-2058A y FMX-2059A en MemoryMaster. Sin workers
codex: la suite `tests/test_stage2058a_to_2063a_suite.py` y el gate
`tools/verify/verify_stage2063a_wave170_opus1_gate.py` los escribio y corrio el carril.
