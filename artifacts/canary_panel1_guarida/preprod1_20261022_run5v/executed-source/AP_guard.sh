#!/bin/sh
trap '' HUP
set -eu
D=/tmp/fmx-step1c-ap-observer-498349ace66a0a4706a66b1daef56ea3
TOKEN=498349ace66a0a4706a66b1daef56ea3
test ! -L "$D"; test -d "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = "drwx------ 0 0"
test ! -L "$D/owner"; test "$(cat "$D/owner")" = "$TOKEN"

printf '%s %s
' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/guard.id"
end=$(($(cut -d. -f1 /proc/uptime)+1200))
echo "$end" > "$D/deadline"
: > "$D/ready"
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do
 test ! -f "$D/restored" || exit 0
 sleep 1
done
/bin/sh "$D/restore.sh" > "$D/restore.log" 2>&1
