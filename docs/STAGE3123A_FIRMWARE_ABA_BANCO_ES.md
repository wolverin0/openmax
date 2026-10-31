<!-- doc-head: W457 firmware CURRENT/A/CURRENT/B/CURRENT de banco -->
Evidencia finita; sin promocion de firmware ni aceptacion SG03-05.
Separar arranque, trafico RF, recuperacion automatica y mantenimiento manual.
El gate declara los pendientes; no convierte observaciones parciales en aprobacion completa.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W457 - comparacion de firmware en banco

Fuente: [artefacto W457](../artifacts/autoresearch/wave457_firmware_aba.json), SHA256 `13bab943228487c77fcbd1e7326377fca8877e75b0c1dce200ea328eeb9019de`.
Cierre de la sesion: `2026-10-31T18:34:26.116825+00:00`. Deadline ampliado a 18:35Z por Master `<orca-id>`.

## Alcance y metodo

AP cableados: PowerBeam .241 y LAP .20. Los peers RF-only .242 y Loco .117 conservan CURRENT: no se demostro rollback autonomo de imagen. No produccion.
Secuencia prevista: CURRENT -> A (24.10.4/2410_bp) -> CURRENT -> B (25.12.6/2512_bp) -> CURRENT. PBE la completo; LAP ejecuto CURRENT/A/CURRENT y B quedo pendiente. La variable es el bundle de firmware; esto no aisla una funcion del driver.
PBE: dos ventanas UP y dos DOWN por fase, mismos binarios RAM en ambas puntas. LAP: dos ventanas bidireccionales de 20s por fase, carga host-Loco sin iperf en el AP; LiteBeam conocida permanece pasiva.
Cohorte LAP: Loco PUBLIC_DEVICE_0036 y LiteBeam PUBLIC_DEVICE_0083. Su presencia no equivale a dos estaciones cargadas.
Se retienen CPU y MemAvailable bajo carga, contadores retry/failed y RTT. No se usan umbrales nuevos: dos repeticiones describen variacion observada, no significancia universal.
LAP conserva protocolo W434: ping iniciado inmediatamente antes de TCP; no se afirma coincidencia exacta de cada paquete con carga.

## PBE: ventanas formales

| Fase | UP Mbps (r1/r2) | DOWN Mbps (r1/r2) | RTT p95 UP ms | RTT p95 DOWN ms |
|---|---|---|---|---|
| CURRENT_PRE | 9.800/10.008 | 23.990/22.300 | 15.362/17.288 | 13.432/13.261 |
| A | 9.957/9.270 | 23.513/22.710 | 14.641/25.454 | 13.158/12.845 |
| CURRENT_AFTER_A | 8.802/9.329 | 23.442/22.940 | 16.298/19.590 | 10.397/12.469 |
| B | 9.747/9.485 | 23.824/23.224 | 19.079/20.174 | 11.772/12.993 |
| CURRENT_AFTER_B | 9.276/9.848 | 22.940/24.393 | 18.137/20.402 | 15.276/14.898 |

No mejora consistente que justifique promocion: comparar tambien los retornos CURRENT y su deriva temporal.

## LAP: ventanas formales

| Fase | DL Mbps | UL Mbps | Suma bidireccional Mbps | RTT p50 ms | RTT p95 ms |
|---|---|---|---|---|---|
| CURRENT_PRE | 8.446/11.757 | 29.089/27.929 | 37.535/39.687 | 4.707/5.527 | 8.803/6.777 |
| A | 12.443/13.332 | 15.349/15.342 | 27.792/28.674 | 6.103/7.235 | 7.962/11.551 |
| C_AFTER_A | 12.085/11.471 | 15.667/15.795 | 27.752/27.266 | 6.181/6.579 | 15.665/9.106 |

El retorno CURRENT tras A tambien midio ~27 Mbps frente a ~38 Mbps iniciales. Esa caida no puede atribuirse causalmente a A.

## Crashes reales y recuperacion

| Trial | Intenciones emitidas | GUID distintos retenidos | Recuperaciones ICMP | Tiempos comparables s |
|---|---:|---:|---:|---|
| PBE_A_R2 | 5 | 5 | 5 | 5.656, 5.545, 5.529, 5.857 |
| PBE_C_AFTER_A | 5 | 5 | 5 | 6.227, 4.727, 4.372, 4.492, 5.387 |
| PBE_B_1 | 5 | 5 | 5 | 11.362, 5.552, 14.500, 5.460, 10.105 |
| LAP_C_AFTER_A | 1 | 1 | 0 |  |

