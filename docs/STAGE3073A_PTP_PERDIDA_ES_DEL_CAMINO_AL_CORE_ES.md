<!-- doc-head: Stage 3073A (W413) ES: los 3 PtP marcados con perdida en W412 no pierden por su radio; la perdida es de modo comun en el camino oficina → core (cpu0 del RB1100AHx4 al 100 % y rx-drop en todos sus puertos, o el UTP RB4011→RB1100), con cifras de origen oficina y arreglos rankeados -->
Que cubre: 60 min de sidecar, 3 pings de control a 1/s, airOS de las 6 puntas (2 pasadas), CPU y descartes del core; separa RF, congestion y Ethernet.
Estado: solo lectura. 0 escrituras en equipos. Cifras de perdida y latencia = origen oficina (aviso del operador).
Datos maquina: artifacts/autoresearch/wave413_lossy_ptp.json. Informe visual: artifacts/2026-10-30-ptp-con-perdida.html.
Leer cuando: antes de culpar a un PtP o panel por perdida medida desde la oficina, y al preparar W414.
<!-- /doc-head -->
# Stage 3073A: PtP con perdida, la perdida es del camino al core (W413)

## 1. Hallazgos

- **F1 CONFIRMED** (external controller (core RB1100AHx4) o el tramo UTP oficina→core: no separables desde este origen): La perdida es de modo comun. En 10 min a 1/s simultaneos, los 4 nodos de referencia del sitio del core (sin radio) perdieron 6.12 % y las 6 puntas PtP 5.0-6.5 %; exceso de cada punta contra la referencia con IC95 que incluye 0. El core mismo perdio 4.67 %.
- **F2 CONFIRMED** (external controller (core)): Los segundos perdidos coinciden con un nucleo del core al 100 %: perdida 36.4 % (c44af853) y 31.8 % (e0e0b1b6) en esos segundos contra 1.6-2.3 % fuera (Fisher p<=1e-4). En 2000 s de muestreo un nucleo estuvo al 100 % el 10.4 % del tiempo; minuto a minuto, Spearman segundos calientes vs perdida de red 0.317 (p 0.03895, 31 min).
- **F3 CONFIRMED** (external controller (core)): El core descarta en recepcion (rx-drop) en todos los puertos con trafico: WAN1 3.75 %, LAN sw-poe200 4.77 %, WAN2 3.75 %, LAN sw-poe201 4.15 %, WAN3 3.74 % en 60 s; por minuto el total fue 1.36-4.24 %. Contadores desde el arranque muestran millones de descartes previos al sidecar.
- **F4 CONFIRMED** (external controller (core)): /tool profile 10 s: cpu0 98.5 %, de eso el proceso alpine_sd 77.0 %. Sin regla fasttrack; 489 colas simples y 100 reglas mangle. Que es alpine_sd: UNKNOWN.
- **F5 INFERRED** (UNKNOWN (fuente periodica)): Las rafagas del core tienen un componente de ~70 s (autocorrelacion 0.171 contra 0.064 al azar); a 60 s es 0.022, asi que no es la lectura de colas del sidecar (cada 60.4 s; 14.5 % de segundos calientes junto a la lectura contra 9.5 % fuera: aporte menor). Fuente UNKNOWN.
- **F6 REFUTED** (medicion): La tabla de W412 que marcaba estos PtP como 'con perdida' y las diferencias por nodo del sidecar a 1 eco cada 10 s: a 1/s simultaneo no hay diferencia. La sonda de 10 s cae siempre en la misma fase y las rafagas del core no son aleatorias.
- **F7 CONFIRMED** (hardware/radios: sin descarte): En ~40 min, las 6 puntas descartaron 0-2 paquetes entre eth0 y ath0 (<=1,6 ppm), 0 errores inalambricos y ningun reinicio. La radio y su Ethernet no explican la perdida.

## 2. Por enlace (origen oficina)

| Par | Canal | Capacidad baj/sub Mbit/s | Aire AP/STA % | Señal dBm | Ruido dBm | Salto radio p95 ms | Perdida 1/s AP/STA % |
| :-- | :-- | --: | --: | --: | --: | --: | --: |
| A | 10 MHz, 2700 m | 60,8/26,0 | 40,8/44,5 | -49/-48 | -93/-92 | 11,8 | 5,67/5,5 |
| B | 40 MHz, 300 m | 205,2/223,2 | 64,3/68,7 | -50/-46 | -93/-86 | -6,5 | 5,0/6,5 |
| C | 10 MHz, 2700 m | 62,4/41,6 | 1,5/1,4 | -50/-48 | -87/-90 | 2,8 | 5,33/5,67 |

- Salto radio = p95 de la STA menos el del AP por minuto (metodo W382). B da negativo: dentro del ruido de la sonda.
- ACK automatico activo en las 6 puntas. Exceso de perdida de cada punta contra la referencia: IC95 incluye 0 en las 6.

## 3. Arreglos rankeados

1. **toda la red, core / tramo oficina (infra)** (operador + infra, CONFIRMED sintoma, causa a separar): W414: mover el origen de las sondas al RB1100 para separar el UTP RB4011→RB1100 de la saturacion de cpu0; despues el dueño del core decide (identificar alpine_sd, reparto de recepcion por nucleo, ausencia de fasttrack con 489 colas). FuturaMAX no toca el core.
2. **PtP A (c44af853), config stock** (operador, INFERRED): Pasar de 10 a 20 MHz tras un airView en ambas puntas dentro de la banda legal: hoy techo 60,8/26 Mbit/s con aire 41-45 % y picos de uso de 0,58. Solo despues de que el core deje de perder.
3. **PtP B (e8eabc59), config stock** (operador, INFERRED): Aire 64-69 % llevando ~110-124 Mbit/s sobre 164-205: 80 MHz solo si un airView en ambas puntas lo permite.
4. **PtP B y A, fisico** (operador, INFERRED): B: señal 20 dB bajo lo que espera el equipo (-46/-50 contra -26) y ruido 7 dB mas alto en la STA: revisar alineacion u obstruccion (da margen, no velocidad: ya esta en MCS 8-9). A: la STA negocia Ethernet a 100 Mbps (puede ser el equipo del otro lado, mm 153307); hoy no limita.
5. **PtP C (9f29f65d), fisico** (operador, CONFIRMED medicion, baja prioridad): Enlace casi sin uso (aire 1,5 %); 7 dB de diferencia entre cadenas en el AP (-51/-58). Nada que arreglar por perdida.
6. **los 3 PtP, migracion OpenWrt** (lanes FuturaMAX, INFERRED): No ataca la causa medida. Solo con el core sano y re-medido, y con gate PASS de banco del cambio exacto (politica 30/10).

## 4. Limites

- Desde la oficina no se separa el UTP RB4011→RB1100 de la saturacion del core: lo resuelve W414 (origen en el RB1100).
- El componente de ~70 s y el proceso alpine_sd quedan UNKNOWN. El espectro de UISP no tiene unidad documentada: no se usa para elegir canal.
- Claves SSH de las 6 puntas registradas como OBSERVED_NOT_PREPINNED en el JSON.
