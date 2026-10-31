<!-- doc-head: Wave334 L3, fast-path estático, presupuestos MIPS y compatibilidad WDS -->
Auditoría local de ELF y fuentes fijadas; perfiles generados sin SSH ni cambios en radios.
Los ciclos son un modelo aritmético, sin certificación de rendimiento o despliegue.
<!-- /doc-head -->

# OpenWrt: límites del fast-path y WDS

## Evidencia local

Se inspeccionaron mac80211 v3, ath10k_core y ath10k_pci, todos ELF32 MIPS
big-endian ET_REL con vermagic 6.6.110. Los SHA-256 quedan en el recibo JSON.
El mac80211 de referencia es fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6.
Se verificaron los 21 words de decap TEB y los 13 del gate de autorización 4addr.
El análisis relocation-aware de ath10k_mac_register no equivale a ejecutar su ruta.
No se encontró un ag71xx.ko independiente: puede estar integrado en el kernel.
La lectura de su fuente de release no identifica el binario cargado en un equipo.

## Ethernet TX, RX y cuatro direcciones

`frame_mode=2` selecciona Ethernet para TX bajo condiciones de driver/firmware.
No demuestra decapsulación Ethernet RX, ni evita todo trabajo de mac80211.
La capacidad moderna se llama `SUPPORTS_TX_ENCAP_OFFLOAD`.
`ieee80211_subif_start_xmit_8023` conserva fallback para EAPOL/control-port,
estaciones no autorizadas o no subidas al driver y claves no aptas para offload.

Un AP_VLAN hereda las operaciones de su BSS. Si usa cuatro direcciones, necesita
`IEEE80211_OFFLOAD_ENCAP_4ADDR`; no se encontró su anuncio en el mac.c ath10k-ct
del commit fijado por OpenWrt. Forzar el flag o habilitar modo 2 queda rechazado
para el contrato WDS actual hasta validar soporte completo.

El perfil conserva modo 1, encapsulación software, TEB `0x6558` y la secuencia
EAPOL antes de autorización/AP_VLAN después de autorización.
Un bypass RX podría saltar el punto de decap modificado: su equivalencia es UNKNOWN.
El parámetro visible en sysfs tampoco prueba que los vdev existentes se reconfiguren.

## Identidad de fuentes y ABI

OpenWrt v24.10.4 declara backports mac80211 6.12.52 y ath10k-ct de la rama 6.10,
commit ac71b14dc93aef0af6f0f24808b0afb673eaa5f5, sobre kernel ABI 6.6.
Se contrastaron fuentes Linux 6.6.110, 6.12.52 y ath10k-ct.
Compartir vermagic no prueba identidad de fuente, configuración o Module.symvers.
No se trasladan offsets binarios históricos a módulos recompilados.

## Bridge, flowtable y GRO/GSO

La ruta bridge termina en dev_queue_xmit y conserva sus reglas de forwarding.
`nf_flow_table_inet` acelera flujos elegibles IPv4/IPv6 TCP/UDP, no cualquier trama L2.
Un hit puede saltar hooks posteriores: clasificación WMM/DSCP, contabilidad y
firewall deben conservar su semántica antes de considerar un cambio.
No se habilitó flow offloading ni se infirió offload hardware por el nombre del módulo.

La fuente ag71xx de OpenWrt entrega RX mediante `netif_receive_skb_list`, sin
`napi_gro_receive` en ese archivo. Activar solo una feature GRO no acredita agregación.
mac80211 sí importa `napi_gro_receive`, sin que el símbolo pruebe su ejecución.
Un super-SKB puede reducir costes por skb; si el egreso carece de GSO/TSO adecuado,
la segmentación vuelve a software. Los paquetes en el aire siguen existiendo.
VoIP pequeño y multicast no se tratan como agregados TCP genéricos.

## Presupuestos WA y XC

Los relojes de 535 MHz y 720 MHz se toman del mandato; no son lectura de CPU actual.
Para 100 Mbps y paquetes de 1500 bytes hay 8333.33 paquetes/s en ese denominador.
Reservando 25% de CPU quedan 48150 ciclos/paquete en WA y 64800 en XC.
Con paquetes de 64 bytes quedan 2054.4 y 2764.8 ciclos/paquete respectivamente.
No son límites de goodput ni RTT estimado: faltan ACK, sentidos, overhead y otros trabajos.
Dual issue afecta IPC; no duplica ciclos de reloj ni convierte el equipo en dos núcleos.
GRO amortiza solo el coste por skb; el modelo conserva el trabajo por paquete.
Sin costes suministrados, uso CPU, factibilidad y speedup permanecen null.

## Compilación y prefetch

El target ath79 de release declara CPU_TYPE=24kc. Los flags efectivos de los
módulos requieren configuración y log verbose; ELF MIPS32_R2 no prueba `-Os` o `-O3`.
Se genera un candidato por objeto con `-O3 -march=74kc -mtune=74kc`, soft-float y
DSP/DSPR2 deshabilitado, conservando ABI, hardening y el resto de Kbuild.
Queda HOLD hasta verificar CPU real, toolchain, headers, símbolos y pruebas cargadas.
`-mdspr2` queda en cuarentena por soporte ASE y seguridad del estado DSP en kernel.

Prefetch es una hipótesis sin parche aplicado. Solo se propone tras límites,
vida útil y sincronización DMA; no sobre MMIO ni buffers sin propiedad CPU.
Se deben medir ciclos, misses de I/D-cache, tamaño de texto y latencia: O3 puede
empeorar la presión de I-cache. No se asigna un porcentaje de mejora imaginado.

## Reproducción y aceptación

`python tools/firmware/fmx_openwrt_ground_up_fastpath_optimizer.py --board WA --inspect-binaries`

`python -m pytest tests/test_fmx_openwrt_ground_up_fastpath_optimizer.py -q`

Los perfiles runtime contienen únicamente comandos de lectura; el generador no ejecuta ninguno.
La aceptación física requiere rollback independiente, EAPOL/TEB/AP_VLAN íntegros,
MACs downstream distintas y comparación contrabalanceada bajo carga de CPU/Sirq,
goodput, RTT y pérdida. Esta auditoría no concede esa aceptación.
