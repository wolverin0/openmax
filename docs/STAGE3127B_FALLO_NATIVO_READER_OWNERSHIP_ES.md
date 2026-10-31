<!-- doc-head: W460b fallo nativo del helper spectral final antes del trigger -->
El pin 1e03793b se instalo y verifico en el LiteBeam .116; la captura fallo rc 65.
No se cambia el piso de memoria ni se edita el helper del repositorio sin ampliar scope.
<!-- /doc-head -->

# Carrera del reader observada en banco

Se reinicio una sola vez el LiteBeam autorizado y cambio su boot ID.
La clave SSH coincide. El helper instalado tiene exactamente SHA-256
`1e03793b32cb29f97bfa59c1060c2fbfc88a29337c49c305ae1d1da8f7a18099`.

La primera captura nativa final fallo antes de escribir manual/trigger:

```text
status=FAILED reason=READER_OWNERSHIP rc=65
line 111: can't open /proc/2082/stat: no such file
```

MemAvailable previo: 11732 KiB, superior al piso inalterado de 6144 KiB.
Readback posterior: mode=disable, count=0, MemAvailable=11704 KiB;
guard.ready y guard.done existen. El fallo y stdout/stderr se conservan en el recibo.
No se presenta como captura exitosa ni se reemplaza por evidencia historica.

## Diagnostico

CONFIRMED: el PID del `dd` ya no existe al intentar leer su `/proc/PID/stat`.
INFERRED: el drain de un relay vacio termino antes de registrar su identidad.
El codigo exige un reader vivo incluso si un hijo propio ya termino correctamente.
El motivo preciso del fin de ese primer `dd` no se puede conocer porque el fallo
actual no recoge su wait status. No se atribuye de antemano un exit 0.

## Reparacion minima propuesta, sin aplicar

Si el reader sigue vivo, conservar registro PID/starttime para el guardian.
Si ya termino, recoger su exit status real con `wait`: aceptar solo 0 y no esperar
de nuevo un PID vacio. Si el reader esta vivo pero su identidad no se puede leer,
seguir rechazando la captura. No agregar sleeps, bajar el piso ni ignorar errores.

```diff
- if IFS= read -r line < /proc/$reader/stat;then
+ if IFS= read -r line < /proc/$reader/stat 2>/dev/null;then
    # conservar la validacion y publicacion PID/starttime actual
  fi
+ if ! kill -0 "$reader" 2>/dev/null;then
+  wait "$reader";reader_rc=$?;reader=
+  [ "$reader_rc" = 0 ] || return 1
+  return 0
+ fi
  return 1
```

En ambos sitios que lanzan `dd`, tras `own_reader`:

```diff
- wait "$reader";rc=$?;reader=;[ "$rc" = 0 ] || fail RELAY_DRAIN 70
+ rc=0
+ if [ -n "$reader" ];then wait "$reader";rc=$?;reader=;fi
+ [ "$rc" = 0 ] || fail RELAY_DRAIN 70
```

El segundo sitio conserva `RELAY_CAPTURE`. Son fragmentos de cambio, no un patch
aplicado ni una aceptacion del helper nuevo. La integracion exacta requiere ampliar
scope a la fuente y su suite, fijar el nuevo hash y repetir captura nativa.

Tests propuestos: hijo ya terminado exit 0, hijo exit distinto de 0, reader vivo
con identidad valida/invalida y reader bloqueado bajo guardian independiente.
Todos deben conservar readback disable/count y la propagacion de fallos.
Las imagenes W460 permanecen selladas al pin anterior; no se reempaquetan aqui.
