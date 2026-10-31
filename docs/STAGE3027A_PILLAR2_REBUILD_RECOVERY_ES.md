<!-- doc-head: W367 recuperado con readback solo lectura; ABI y captura archivada verificados, riesgos del hook y EVM sin aceptar -->
Recuperacion del banco CONFIRMED_RUNTIME; par recompilado confirmado en estatico.
Captura historica recuperada, con alcance de anillo y endian mixto explicitos.
Gate PARTIAL: no promover el modulo ni atribuir mejora RF o precision de ranging.
<!-- /doc-head -->

# W367 / Stage3027A: reconstruccion del pilar 2 y recuperacion

Responsable: lane_4, reemplazo de OpenCode; revision binaria por subagente
`rea-specialist`. Atribucion: Linux/ath10k para carga, anillo y depuracion;
QCA firmware para los datos del descriptor, cuya semantica sigue limitada.

## Recuperacion observada en esta sesion

Primero se consulto exclusivamente el LAP de banco, sin escrituras remotas.
Ya habia reiniciado antes de esta sesion: uptime inicial 1240.33 s, kernel
6.6.110, radio AP en canal 36/20 MHz y una estacion asociada. MemAvailable
inicial 9732 kB; ultima lectura 9184 kB, uptime 1462.61 s y una estacion.
No existe `fmx_ppdu_end`; `/proc/kallsyms` tampoco contiene sus simbolos en
ath10k_core. Los modulos activos ocupan core 548864 B y PCI 49152 B.

| Archivo original, igual en /lib/modules y /rom | SHA-256 |
| --- | --- |
| ath10k_core.ko | `1ef8144f569a84bb5da67fa6b8c515123ab8b5ea809ce5d8cc214ece8e51571a` |
| ath10k_pci.ko | `9e758ff4e10ab54269187fae8c4bd2b018d77177bc9842997ed0e7ebab28ce28` |

Estos hashes identifican los archivos, no la memoria reubicada del kernel.
La identidad activa como par original se infiere del arranque, tamanos y
ausencia de simbolos y debugfs parcheados. No hay build-id o srcversion
discriminante. SHA-256 exacto de la imagen cargada: UNKNOWN.
No se repitio reboot porque el par parcheado ya no estaba activo.
Esta sesion: cero cargas/descargas de modulos, reboots o escrituras al banco.

## Historial preservado

| Intento anterior | Resultado recuperado |
| --- | --- |
| 1 | core y PCI insmod rc=0; captura vacia; restauracion con rmmod y SSH termina en timeout. Fallo preservado. |
| 2 | core y PCI insmod rc=0; captura vacia, radio sin reasociacion; reboot controlado devuelve originales. |
| 3 | insmod rc=0, reasociacion observada, captura durante 310 s y reboot controlado. La lectura inmediata vio cero estaciones; la lectura nueva confirma una. |

No se ejecutaron esos intentos en esta sesion. Los JSON originales se conservan.
El archivo binario compartido fue sobrescrito historicamente por el intento 3:
los hashes de las capturas vacias 1/2 quedan solo en sus recibos; sus bytes no
se han recuperado. El watchdog historico usaba rmmod en su restauracion; no
constituye rollback seguro del modulo parcheado y no debe reutilizarse.

## Reconstruccion y captura: alcance aceptado

El par `*.night367.stripped.ko` tiene core SHA-256
`111af363c5d41558eff45a82ce924cdaed2db6aa1a107b7c439f6ac62427be37`
y PCI `bd19bafaf39f0a8abf58f04d8124b7a6c237dfa0e0106c6bda66a56842662789`.
Ambos son ELF32 MIPS BE ET_REL, vermagic
`6.6.110 mod_unload MIPS32_R2 32BIT`, y this_module de 384 B, igual al original;
el SDK anterior producia 352 B. El arbol night-20261007-reproduce tiene kernel
config SHA-256 `13699b7c04d3fd08121a016a5e56a8c08528906fe682033de2dc97168f21d0f2`.
La compatibilidad de los campos comparados y el insmod historico no demuestran
equivalencia completa de configuracion o seguridad de ejecucion.

Captura SHA-256 `de4662fbc94e83c712592d218bb997780880ba609711130489e2bf95a995a387`:
262208 B, cabecera FPPH de 64 B y 2048 registros FPPU de 128 B.
Secuencia 15541..17588; total 17589 invocaciones, indice 1205.
15541 registros fueron desplazados. Ventana retenida: 33.352441 s.
Es una sesion de mas de cinco minutos con anillo limitado; no son cinco minutos
de muestras completas ni una medicion bajo carga controlada.

## Hallazgos que impiden cierre verde

- El lector toma count, libera lock y reserva; al retomar lock vuelve a tomar
  count y puede copiar mas registros de los reservados si el anillo crecio.
  Fuente compilada y ensamblado respaldan el riesgo; no se provoco en el banco.
- El teardown con rmmod fallo historicamente. La causa exacta del cuelgue es
  UNKNOWN; no se atribuye a la carrera sin evidencia causal.
- Los escalares del registro son BE, pero evm[16] conserva bytes LE del
  descriptor. El analisis anterior no puede sustentar posiciones high/low.
- En cada word EVM 0..3 hay 2038 valores `0x80808000`, cuatro centinelas y
  seis excepciones; la prosa anterior contaba 2044 ceros incorrectamente.
  Words 4..15 son siempre `0x80808080`. Escala dB y mapeo de cadenas/subportadoras
  siguen UNKNOWN; diversidad de timestamps no demuestra fronteras PPDU.
- El accessor usado para peer_idx es MSDU y la mascara aplicada es MPDU;
  esa semantica no queda aceptada. Precision de ranging sigue UNKNOWN.
- fq_overmemory y cambio de RTT p95 bajo carga no fueron medidos; el objetivo
  Karpathy no esta probado. MemAvailable de la restauracion no valida el modulo.

Siguiente paso tecnico: corregir y verificar offline el lector, teardown y
decodificacion antes de proponer otra carga. No repetir el swap actual.

## Evidencia

- Gate: `artifacts/verification/wave367_lane4_pillar2_rebuild_gate.json`.
- Lecturas nuevas: `artifacts/ground_up/pillar2_build/w367_recovery/`.
- Revision: `artifacts/ground_up/pillar2_build/w367_rea_specialist/`.
- Intentos preservados: `artifacts/autoresearch/wave367_pillar2_bench_capture*.json`.
- Captura: `artifacts/autoresearch/wave367_fmx_ppdu_end_records.bin`.

Sin contacto con produccion ni PowerBeam. El master state no fue modificado.
