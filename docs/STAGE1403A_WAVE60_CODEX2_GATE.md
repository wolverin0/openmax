<!-- doc-head: Wave60: replay independiente y separacion de aceptacion observada, local y postflash -->
El gate usa las cuatro capturas originales, sus fuentes ejecutadas y recuperacion explicita.
Un PASS describe las desigualdades observadas y software local; no certifica poblacion ni flash.
<!-- /doc-head -->

# Stage 1403A - Gate de cierre

`python tools/verify/verify_stage1403a_wave60_codex2_gate.py --run-tests`
recalcula CPU, HTTP e ICMP desde RAW, verifica secuencia preregistrada, fuentes,
transiciones, watchdogs, restauracion ON, locks y ausencia de deriva RF.
La lista exacta de fuentes ejecutadas se resuelve a sus archivos preservados;
el parser recuperado se valida como fuente distinta, sin fingir nueva ejecucion.

Se auditan los ocho RAW de carga y las tres fases de cada radio/ventana.
Se conserva el error inicial, el control inmediato post-B2 ausente y la salud
real posterior a restauracion. La comparacion usa las medias de los cuatro
slots con margen cero, sin seleccionar muestras ni relajar por perdida ICMP.

1399 exige fuente694 intacta, fixtures Linux, overlays aislados y activos,
TAR/manifiestos exactos. 1400 exige baseline parcial y modo offline sin flash.
La suite nueva debe ejecutar todos sus casos con cero skips/fallos.

`implementation_and_local_gate_passed` expresa software y replay validos.
`no_regression_claim` solo expresa el contraste observado; certificacion
poblacional, ausencia causal de overhead y aceptacion postflash no se deducen.
Las regresiones historicas se reportan aparte con reproduccion de baseline:
250 PASS y siete fallos Wave48 tambien presentes con694. El gate exige que
las identidades JUnit de esos siete coincidan exactamente; no los omite.
