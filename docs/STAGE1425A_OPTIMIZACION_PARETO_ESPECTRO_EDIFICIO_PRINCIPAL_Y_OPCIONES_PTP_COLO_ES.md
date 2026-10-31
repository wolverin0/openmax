<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1425A (ES) - optimizacion Pareto de 4 objetivos (solape, guarda, enlaces movidos, CAC DFS) del espectro 5 GHz de EDIFICIO-PRINCIPAL con pymoo NSGA-II/NSGA-III: frente de 19 puntos, exacto hasta k=3; ningun re-plan completo llega al frente. Rodillas del PtP-Colo: K1 ch149 5745 / ch165 5825 (no-DFS, 45 s), K2 ch56 5280 (DFS, guarda 20/20, 60 s CAC, 120 s), K3 ch149 + mover ptp-abeni-ap. Sensibilidad al ancho desconocido de ptp-abeni-ap (10/20/40 MHz). Runner con preflight de guarda. Offline. -->
# Stage 1425A — Optimización Pareto del espectro de EDIFICIO-PRINCIPAL y opciones del PtP-Colo

Wave 64 (Stages 1422A..1427A). Todo offline: sin red, sin SSH, sin binarios. Ningún radio fue tocado.

- **Frente Pareto**: [`stage1422a_edificio_principal_pareto_channel_front.json`](../artifacts/verification/stage1422a_edificio_principal_pareto_channel_front.json)
- **Rodillas y sensibilidad**: [`stage1423a_ptp_colo_k1_k2_k3_sensitivity_matrix.json`](../artifacts/verification/stage1423a_ptp_colo_k1_k2_k3_sensitivity_matrix.json)
- **Runner no-DFS vs DFS**: [`stage1424a_ptp_colo_runner_nondfs_vs_dfs_dryrun.json`](../artifacts/verification/stage1424a_ptp_colo_runner_nondfs_vs_dfs_dryrun.json)
- **Herramientas**: `tools/research/optimize_edificio_principal_5ghz_pareto_channels.py`, `tools/deploy/ptp_colo_staged_channel_and_openwrt_runner.py`
- **Gate**: [`stage1427a_wave64_opus55_gate.json`](../artifacts/verification/stage1427a_wave64_opus55_gate.json)

## 1. Fuentes

El optimizador lee solo 1374A (ocupación: 16 emisores co-ubicados y 22 APs de campo lejano), 1375A
(qué canales son DFS) y 1389A (los 27 canales de la tabla ath10k, 5180..5865 MHz). El SKILL.md de
pymoo fijó el método. Los cuatro archivos quedan con su SHA-256 en 1422A.

El runner extendido (1424A) sigue leyendo sus entradas de siempre (1344A, la copia UISP y el perfil
OpenWrt). Al cambiar su código se regeneraron 1374A..1376A: el contenido es idéntico, solo cambia
`meta.tool_sha256`. La suite 1378A y el gate 1379A siguen en verde.

## 2. Formulación

- **Radios**: el PtP-Colo (debe salir de 6035 MHz) y los 16 co-ubicados. 17 en total.
- **Decisión**: cada radio se queda o pasa a un centro de la tabla ath10k, con su ancho actual.
  20 MHz usa los 27 centros. 40 y 80 MHz usan bloques cuyas mitades o cuartos están en la tabla.
  Atajo: los anchos 10 y 30 MHz (solo airOS) reutilizan los centros de 20 MHz.
- **f1**: solape total co-ubicado en MHz, sobre los 136 pares (incluye lo que ya solapa hoy).
- **f2**: penalización de guarda, suma de `max(0, 20 - hueco)`; un par solapado suma 20.
- **f3**: enlaces movidos, contando el PtP-Colo. 17 es el re-plan completo.
- **f4**: 60 s de CAC por cada radio movido que cae en DFS.
- ch169 y ch173 entran por el pedido pero pasan 5825 MHz: se marcan y las rodillas los excluyen.
- El campo lejano no es objetivo; se informa por solución.

**Hoy**: f1 = 10 MHz (ptp-jose-ap 80 MHz contra PTP-Alma-AP 40 MHz), f2 = 70.

## 3. Método y estadística

- k = 1, 2 y 3 se enumeraron completos. Como f3 se minimiza, un punto con k ≥ 4 no puede dominar a
  uno con k ≤ 3: esa parte del frente es **exacta**.
