<!-- doc-head: Wave 167 (2040A-2045A) sintesis ES: nota #632 une Waves 158 (auditoria IRQ Guarida en vivo de solo lectura: IRQ espectral medida 1999.8/s en Panel2 y 3716.47/s en Panel3, 0/s en OpenWrt; ciclo finito dev_weight/netdev_max_backlog todo restaurado), 160 (request_threaded_irq explica la ausencia de request_irq; 4178 stores a 0x10), 162/164/165 (traza ioctl de ubntspecd: comando DESCONOCIDO; censo de constructores umac 4178 -> 26 -> 4, inicializador DESCONOCIDO); banda :8787 a 1536A..2045A; SIN campeon -->
# Reporte ejecutivo - Nota #632: auditoria de IRQ en Guarida y censo de constructores umac

**Wave 167 - Etapas 2040A-2045A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 10 recibos primarios de las Waves 158, 160, 162, 164 y 165 en la nota evergreen #632, se
regeneraron las paginas de indice del vault (research/index/*.md), el feed del Command Center :8787 se
amplio a 1536A..2045A y las tres docs maestras siguen en 179 lineas o menos con 0 apellidos del alcance.
Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda aplicado. La novedad
dura: la IRQ ath-spectral-filter, que la nota #631 solo podia nombrar, ahora tiene una **tasa medida en
vivo**. El comando ioctl de ubntspecd y el inicializador de priv+0x10 siguen DESCONOCIDOS.

## Wave 158 - auditoria de IRQ en Guarida (en vivo, solo lectura)

- stage1986A: 3 ventanas de 10 s, 0 escrituras de configuracion, sin login a ningun CPE de cliente.
  - Panel2 airOS 8: IRQ espectral **1999.8/s**, IRQ wifi 2347.17/s, CPU ocupada 20.25 %, softirq
    12.66 %, hardirq 1.55 %, ubntspecd 2.86 %.
  - Panel3 airOS 8: IRQ espectral **3716.47/s**, CPU ocupada 14.41 %.
  - Promedio de paneles airOS 8: 2858.13/s espectral, softirq 10.09 %, CPU 17.33 %.
  - Panel1 OpenWrt: **0 IRQ espectral**, sin ubntspecd, IRQ wifi 135.33/s, softirq 2.17 %, CPU 19.79 %.
  - Banco: XC .198 17.13/s y XC .253 25.03/s (ubntspecd corriendo), LTU .110 0/s (sin ubntspecd).
- Advertencias del propio recibo: los contadores de softirq son por tipo, no por origen, asi que la parte
  causada por la IRQ espectral **no es separable**; los paneles OpenWrt y airOS tienen estaciones y carga
  distintas, asi que el contraste **no es un A/B controlado**; ubntspecd no se detuvo.
- Esto reemplaza el "sin tasa medida" de la nota #631: los "1900 IRQs/s" de un pedido anterior no estaban
  medidos entonces; la cifra en vivo de Panel2 es 1999.8/s.
- stage1987A: ciclo finito de 3 iteraciones en RAM (A1 -> B1 -> A2 -> B2, parada por maximo de
  iteraciones): dev_weight 96 -> 64 en XC .198, netdev_max_backlog 768 -> 1024 en XC .253 y dev_weight
  64 -> 96 en LTU .110. Cada escritura tuvo efecto y **todas se restauraron**. El goodput es trafico
  ambiente del enlace .84 (0.026 a 0.083 Mbps), asi que **no se atribuye ningun efecto en el aire**.
  0 escrituras a flash, RF sin arrancar.

## Wave 160 - por que faltaba request_irq y el censo de stores a 0x10

- stage1998A (estatico): ath_dev.ko importa **request_threaded_irq** y free_irq; por eso la nota #631 no
  encontraba request_irq. 9 funciones espectrales y 2 binarios ubntspecd. Que detener el daemon o el
  filtro apague la IRQ es INFERIDO; el efecto sobre el TX de datos es DESCONOCIDO; mascara y ring
  DESCONOCIDOS.
- stage1999A (estatico): 4178 stores al offset 0x10 en umac.ko de WA y XC, 514 en la familia de init y
  176 con base s0. El offset 0x10 es demasiado comun para identificar el inicializador solo por offset;
  los 42 candidatos a escritor de 1993A siguen sin atribuir.

## Waves 162/164/165 - traza ioctl de ubntspecd

- stage2010A: 52 sitios jalr en ubntspecd y **0 codigos ioctl atribuidos** (ninguno adivinado).
- stage2023A: los jalr se agrupan en 4 grupos GOT; no hay tabla de secciones que mapee slot a nombre;
  el wrapper es DESCONOCIDO.
- stage2029A: la resolucion DT_MIPS_GOTSYM nombra 2 sitios (__uClibc_main) y deja 50 sin resolver; 0
  sitios ioctl con inmediatos. **El numero de comando ioctl sigue DESCONOCIDO.**
- Correccion posterior (Wave 166, fuera de este conjunto): stage2034A muestra que solo 2 de los 52 jalr
  pasan por un stub; la mayoria son llamadas directas, asi que la lectura por grupos GOT queda superada.

## Waves 162/164/165 - censo de constructores de priv+0x10 en umac

- stage2011A: umac.ko (no ath_dev.ko) importa alloc_netdev_mq, register_netdev y free_netdev; 12
  funciones constructoras (__ath_attach, init_ahb, osif_ioctl_create_vap, __ol_ath_attach/detach por
  modulo) contienen **26** stores a 0x10, desde 4178.
- stage2022A: de esos 26, **22 son guardados de prologo `sw s0,16(sp)`** en la pila y solo 4 son stores
  a estructura: el conteo anterior estaba contaminado.
- stage2028A: los 4 stores a estructura llevan su instruccion definidora (lw v0,-7736(s7) y
  lw v1,880(s1)), pero un slice no es flujo de datos: **inicializador DESCONOCIDO**.

## recall-first

Antes de escribir la nota, 3 de 6 consultas al vault unificado tuvieron aciertos: ath-spectral-filter 2,
ubntspecd 7, netdev priv 4; alloc_netdev_mq, dev_weight y netdev_max_backlog 0 (especificos nuevos).
No se corrio chequeo scholar en esta wave (no se pidio).

## Etapa 2040A - vault

La nota #632 quedo en research/notes/scholar_sources/ como evergreen. `hyperresearch sync` actualiza la
base pero no las paginas de indice; por eso tambien se corrio `hyperresearch index build`, que regenero
research/index/*.md. Conteo observado: 631 antes, 632 despues de sincronizar la nota y 652 despues del
primer index build, porque este agrego 20 paginas de indice por tag que el vault tambien cuenta.

## Etapa 2041A - banda 1536A..2045A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (222 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; los 10 recibos fuente y el 2040A aparecen en el
feed con su propia clase de evidencia. El servidor :8787 ya sirve la banda nueva. MASTER, CURRENT y
CURATED ya estaban en 179 lineas, asi que ninguna se reescribio.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado: el ciclo 1987A prueba que escribir y restaurar
  es seguro, no que ayude.
- La IRQ espectral esta medida, pero su parte de la CPU no es separable y el contraste de firmware no es
  controlado.
- El comando ioctl de ubntspecd, el inicializador de priv+0x10 y el escritor de 0xb4/0xdc siguen
  DESCONOCIDOS: todo porcentaje de "no tx buffer" sigue siendo un alias.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Un A/B controlado de detener ubntspecd en un solo panel.
- Una traza ioctl en vivo de ubntspecd.
- Leer un buffer SIOCGATHSTATS en vivo contra un offset resuelto.

Recibos: `stage2040a_guarida_irq_audit_and_constructor_census_note632_receipt.json`,
`stage2041a_command_center_1536a_2045a_refresh_receipt.json`, `stage2045a_wave167_opus2_gate.json`.
