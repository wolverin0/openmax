<!-- doc-head: Stage 3052A (W392) ES: el PtP LTU del banco y su A/B no se corrieron porque el LTU-Lite 2 sigue sin responder por LAN ni por RF y no llego la confirmacion de PoE del operador. Lectura sola de .110: AP-PTMP arriba en RAM, 0 enlaces y 84 C en los cuatro sensores, sin guarda termica -->
Que cubre: la precondicion de la ola, el estado leido de .110 y por que se detuvo.
Estado: solo lectura. 0 escrituras en .110 y 0 en /dev/ame. El PtP y el A/B no se intentaron.
Datos maquina: artifacts/autoresearch/wave392_ltu_ptp_ab.json.
Leer cuando: antes de relanzar el PtP del banco LTU o de decidir que hacer con la temperatura de .110.
<!-- /doc-head -->
# Stage 3052A: PtP LTU y A/B detenidos sin par (W392)

## 1. Precondicion

- **Confirmacion de PoE del LTU-Lite 2:** no llego en esta sesion.
- **LAN del LTU-Lite 2:** 0 de 10 ecos desde el host y sin respuesta desde .110.
- Segun el despacho, sin respuesta se reporta y se detiene: no se intento el PtP ni el A/B.

## 2. Estado de .110 (CONFIRMED_LIVE_READONLY, 2026-10-30T14:42:57Z)

- AP-PTMP en RAM desde W383, ath0 up, powerout -4, 0 enlaces.
- Temperatura 84/84/84/84 C (temp0, temp1, rtemp0, rtemp1). En W383 el ultimo cuadro fue 79 C; el corte del 27/10 fue a 73 C.
- La radio sigue transmitiendo sin par y sin guarda termica, por decision de W378.

## 3. Que hace falta

- Operador: dar PoE al LTU-Lite 2 y decidir si .110 sigue encendido sin par mientras tanto.
- Despues, una ola con el par en LAN establece el PtP y corre el A/B con registro de temperatura.
- **Karpathy: TARGET_NOT_MET.** Sin enlace no hay snapshots ni A/B; ame_device_writes 0.
