#!/bin/sh
set -eu
D=/tmp/fmx-step1c-ap-observer-cbf580bace28e33f9138b2a6ef4b746a
TOKEN=cbf580bace28e33f9138b2a6ef4b746a
test ! -L "$D"; test -d "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = "drwx------ 0 0"
test ! -L "$D/owner"; test "$(cat "$D/owner")" = "$TOKEN"

wifi down radio0
if ! mkdir "$D/restoring"; then
 for n in 1 2 3 4; do test -f "$D/restored" && exit 0; sleep 1; done
 exit 80
fi
trap 'rmdir "$D/restoring"' EXIT
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a
test "$(sha256sum /etc/config/network | awk '{print $1}')" = d273ab6bece9a950b119a4fc6c0f6f076543e4a88ab7346760e02d211b403015
changes=$(uci changes wireless)
printf '%s
' "$changes" | while IFS= read -r row; do
 case "$row" in ""|"wireless.radio0.disabled='0'"|"wireless.radio0.txpower='0'"|"wireless.default_radio0.wds='1'"|"wireless.default_radio0.encryption='none'"|"wireless.default_radio0.encryption='psk2'") ;; *) exit 81;; esac
done
test "$(uci -q get wireless.radio0.disabled)" = 0 -o "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 0 -o "$(uci -q get wireless.radio0.txpower)" = 18
if printf '%s
' "$changes" | grep -q "^wireless.radio0.disabled="; then uci revert wireless.radio0.disabled; fi
if printf '%s
' "$changes" | grep -q "^wireless.radio0.txpower="; then uci revert wireless.radio0.txpower; fi
if printf '%s
' "$changes" | grep -q "^wireless.default_radio0.wds="; then uci revert wireless.default_radio0.wds; fi
if printf '%s
' "$changes" | grep -q "^wireless.default_radio0.encryption="; then uci revert wireless.default_radio0.encryption; fi
test -z "$(uci changes wireless)"
test "$(uci -q get wireless.default_radio0.wds)" = 0
test "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 18
ubus call network reload >/dev/null
wifi down radio0
fmx_wireless=$(ubus -t 4 call network.wireless status)
test "$(jsonfilter -s "$fmx_wireless" -e '@.radio0.up')" = false
fmx_devs=$(iw dev)
test -z "$(printf "%s\n" "$fmx_devs" | awk '$1=="Interface" {print $2}')"
fmx_tables=$(nft list tables)
if printf "%s\n" "$fmx_tables" | grep -Fx "table bridge fmx_preprod_cbf580bace28e33f9138b2a6ef4b746a" >/dev/null; then
 fmx_table=$(nft -j list table bridge fmx_preprod_cbf580bace28e33f9138b2a6ef4b746a)
 fmx_owner=$(jsonfilter -s "$fmx_table" -e '@.nftables[*].table.comment')
 test "$fmx_owner" = cbf580bace28e33f9138b2a6ef4b746a
 nft delete table bridge fmx_preprod_cbf580bace28e33f9138b2a6ef4b746a
fi
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/24 '; then ip addr del 10.99.0.1/24 dev br-lan; fi
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/'; then exit 82; fi
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a
: > "$D/restored"
echo RESTORE_OK
