#!/bin/sh
# Historical WA v12 actuator is retired. No getters, mutation or delegation.
set -eu
MODE="${1:---inspect}"
case "$MODE" in
  --inspect|--inspect-only|--dry-run)
    [ "$#" -le 1 ] || { printf '%s\n' 'RETIRED unsupported inspection arguments' >&2; exit 64; }
    printf '%s\n' 'PLANNED_RETIRED wa_version=v12 runtime=UNKNOWN'
    printf '%s\n' 'canonical=firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh explicit_identity_contract_required=true'
    ;;
  *)
    printf '%s\n' 'RETIRED wa_version=v12 apply_refused=true canonical=firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh' >&2
    exit 64
    ;;
esac
