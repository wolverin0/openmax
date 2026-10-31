<!-- doc-head: Stage 3070A (W410) ES: mapa UISP de toda la red para el sidecar_e2e (26 sectores, 27 extremos PtP y 18 nodos del registro), sonda de latencia baja (1 eco cada 10 s) en cada sector y PtP nuevo con linea de base STOCK_BASELINE desde el 30/10, check_stale sobre 71 nodos y reclamos de 30 dias mapeados por sector: 46 de 56 -->
Que cubre: como se armo el mapa, que se sondea y a que ritmo, la cobertura del aviso de nodo caido y cuantos reclamos caen en cada sector.
Estado: solo lectura (GET de UISP, ping y lectura de la base del bot). 0 escrituras en equipos. El sidecar corre con el mapa nuevo.
Datos maquina: artifacts/autoresearch/wave410_network_map.json. Codigo: tools/observability/sidecar_e2e/build_uisp_map.py.
Leer cuando: antes de elegir el proximo sector a migrar o de usar reclamos por sector como criterio.
<!-- /doc-head -->
# Stage 3070A: mapa de red y linea de base de toda la red (W410)

## 1. Mapa

- `build_uisp_map.py` lee `GET /devices` (607 equipos) y guarda en el repo solo UUID, nodo, celda y tipo: 26 sectores, 27 extremos PtP y 18 del registro.
- Sectores: modo ap-ptmp. PtP: ap-ptp y sta-ptp. Las estaciones de clientes no se mapean.
- Sin IP ni nombres de clientes en el repo. Las IP de gestion para la sonda quedan en `%LOCALAPPDATA%/FuturaMAX/sidecar_e2e/uisp_probe_targets.json`.

## 2. Sonda

- Cada sector y PtP activo nuevo: 1 eco cada 10 s, etiqueta airOS o LTU y STOCK_BASELINE. Los 18 del registro siguen a 1 por segundo.
- Nodos con minutos en los ultimos 10 min: 71. `check_stale.py` cubre los 71: 0 sin reportar.

## 3. Reclamos de 30 dias por celda (MEASURED)

| Celda | Reclamos | Clientes |
| :-- | --: | --: |
| sin_nodo | 10 | 10 |
| sector_ft_jose_l1 | 10 | 8 |
| sector_panel4_alma | 8 | 6 |
| sector_panel1_acvnew | 4 | 4 |
| sector_panel_2_guemes | 3 | 3 |
| sector_panel1_guemes | 3 | 3 |
| sector_edificio_panel_italia | 3 | 3 |
| sector_panel2_jh | 2 | 1 |
| sector_ft_12_l1 | 2 | 2 |
| sector_ft_12_1 | 2 | 2 |
| sector_panel3_jh | 1 | 1 |
| sector_panel3_alma | 1 | 1 |
| sector_panel1_jh | 1 | 1 |
| sector_panel1_baigorria | 1 | 1 |
| sector_panel1_alma | 1 | 1 |
| sector_ltu1_mas | 1 | 1 |
| sector_ft_jose_l2 | 1 | 1 |
| sector_ft_gue_l1 | 1 | 1 |
| panel1 | 1 | 1 |

- Mapeados: 46 de 56. Los que quedan sin nodo no tienen ruta de red guardada o su ruta no pasa por un sector del mapa.
- **Arreglo:** `locate()` solo reconocia nodos del registro; ahora usa el sector y despues el PtP. Tests: 19 passed in 1.10s.
