<!-- doc-head: Stage 3061A (W401) ES: se encontro el LTU-Lite 2 real detras de la Loco .250, en x.x.110.55 (afltu v2.4.0, CPE-PTMP 5500/20, config del 26/10, 4,6 dias encendido) pero no enlaza con .110. Los dos extremos coinciden en frecuencia, ancho, SSID y cifrado; la diferencia con el 26/10 es la potencia del AP (txpwr -30 contra txpower 15). No se subio la potencia porque .110 esta a 85-86 C sin guarda: decision del operador. El Rocket LTU no aparecio -->
Que cubre: como se encontro el LTU-Lite 2, que configuracion tiene, por que no enlaza y que falta decidir.
Estado: solo lectura salvo un alias RAM temporal en la Loco, agregado y quitado. 0 escrituras en .110, en el LTU-Lite 2, en /dev/ame y en flash.
Datos maquina: artifacts/autoresearch/wave401_ltu_discovery_ptp.json.
Leer cuando: antes de relanzar el PtP LTU del banco o de cambiar la potencia de .110.
<!-- /doc-head -->
# Stage 3061A: LTU-Lite 2 encontrado detras de la Loco (W401)

## 1. Como se encontro

- **UDP 10001 desde el host:** responde solo un LTU (.110). En x.x.1.20 contesta una NanoStation loco M2 con airOS 6, no un LTU.
- **Loco .250:** su puerto LAN esta en un bridge propio (br-lan, separado del radio), con enlace a 100 Mbit/s. La Loco usa x.x.1.20 en esa LAN.
- **Captura de 25 s en eth0:** un equipo e2:63:da (familia Ubiquiti) en x.x.110.55 pide cada 1-2 s su gateway x.x.110.1.
- **Acceso:** alias RAM x.x.110.250/24 en br-lan de la Loco y SSH por tunel; alias quitado al final.

## 2. LTU-Lite 2 (CONFIRMED_LIVE_READONLY)

- LTU-Lite (0xae08), afltu v2.4.0, 4,6 dias encendido, no esta de fabrica (no se le dio IP de banco).
- Config del 26/10: CPE-PTMP, 5500 MHz, 20 MHz, txpower 15, sin cifrado, SSID FMX-LTU.
- Estado: syncing, 0 enlaces. Temperatura 77 C en los cuatro sensores.

## 3. Por que no enlaza (INFERRED)

- .110 es AP en 5500/20, sin cifrado, autolink 1: coincide con la CPE.
- La diferencia con el PtP que funciono el 26/10 es la potencia del AP: txpower 15 entonces, txpwr -30 y powerout -4 ahora, unos 45 dB menos.
- **No se subio:** .110 esta a 85-86 C sin guarda termica y la potencia de banco la fijo el despacho. Lo decide el operador.

## 4. Pendiente

- El Rocket LTU no aparecio en la LAN (UDP 10001 al inicio y al final de la ronda).
- PtP y A/B sin correr. **Karpathy: TARGET_NOT_MET**; ame_device_writes 0.
