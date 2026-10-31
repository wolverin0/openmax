<!-- doc-head: Wave60: regresiones locales de replay, GPIO y comparador sin red -->
La suite exige las cuatro ventanas y conserva perdidas y desvios de protocolo.
Los fixtures ejecutan shell Linux descartable; no conectan radios ni routers.
<!-- /doc-head -->

# Stage 1402A - Verificacion local

`tests/test_stage1398a_to_1403a_suite.py` valida el contraste estricto con
margen cero, rechaza datos incompletos/no finitos y prohibe certificacion
poblacional a partir de dos observaciones por brazo.

Incluye 19 fixtures de shell Linux para LiteBeam, corrupcion de identidad/GPIO,
comparador offline sin red, errores de candidato y contabilidad BusyBox 5/6
con perdida publicada entera16%. La perdida cientifica usa enviados/recibidos.
El replay adversario rechaza slots faltantes, cambio de brazo/media, falta de
restauracion, salud inventada, nuevas ventanas y deriva del archivo ejecutado.

El gate ejecuta coleccion y pytest, compara identidades JUnit y exige cero
omisiones/fallos. Guarda comandos, stdout/stderr y JUnit en
`artifacts/verification/stage1402a/`, enlazados desde el recibo1402.
Los intentos anteriores y la regresion red/green se conservan por separado;
no se presentan como evidencia RF ni como aceptacion visual.

La ejecucion final Linux registra 44/44 casos sin fallos ni skips.
El primer intento de la regresion BusyBox fallo por un import `re` ausente;
su XML red y el posterior green se preservaron, sin atribuir ese error al radio.
