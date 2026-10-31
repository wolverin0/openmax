<!-- doc-head: 1327A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# WA v7 explicit universal LED companion overlay

Status: CONFIRMED_STATIC; atribucion: Linux/sysfs y empaquetado local.

Overlay explicito para WA v7: daemon nuevo con allowlist de cuatro placas, procd y configuracion.
PBE: blue:rssi0..3; LBE/NS Loco: blue:power; LAP-120: white:dome.
En placas de un LED representa enlace asociado; bars_lit sigue siendo RSSI logico 0..4.
Desconocido, identidad discrepante o banco RSSI parcial fallan antes de escribir LEDs.
TAR determinista conserva shell0755/config0644 incluso si DrvFS expone0777.
Extraer el TAR preservando modos en un root POSIX antes de un futuro empaquetado SquashFS.
El hook de primer inicio valida placa, habilita procd y arranca el indicador.
Las16 imagenes WA v7 existentes, canonical Wave44, overlay v17 y tuning quedan intactos.
No se reconstruyeron imagenes ni se ejecutaron SSH, flashes o pruebas fisicas.
