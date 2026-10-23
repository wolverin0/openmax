#!/bin/sh
trap '' HUP
set -eu
D=/tmp/fmx-step1c-ap-observer-f6c0ebff69eb9f7db0f62d982d302789
TOKEN=f6c0ebff69eb9f7db0f62d982d302789
test ! -L "$D"; test -d "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = "drwx------ 0 0"
test ! -L "$D/owner"; test "$(cat "$D/owner")" = "$TOKEN"

printf '%s %s
' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/guard.id"
end=$(($(cut -d. -f1 /proc/uptime)+480))
echo "$end" > "$D/deadline"
: > "$D/ready"
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do
 test ! -f "$D/restored" || exit 0
 sleep 1
done
/bin/sh "$D/restore.sh" > "$D/restore.log" 2>&1
