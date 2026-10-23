set -eu
trap '' HUP
one=0; two=0; restore=0
cleanup() {
 trap - EXIT USR1 TERM INT
 set +e
 wpa_cli -i ath0 reconfigure
 rc=$?
 test "$one" = 0 || ebtables -D FORWARD -i ath0 -o eth0 -j DROP || rc=91
 test "$two" = 0 || ebtables -D FORWARD -i eth0 -o ath0 -j DROP || rc=92
 sleep 2
 primary=$(ip -4 addr show dev br0 | awk '/inet /{print $2;exit}')
 if test "$primary" = 169.254.213.210/16; then
  if ip -4 addr show dev br0 | grep -q 'inet 192.168.100.198/24'; then
   ip -4 addr del 169.254.213.210/16 dev br0 || rc=93
   ip -4 addr add 169.254.213.210/16 brd 169.254.255.255 dev br0 || rc=94
  else rc=95; fi
 fi
 printf 'ROCKET_RESTORE_RC=%s\n' "$rc"
 exit "$rc"
}
trap cleanup EXIT
trap 'exit 0' USR1 TERM INT
ebtables -I FORWARD -i ath0 -o eth0 -j DROP
one=1
ebtables -I FORWARD -i eth0 -o ath0 -j DROP
two=1
wpa_cli -i ath0 disable_network 0 | grep -q '^OK$'
printf 'READY %s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)"
end=$(($(cut -d. -f1 /proc/uptime)+1140))
while test "$(cut -d. -f1 /proc/uptime)" -lt "$end"; do sleep 1; done
