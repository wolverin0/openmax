<!-- doc-head: Stage 3064A (W404) ES: .110 vuelto en RAM a la potencia del PtP del 26/10 (powerout 28 EIRP, antennagain 13, 15 dBm conducidos, recibo 47B) durante 3 min: 0 enlaces con el LTU-Lite 2 y temperatura hasta 91 C. 28 dBm ya es el maximo del 26/10, asi que no hubo escalones; se volvio al estado previo (powerout -4, antennagain 26). PtP y A/B sin correr; el Rocket LTU no aparecio -->
Que cubre: la potencia aplicada y su fuente, el resultado, la temperatura y el estado en que quedo .110.
Estado: escrituras solo en RAM de .110 con af set (sin commit), revertidas. 0 escrituras en el LTU-Lite 2, en /dev/ame y en flash.
Datos maquina: artifacts/autoresearch/wave404_ltu_ptp_ab.json.
Leer cuando: antes de volver a intentar el PtP LTU del banco.
<!-- /doc-head -->
# Stage 3064A: potencia del 26/10 sin enlace (W404)

## 1. Potencia aplicada

- **Fuente:** recibo 47B del 26/10, .110 como AP-PTMP 5500/20 con txpower 15 dBm, ganancia 13 dBi y EIRP 28; enlace con una estacion a -33/-36 dBm.
- **Antes:** powerout -4, antennagain 26 (unos -30 dBm conducidos), 85-86 C.
- **Aplicado en RAM:** `af set antennagain 13` y `af set powerout 28`, readback 28/13.

## 2. Resultado

- 3 min de observacion cada 10 s: TOTAL LINKS 0 en todas las muestras.
- Temperatura: subio a 91 C en los cuatro sensores.
- **Escalones de 3 dB:** no aplican, 28 dBm EIRP ya es el maximo del 26/10.
- **Vuelta atras:** powerout -4 y antennagain 26 de nuevo, 87 C despues. No es un corte termico: el cambio no sirvio.

## 3. Que queda

- Con los dos extremos iguales en frecuencia, ancho, SSID y cifrado y la potencia del 26/10, el enlace igual no sube: la potencia no era la causa.
- **Hipotesis siguientes:** que el LTU-Lite 2 no vea beacons (leer en la CPE su escaneo y si detecta el AP), o que el AP en RAM con el air_fpga parcheado no emita beacons utiles (comparar con el arranque del 26/10).
- El Rocket LTU no aparecio. **Karpathy: TARGET_NOT_MET**; ame_device_writes 0.
