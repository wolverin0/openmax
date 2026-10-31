<!-- doc-head: W371 CONFIRMED_OFFLINE: anillo v2 LE corregido, par MIPS ABI384 reconstruido y revision independiente PASS -->
Sin SSH ni acceso a dispositivos en esta ronda.
La captura W367 se conserva con 2048 registros y rechazos explicitos.
56 pruebas Python, C con ASan/UBSan y cuatro mutantes detectados.
Aceptacion limitada a fuente, build, ABI y pruebas locales; runtime UNKNOWN.
<!-- /doc-head -->

# W371 / Stage3031A: correccion offline del pilar 2

Estado: **CONFIRMED_OFFLINE**. Atribucion: Linux/ath10k para
el anillo, serializacion y ciclo de vida; external controller para decodificacion
y pruebas. Comportamiento en radio, EVM calibrado y precision fisica: UNKNOWN.

## Limites y continuidad

Esta ronda es exclusivamente offline. Parte de los hallazgos W367; no modifica
la captura historica, los modulos W367, el master state ni ningun equipo.
Los binarios nuevos requieren un despacho de banco separado; no se acepta
rendimiento, interop, recuperacion hardware o QoE por el resultado de un build.
El fallo W368 del control A tampoco se declara resuelto por este parche.

## Contrato del formato

v2 conserva cabecera de 64 B y registro de 128 B, con todos los escalares LE
y los bytes EVM LE explicitos. Flags de cabecera: bit 0 captura habilitada,
bit 1 snapshot estable por open, bit 2 formato LE. `metadata_flags` en offset
20: bit 0 peer valido, bit 1 PPDU done. El campo de flags en offset 46 sigue
siendo el dato raw QCA. `peer_idx=ffff` cuando no hay atribucion valida.

La captura legacy v1 conserva escalares nativos BE y EVM LE. El adaptador
exige `--legacy-cpu-endian big`; no acepta atribucion del campo peer antiguo.
No reescribe los bytes historicos para convertirlos artificialmente en v2.

## Anillo y remocion

El snapshot se reserva fuera del spinlock con capacidad fija. Un solo lock
protege la copia y la cabecera; las lecturas parciales del mismo descriptor
ven bytes inmutables. La asignacion no depende del count antes de tomar el lock.
La implementacion limita los snapshots simultaneos por ring.

Enable, disable y reset se serializan por ring. Deshabilitar no libera memoria
que RX pueda estar usando. La publicacion retiene referencias de core y bus;
la interfaz soportada es deshabilitar la captura en runtime y reiniciar para
retirar el par. No usar rmmod para restaurarlo. El origen exacto del cuelgue
historico sigue UNKNOWN: esta ronda cambia el contrato de remocion y elimina
su dependencia operativa, sin afirmar una prueba hardware del origen.
La retirada/reprobe de un dispositivo conserva deliberadamente su ring y
referencias hasta reboot. Repetir hotplug o reprobe acumula esa retencion;
no se afirma que sea una solucion de hotplug ilimitado ni sin coste de RAM.

## Decodificador y regresiones

El adaptador `tools/ground_up/pillar2_kernel/decode_fmx_ring.py` utiliza
`tools/ground_up/pillar2/ppdu_evm_ranging.py` sin editar ese archivo compartido.
Cada registro se reencuadra en los 84 B esperados por el decodificador existente.
Se validan version, endian, longitudes exactas, flags, capacidad, count,
write_idx, secuencia modular, reservados y formula temporal de software.

Captura SHA-256
`de4662fbc94e83c712592d218bb997780880ba609711130489e2bf95a995a387`:

| Campo | Resultado offline |
| --- | --- |
| Registros retenidos | 2048 |
| Invocaciones totales | 17589 |
| Desplazados | 15541 |
| Secuencia retenida | 15541..17588 |
| Ventana retenida | 33.352441 s |
| Descriptor estricto aceptado | 1871 |
| Rechazado por location 80..86 | 177 |
| EVM first-four ordinarios / centinelas / excepciones | 2038 / 4 / 6 |

Se conservan todos los registros raw y se cuentan por separado los rechazos.
No se identifica cada registro como PPDU distinto, ni se infiere una estacion
real, dB calibrados o precision de ranging. La conversion temporal de software
no demuestra la resolucion efectiva del hardware.

Trece regresiones nuevas cubren formatos legacy/v2, bytes EVM asimetricos,
peer invalido y sentinela, snapshots vacios/llenos, wrap de secuencia, muestras
truncadas/extra, contadores, reservados y datos fuera del rango documentado.
Un spy confirma 2048 llamadas al decodificador existente. Suite integrada:
56 passed; solo pruebas offline con fixtures locales.

## Build y evidencia

Se usa una copia aislada del kernel y paquete, sin cambiar el arbol W367.
Configuracion esperada: SHA-256
`13699b7c04d3fd08121a016a5e56a8c08528906fe682033de2dc97168f21d0f2`.
El primer lanzamiento fallo en WSL con WSAETIMEDOUT antes de salida del
compilador. El segundo devolvio rc0, pero CRLF habia cambiado el target a
`modules-CR`: no compilo y se rechazo ese falso exito. Se verifico ausencia
de procesos y objetos nuevos antes de reparar. El tercer lanzamiento, con LF,
compilo y enlazo ambos modulos, make rc0. Se preservan los tres logs.

Ambos son ELF32 MIPS BE ET_REL, vermagic
`6.6.110 mod_unload MIPS32_R2 32BIT`, y `.gnu.linkonce.this_module=384 B`.
Los datos exportados v2 son LE aunque el codigo del modulo sea MIPS BE.
Stripping conserva todas las secciones asignadas. Candidatos sin debug:

| Modulo | Bytes | SHA-256 |
| --- | --- | --- |
| core | 799704 | `63149266d2c2b9945251d2e5a8f032d6978a3774dc18779c9737e3fe94852cf7` |
| PCI | 73104 | `87342338299eca5acd7dd5c3098215fb2f01da6392482ac2c69dc7f7a9ab4069` |

Cinco comparaciones de comandos y objetos enlazados coinciden con W367 tras
normalizar rutas. Se refuto una sospecha de perdida de hwmon: la imagen exacta
y W367 night ya lo excluian; lo incluian otras variantes SDK incompatibles.
El patch aplica con fuzz0 en una copia aislada y produce C/H byte a byte iguales.

El harness del C real con servicios kernel simulados pasa ASan/UBSan. Cubre
crecimiento durante allocation, snapshot estable, limite de lectores, peer,
endian, disable concurrente, dos dispositivos y unwind de fallo al publicar.
El primer compile del shim carecia de typedef __u8; fallo preservado y corregido
solo en el test. LeakSanitizer se desactiva para la retencion intencional hasta
reboot; no es una prueba de ausencia de fugas. ASan/UBSan permanecen activos.
Cuatro mutantes son rechazados: reserva segun count, peer desde MSDU, falta de
pin del bus y lectura desde ring vivo en vez de snapshot.

Revision independiente separada de implementacion: **PASS**, sin bloqueantes,
con reejecucion de 13 tests y del harness existente. Incluye fuente, parche,
config, ELF/ABI, stripping y ensamblado relevante. No realizo otro build ni
acceso a equipos. La causa historica del cuelgue sigue UNKNOWN; no se cargo
este par en radio ni se comprobo rendimiento o recuperacion hardware.

Evidencia de decoder: `artifacts/ground_up/pillar2_build/w371_decoder/`.
Fuente/build/ABI: `artifacts/ground_up/pillar2_build/w371_fix/`.
Gate: `artifacts/verification/wave371_lane4_pillar2_fix_gate.json`.
