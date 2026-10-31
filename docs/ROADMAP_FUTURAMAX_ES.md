<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: ROADMAP UNICO de FuturaMAX (ES). Lista de todo lo pedido por el operador, con estado, dueno y siguiente paso. Lo actualiza solo el orquestador en cada cierre de ronda. Reemplaza como punto de entrada a los planes dispersos. -->
# Roadmap unico de FuturaMAX

Este es el UNICO lugar para ver que esta pedido, que se esta haciendo y que sigue.
Reglas: lo actualiza el orquestador (lane_5) al cerrar cada ronda; cada fila tiene dueno y siguiente paso;
nada se borra, se marca HECHO o DESCARTADO con el motivo. Asignacion tecnica por ronda: `orchestration/master_orchestrator_state.json`.
Horas en hora local de Argentina.
Lista corta, una linea por tarea y por panel: `docs/PENDIENTES_POR_PANEL_ES.md`.

## 0. Ahora (bloquea todo lo demas)

| # | Tarea | Dueno | Estado | Siguiente paso |
|---|---|---|---|---|
| 0.1 | Instalar el admitter corregido (logs acotados) en Panel3, Panel1, Panel2 | lane_2 | EN CURSO desde 18:45 | Panel3 30 min, luego Panel1 y Panel2 10 min c/u |
| 0.2 | Monitoreo 12 h de memoria y /tmp en los 3 AP | lane_5 | EN CURSO hasta ~06:30 | alarma si MemAvailable < 6 MB o /tmp crece > 1 MB en 2 h |
| 0.3 | Kit de reparacion de .84: printf -> echo y renovacion del watchdog | lane_1 | EN CURSO | probar en qemu con el fallo real de printf |
| 0.4 | Valores de cola de .84 | lane_5 | EN ESPERA | no cambiar sin medicion; falta carga > 80 Mbps en banco |
| 0.5 | Verificar en UISP que Panel3 (.83) sigue conectado | operador | PENDIENTE | mirar el dashboard de UISP |

Causa de la caida del 29/10 (cerrada): `tools/panel1/panel1_admitter.sh` escribia sin tope en /tmp (RAM) de los 3 AP,
y udapi-bridge en Panel3 con `-v -l /tmp/...`. Detalle: `docs/STAGE2872A_INCIDENTE_PANEL1_29_10_ES.md`, `docs/STAGE2896A_CAUSA_RAIZ_Y_ARREGLO_MEMORIA_PANEL1_AP_ES.md`, `docs/STAGE2945A_ADMITTER_LOG_ACOTADO_ES.md`.

## 1. Pedidos del operador (lista viva)

| # | Pedido | Estado real | Dueno | Siguiente paso |
|---|---|---|---|---|
| 1.1 | Rollout a produccion (Panel1/2/3, PtP-Colo) con seguro de vuelta atras | BLOQUEADO hasta 0.1-0.3 | lane_5 | runbooks STAGE1131A y STAGE1700A; watchdog nuevo `tools/watchdog_acceptance/fmx_watchdog.sh` |
| 1.2 | Banco PtMP: LAP-120 .20 + Loco 5AC .250 + XC .198 + LiteBeam M5 .4 (multi tecnologia) | PARCIAL: banco usable; Loco .250 cambio de host key | lane_1 | generar > 80 Mbps hacia el AP (puerto gigabit u otro equipo) |
| 1.3 | Banco PtP: 2x PowerBeam 5AC .241/.242 | SIN TRABAJO HOY | sin asignar | releer estado y campeon real v18 (Stage 52A, no 1485A) |
| 1.4 | Banco LTU: LTU-Lite .110 (+ Lite #2, Rocket LTU) | PARADO desde W276 | sin asignar | clave del snapshot 1135A |
| 1.5 | SXT de MikroTik en el banco | SIN DATOS en el repo | sin asignar | operador confirma IP y rol |
| 1.6 | hyperresearch + scholar (metodo de investigacion) | POCO USO HOY | lane_3 | investigacion de presupuesto de memoria y colas en AP de 64 MB |
| 1.7 | Ground-up / primeros principios / ideas no documentadas | DOCS existen, sin ronda activa | lane_3 | `docs/GROUND_UP_FIRST_PRINCIPLES_5PILLARS_MASTER_BLUEPRINT.md` |
| 1.8 | Autoresearch (A1-B1-A2-B2) | runners listos, sin corridas | lane_5 | correr solo con watchdog con renovacion (0.3) |
| 1.9 | Observabilidad ya instalada: Prometheus :9090 y Grafana :3400 en PUBLIC_TERM_0003, Kuma en NAS, UISP, Command Center :8787 | Prometheus raspa 5 targets, incluido fmx-site-aware :9297 (W262); NO raspa el exporter de memoria :9118 (escucha solo en loopback) | lane_2 + dueno infra | exporter a la LAN y target nuevo en PUBLIC_TERM_0003 (lo agrega el dueno infra); ver docs/STAGE2969A_INVENTARIO_OBSERVABILIDAD_ES.md |
| 1.10 | OpenWISP | NO CORRE (PUBLIC_TERM_0003 :18080 sin respuesta) | operador | decidir si se usa o se descarta |
| 1.11 | airControl2 | NO FIGURA en infra/PLACEMENT.md ni SYSTEM.md | operador | decir donde corre o si ya no se usa |
| 1.12 | Regulatorio: Panel1 en regdomain US 23 dBm (AR 17 dBm) | DECISION DEL OPERADOR | operador | decidir |
| 1.13 | Higiene de /tmp en todos los scripts (47 archivos) | CHEQUEO LISTO, sin limpiar | duenos de cada carpeta | `python tools/verify/check_device_tmp_hygiene.py` |
| 1.14 | Centralizar planes y no olvidar pedidos | ESTE ARCHIVO | lane_5 | mantenerlo al cerrar cada ronda |
| 1.15 | Builders de Panel2/Panel3 no coinciden con lo instalado (IGNORE_MACS del admitter en Panel3) | DETECTADO 29/10 | lane_2 registra, lane_1 reconcilia | traer al repo la config real de cada AP antes de cualquier reimagen |

## 2. Orden de trabajo

1. Seccion 0 completa (incidente cerrado y monitoreado).
2. Observabilidad conectada a lo que ya existe (1.9) para no depender de mirar a mano.
3. Kits con watchdog probado en banco real, luego rollout de a un equipo (1.1, 1.2).
4. Bancos PtP y LTU (1.3, 1.4) y metodo de investigacion (1.6, 1.7, 1.8) en paralelo.

## 3. Reglas aprendidas el 29/10

- Medir antes de proponer arreglos: primera ronda de todo incidente = que consume / que cambio.
- Ningun script en equipos escribe sin tope en /tmp; los logs van con tope o a logd.
- Todo cambio de colas o sysctl se prueba primero en banco con carga real.
- OpenWrt 24.10 no trae `timeout` ni `nohup`; en debugfs de aqm escribir con `echo`, no con `printf`.
- Si un panel falla una tarea, se reasigna.
