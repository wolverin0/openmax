<!-- doc-head: Stage 3004A (W351 P1) ES: auditoria de solo lectura del PCC both-addresses 21 buckets del core MK2-RS; dueño efectivo de cada bucket (primera regla habilitada gana por connection-mark=no-mark), 5 reglas duplicadas que nunca aplican, buckets 19/20 caidos a isp3/isp5 por isp1_peak deshabilitado, reparto contado en 60 s contra el nominal, sin buckets sin marca; hallazgo INFERRED de que "Forzados a TECO" queda pisado por el PCC -->
Que cubre: como se resuelve un bucket con dos reglas, que WAN se queda con cada uno, cuantas conexiones nuevas recibio cada WAN en 60 s, que reglas sobran y que conviene revisar.
Estado: solo lectura (verbos print). Cero escrituras en el core. Recomendaciones para el dueño (infra), no aplicadas.
Datos maquina: artifacts/autoresearch/wave351_core_pcc_bucket_audit.json. Gate: artifacts/verification/wave351_lane3_core_pcc_audit_gate.json.
Horas: Argentina (UTC-3). Leer cuando: antes de tocar el PCC o de diagnosticar el reparto entre WAN.
<!-- /doc-head -->
# Stage 3004A: auditoria del PCC del core (W351 P1)

## 1. Como se resuelve un bucket con dos reglas

Todas las reglas PCC (posiciones 34 a 61 de mangle prerouting) tienen `connection-state=new`, `connection-mark=no-mark`, `in-interface=bridgeLAN`, `dst-address-type=!local` y `passthrough=yes`. Ninguna tiene matchers extra (sin time, sin listas de origen ni destino).

Por eso **gana la primera regla habilitada** que coincide con el bucket: marca la conexion, y las reglas siguientes del mismo bucket ya ven una marca y no pueden coincidir. Es la misma regla que usa el validador de infra (`abeni_retirement.py`, `effective_buckets`).

## 2. Buckets con dos reglas

| Bucket | Regla que gana (posicion) | Regla que nunca aplica (posicion, conexiones en 60 s) |
| :-- | :-- | :-- |
| 21/4 | isp6 (38) | isp2 (55, 0) |
| 21/5 | isp5 (39) | isp3 (56, 0) |
| 21/6 | isp5 (40) | isp7 (57, 0) |
| 21/15 | isp13 (49) | pppoe (58, 0) |
| 21/18 | isp1_peak (52) | isp2 (59, 0) |
| 21/19 | isp3 (60) | isp1_peak (53), deshabilitada |
| 21/20 | isp5 (61) | isp1_peak (54), deshabilitada |

- Los "dos dueños" del 29/10 son cosmeticos: en 21/4, 21/5, 21/6, 21/15 y 21/18 la segunda regla nunca coincide.
- 21/19 y 21/20 si cambian de dueño: las reglas isp1_peak estan deshabilitadas y los schedulers `codex-peak-fb-reconcile` tambien, asi que isp3 e isp5 se quedan con ellos todo el tiempo.
- **Ningun bucket queda sin marca:** los 21 tienen dueño efectivo.

## 3. Reparto por WAN (60 s desde las 20:04, 21 953 conexiones nuevas)

| WAN (marca) | Buckets efectivos | Nominal | Contado |
| :-- | :-- | --: | --: |
| ether1-WAN1-750 (isp1_peak) | 18 | 4,8 % | 5,0 % |
| ether3-WAN2-Mati (isp2) | 0, 1 | 9,5 % | 10,5 % |
| ether5-WAN3-Pachi (isp3) | 2, 3, 19 | 14,3 % | 13,4 % |
| vlan_coop_2011 (isp5) | 5, 6, 20 | 14,3 % | 14,3 % |
| vlan_Fiber_2011 (isp6) | 4 | 4,8 % | 4,1 % |
| ether6-WAN-TECO (isp7) | 7 | 4,8 % | 4,5 % |
| pppoe-out1 (pppoe) | 8, 9 | 9,5 % | 9,1 % |
| vlan-Pedrito_wan2 (isp10) | 10 | 4,8 % | 4,5 % |
| vlan_personal_4011 (personal) | 11, 12 | 9,5 % | 13,6 % |
| ether10-colo (isp12) | 13, 14 | 9,5 % | 8,1 % |
| vlan_movis_2011 (isp13) | 15 | 4,8 % | 4,2 % |
| pppoe-out2 (isp14) | 16, 17 | 9,5 % | 8,7 % |

- El reparto contado sigue al nominal, salvo Personal (13,6 % contra 9,5 %). Con hash por ambas direcciones, unos pocos pares origen/destino con muchas conexiones pueden cargar un bucket; un solo minuto no alcanza para separarlo del azar.
- **Capacidad por WAN:** no esta documentada en infra (solo hay muestras sueltas de RX). No se puede comparar peso contra capacidad.

## 4. Otro hallazgo (INFERRED)

- **Que pasa:** las reglas 32 ("RouteICMP8888viaTECO") y 33 ("Forzados a TECO") ponen solo una marca de ruteo `to_isp7`, con passthrough. Despues, la conexion nueva recibe igual una marca PCC (34-61), y el mark-routing por WAN de 62-73 (passthrough=no) pisa `to_isp7`.
- **Efecto:** lo "forzado a TECO" sale en realidad por TECO solo cuando su bucket es el de isp7, mas o menos 1 de cada 21. La regla 33 cuenta 27 063 paquetes en 60 s.
- **Como confirmarlo (solo lectura):** mirar `connection-mark` en `/ip firewall connection` para ese rango de origen.

## 5. Recomendaciones (para infra, no aplicadas)

1. Borrar o comentar las 5 duplicadas que nunca aplican (posiciones 55 a 59).
2. Decidir si isp1_peak debe recuperar 19 y 20, o si queda el reparto actual: isp3 e isp5 con 3 de 21 cada una.
3. Confirmar lo de "Forzados a TECO". Si se confirma, que esa regla ponga una marca de conexion propia, o excluir ese rango del PCC.
4. Documentar la capacidad de cada WAN junto a su cantidad de buckets.

## 6. Limites

- Una ventana de 60 s; los porcentajes contados son de ese minuto.
- Solo verbos print: dos lecturas de mangle, mas identity, resource y scheduler. IPs enmascaradas en el JSON.