- Encima de k = 3: NSGA-II y NSGA-III (pymoo 0.6.2), codificación entera con SBX/PM y redondeo,
  población 92, 300 generaciones, semillas 1..10. Más un NSGA-II de re-plan completo (prohibido
  quedarse) para k ≥ 16.
- Hipervolumen con una normalización común (ideal/nadir del frente, referencia 1,1).

| Algoritmo | HV / HV del frente (media ± sd) | Rango | Recall puntos exactos k ≤ 2 |
| :--- | :-: | :-: | :-: |
| NSGA-II | 0,939 ± 0,031 | 0,890..0,984 | 0,83 |
| NSGA-III | 0,918 ± 0,030 | 0,869..0,952 | 0,93 |

Mann-Whitney U = 71, p = 0,121; A12 (NSGA-II sobre NSGA-III) = 0,71. Con 10 semillas no hay
diferencia significativa. NSGA-III conserva mejor los puntos de pocos movimientos.

## 4. Frente de Pareto (19 puntos, k de 1 a 6)

| k | f1 | f2 | f4 | PtP-Colo | Otros movimientos |
| :-: | -: | -: | -: | -: | :--- |
| 1 | 10 | 70 | 60 | 5280 | ninguno |
| 1 | 10 | 90 | 0 | 5745 | ninguno |
| 2 | 10 | 65 | 60 | 5280 | ptp-abeni-ap a 5745 |
| 2 | 0 | 80 | 60 | 5180 | PTP-Alma-AP a 5270/40 |
| 3 | 0 | 60 | 60 | 5280 | PTP-Alma-AP a 5190/40, Panel-Florida a 5745 |
| 6 | 0 | 25 | 240 | 5280 | 5 radios más, 3 de ellos a DFS |

- El mínimo de f1 (0 MHz) aparece con k = 2; el de f2 (25) con k = 6.
- **Re-plan completo**: ningún punto con k ≥ 16 llega al frente. Lo mejor encontrado fue f1 = 0 con
  f2 = 95, peor que mover 3 a 6 enlaces. En este modelo, mover pocos enlaces rinde más.
- Varios puntos mueven PTP-Alma-AP, el troncal hacia Almafuerte y Guarida: moverlo afecta a todos los
  CPEs aguas abajo. Es un dato del modelo, no una propuesta.

## 5. Rodillas operativas del PtP-Colo (ptp-abeni-ap a 20 MHz)

| Rodilla | Canal | Movidos | Hueco abajo / arriba | f1 | f2 | CAC | Watchdog | Campo lejano |
| :--- | :-: | :-: | :-: | -: | -: | -: | -: | :--- |
| K1a | 149, 5745 | 1 | 25 / **0** (ptp-abeni-ap) | 10 | 90 | 0 s | 45 s | PUBLIC_TERM_0004, Panel3-Alma |
| K1b | 165, 5825 | 1 | **5** / **0** (mati, acvnew) | 10 | 105 | 0 s | 45 s | PANEL3-JH |
| K2 | 56, 5280 | 1 | 20 / 20 | 10 | 70 | 60 s | 120 s | Panel 2 Guemes |
| K3 | 149, 5745 + ptp-abeni-ap a 5280 | 2 | 25 / 35 | 10 | 65 | 60 s (abeni) | 45 s / 120 s | PUBLIC_TERM_0004, Panel3-Alma |

En K3 el watchdog es de 45 s para el PtP-Colo y de 120 s para ptp-abeni-ap, que cae en DFS.

- **K2** es el único k = 1 que no agrega penalización co-ubicada (f2 queda en 70). Está en el
  frente exacto. Paga 60 s de CAC y comparte espectro con el sector GUEMES en campo lejano.
- **K1a** es el mejor no-DFS de k = 1 y domina a K1b mientras ptp-abeni-ap use 20 MHz o menos.
- **K3** deja al PtP-Colo con 25 MHz de guarda en no-DFS y baja f2 por debajo de hoy (65 contra 70).
  Cuesta retocar dos enlaces y lleva a ptp-abeni-ap a DFS. Sus extremos remotos también se mueven.
- **K3 sin DFS**: lo mejor es PtP-Colo en ch161 (5805) moviendo ptp-mati-ap a 5745. Da 20 MHz de
  guarda al PtP-Colo, pero ptp-mati-ap queda pegado a ptp-abeni-ap (hueco 0) y f2 sube a 85.