PBE A tuvo cinco GUID/crashes reales y cinco recuperaciones RF, pero solo cuatro tiempos comparables; el quinto quedo censurado por el observador. La preparacion B fallida antes de escritura no cuenta como crash.
Los tiempos son cotas superiores de retorno ICMP, con prueba posterior de SSH al peer. TCP recovery no medido. No se forzo el camino WEDGED de cuatro fallos consecutivos.
LAP CURRENT: primer hard GUID <uuid>; 88 probes sin retorno ICMP en la ventana de 180s. Se detuvo tras una intencion; no se completo N5.
El mismo boot registro device successfully recovered y un warning drv_assign_vif_chanctx / phy0-ap0.sta1 Failed check-sdata-in-driver, flags 0x1. Eso distingue recuperacion del dispositivo de trafico RF; la causa unica permanece UNKNOWN.
La recarga BSS posterior fue mantenimiento manual separado: se conservaron configuracion/modulos, expiraron los bans y se comprobo SSH al Loco por IPv6 RF. No corrige retrospectivamente el crash fallido.

## Preservacion, fallos y limites

Se respaldaron y verificaron los ocho MTD de cada nodo (32 particiones). En este mapa ART es mtd7; mtd5 es rootfs_data. Nunca se escribieron u-boot, u-boot-env ni ART.
Cada commit usa SHA256SUMS o binding de readback, hashes locales/remotos, -T nativo sin -F, guarda conservadora de RAM y una intencion duradera antes de launch. Los rechazos de capacidad previos a launch permanecen.
CURRENT LAP b297b08d... es una imagen reconstruida del kernel/SquashFS del readback original; no se afirma identidad con una distribucion descargada. CRC/metadata no equivalen a firma criptografica.
Kit/config seleccionado: 52 archivos PBE; 74 LAP con modos, ocho directorios privados y dos enlaces de arranque. La closure LAP se transmite una vez directamente al overlay; no se guarda su tar en RAM del DUT.
El kit original del LAP depende de sta1. El orden AID de la cohorte se controlo con BSS y ban temporal de 30s; no se cambio el kit ni UCI para ocultarlo.
La guarda original de memoria no se bajo. Las preparaciones de cache posteriores a radio/-T/staging tienen eventos separados, prohiben replay ambiguo y preservan los rechazos iniciales.
El intento generico d99 de conciliacion tenia un defecto de replay detectado por revision. Solo se uso una vez con rc0; el flag se prohibio en 86f y se preservo el defecto y su fuente.
Si el guard del companion termina sin finished, una eventual conciliacion del coordinador debe identificarse como manual y probar cierre real; no acredita que haya terminado el guard natural.
SG03-05 NO DEMOSTRADO: el stock airOS no aparece asociado. Ping de gestion no prueba WDS/RF. No se continuo SSH al stock tras la orden del Master.
Los peers RF-only conservaron CURRENT. Estas muestras no prueban un twin completo de produccion ni autorizan migracion de AP de produccion.

## Transacciones y cierre

| Trial | Estado |
|---|---|
| PBE_A_R2 | FULLY_VERIFIED |
| PBE_C_AFTER_A | FULLY_VERIFIED |
| PBE_B_1 | FULLY_VERIFIED |
| PBE_C_AFTER_B | FULLY_VERIFIED |
| LAP_SPLIT_C_VALIDATE_1 | ABORTED_BEFORE_COMMIT |
| LAP_A_R2 | FULLY_VERIFIED |
| LAP_C_AFTER_A | FULLY_VERIFIED |

Flashes verificados: 6; ventanas PBE: 20; ventanas LAP: 6; escrituras protegidas: 0.
El estado final y la liberacion de equipos se aceptan solo con readback fresco, no por estas tablas.
Fuentes: [imagenes](STAGE3123A_image_re.json), [CURRENT LAP](STAGE3123A_lap_recovery_rebuild.json), [revision driver](STAGE3123A_review_LAP_C_AFTER_A.json), [cache](STAGE3123A_lap_staged_cache_review.json), [BSS manual](STAGE3123A_lap_after_crash_bss_reload_review.json).
Sin ganador/promocion. Ver [gate W457](../artifacts/verification/wave457_lane4_firmware_aba_gate.json) para cierre y gaps explicitos.

## Cierre observado

Los cuatro nodos quedaron en CURRENT y se liberaron con lectura fresca posterior a la verificacion final del LAP.
LAP boot `<uuid>`; estado `FINAL_CURRENT_REBOOT_FULLY_VERIFIED`. Companion con socket/procesos vivos y SSH al Loco por RF comprobados.
La solicitud SSH original de 11520 bytes fue rechazada por Dropbear antes de exec (String too long). Se archivo integra y la nueva orden de 3533 bytes conservo los 79 hashes.
Las reparaciones de cierre manual/marker finished quedaron offline; no se ejecutaron ni se escribio ese marcador por el coordinador.
Liberados: LAP-120 .20, Loco .117, PBE .241 y .242. Produccion sin cambios; LAP B y SG03-05 siguen pendientes.