## 6. Sensibilidad al ancho de ptp-abeni-ap (5765 MHz, ancho no registrado)

| Ancho | K1a (f1, f2, hueco PtP-Colo) | K1b | K2 | Top-3 de 1374A |
| :-: | :--- | :--- | :--- | :--- |
| 10 MHz | 10, 80, hueco 5 | 10, 100, hueco 0 | 10, 65, 20/20 | 5745, 5825, 5220 |
| 20 MHz | 10, 90, hueco 0 | 10, 105, hueco 0 | 10, 70, 20/20 | 5745, 5825, 5220 |
| 40 MHz | 20, 100, **solapa 10 MHz** | 10, 115, hueco 0 | 10, 80, 20/20 | 5825, 5220, 5745 |

- La vista propia del PtP-Colo en **K1b y K2 no cambia** con el ancho; en **K1a sí**.
  Con 40 MHz, ch149 solapa a ptp-abeni-ap y cae al tercer puesto del ranking de 1374A.
- K3 elige mover a ptp-abeni-ap en los tres anchos (a 5280, o a 5270/40 si usa 40 MHz).
- Conclusión: antes de elegir K1a hay que confirmar el ancho de ptp-abeni-ap.

## 7. Runner con preflight de guarda (1424A)

```
python tools/deploy/ptp_colo_staged_channel_and_openwrt_runner.py --dry-run --channel 149
python tools/deploy/ptp_colo_staged_channel_and_openwrt_runner.py --dry-run --channel 165
python tools/deploy/ptp_colo_staged_channel_and_openwrt_runner.py --dry-run --channel 56
python tools/deploy/ptp_colo_staged_channel_and_openwrt_runner.py --dry-run --write
```

| Canal | DFS | CAC | Watchdog | Avisos WARN | Veredicto |
| :-: | :-: | -: | -: | :--- | :--- |
| 149 | no | 0 s | 45 s | GUARD y WIDTH_UNKNOWN (ptp-abeni-ap; a 40 MHz solapa 10 MHz) | PROCEED_WITH_WARNINGS |
| 165 | no | 0 s | 45 s | GUARD con ptp-mati-ap y ptp-acvnew-ap | PROCEED_WITH_WARNINGS |
| 56 | sí | 60 s | 120 s | ninguno; DFS_CAC deja 60 s de margen dentro del watchdog | CLEAR |

Sin `--dry-run` el runner sigue saliendo con código 65. Ningún aviso bloquea: la decisión es del operador.

## 8. Lectura para el operador

- Si se acepta DFS: **K2 (ch56)** es la opción más limpia de un solo movimiento.
- Si se exige no-DFS y un solo movimiento: **K1a (ch149)**, pero solo si ptp-abeni-ap usa 20 MHz o menos.
  K1b (ch165) no depende de ese ancho, pero queda pegado a dos PtP.
- Si se acepta mover dos enlaces: **K3** da la mejor guarda no-DFS al PtP-Colo.
- En todos los casos falta un airView en ambos extremos antes del Paso-0.

## 9. Límites honestos

- La ocupación sale del inventario (1374A), no de un escaneo; los sectores vienen de la copia del 2026-10-17.
- 1389A no aclara si la frecuencia de las filas de 40/80 MHz es control o centro (PTP-Alma-AP,
  ptp-pachi ap, ptp-jose-ap). Un corrimiento de 10 a 30 MHz cambiaría f1 y f2.
- Mover un enlace mueve también su extremo remoto; el espectro remoto no está modelado.
- Por encima de k = 3 el frente es una aproximación de NSGA, no una prueba de optimalidad.
- Las reglas regulatorias de AR siguen UNKNOWN (1381A); ch169/173 quedan fuera de las rodillas.

## 10. Verificación

```
python tools/research/optimize_edificio_principal_5ghz_pareto_channels.py --write
python -m pytest tests/test_stage1422a_to_1427a_suite.py -q
python tools/verify/verify_stage1427a_wave64_opus55_gate.py --write
```

El optimizador tarda cerca de un minuto y dos corridas dan bytes idénticos.

Método según el skill pymoo de K-Dense. Cita tomada del SKILL.md, sin consultarla en red:
Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent Skills:
A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
