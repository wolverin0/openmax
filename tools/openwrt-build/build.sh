#!/bin/bash
# FuturaMAX FMX-0011 — reproducible OpenWrt build driver (runs INSIDE WSL, foreground of run-attached.sh).
# Usage: see run-attached.sh. Writes START/DOWNLOAD_EXIT/MAKE_ATTEMPT/BUILD_EXIT lines with real exit codes.
# Do NOT write this file through `wsl -- bash -c '<<EOF'` — the outer shell expands $(...) at write time.
#
# Retry policy (2026-09-26): this WSL VM (kernel 6.18.33.2, autoMemoryReclaim=gradual) produces RANDOM
# compiler crashes (gcc-13 ICE, gcc-12 segfault, target lto1 ICE) that do not reproduce on rerun.
# make resumes from stamps, so a failed attempt is retried. Bounded: MAX_ATTEMPTS, and abort early if
# the SAME package fails SAME_LIMIT times in a row (that is a real error, not flakiness).
set -u
cd ~/futuramax/openwrt-24.10.4 || exit 97
LOG="$HOME/futuramax/openwrt-24.10.4/logs/futuramax-build.log"
JOBS="${JOBS:-6}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-12}"
SAME_LIMIT="${SAME_LIMIT:-3}"
# Clean Linux-only PATH: WSL appends the Windows PATH (entries with spaces, e.g. "Program Files"),
# which makes `find -execdir` in package/install abort with "relative path ... is included in PATH".
export PATH="$HOME/futuramax/hostcc-shim:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
# Point the staging host compiler at the shim explicitly. (Deleting the links is NOT enough:
# the prereq check is stamped in staging_dir/host/.prereq-build and does not re-run.)
mkdir -p staging_dir/host/bin
ln -sf "$HOME/futuramax/hostcc-shim/gcc" staging_dir/host/bin/gcc
ln -sf "$HOME/futuramax/hostcc-shim/g++" staging_dir/host/bin/g++
echo "START $(date -Is) commit=$(git rev-parse --short HEAD) tag=$(git describe --tags 2>/dev/null) hostcc=$(command -v gcc) jobs=$JOBS"
make -j"$JOBS" download 2>&1 | tail -3
dl=${PIPESTATUS[0]}
echo "DOWNLOAD_EXIT=${dl} $(date -Is)"
[ "$dl" -eq 0 ] || exit "$dl"

attempt=0; last_err=""; same=0; b=1
while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
  attempt=$((attempt + 1))
  echo "MAKE_ATTEMPT=${attempt} $(date -Is)"
  make -j"$JOBS" 2>&1
  b=$?
  [ "$b" -eq 0 ] && break
  err=$(grep -E "ERROR: .* failed to build" "$LOG" 2>/dev/null | tail -1)
  if [ -n "$err" ] && [ "$err" = "$last_err" ]; then same=$((same + 1)); else same=1; fi
  last_err="$err"
  echo "MAKE_FAILED attempt=${attempt} rc=${b} same=${same} err=[${err}] $(date -Is)"
  if [ "$same" -ge "$SAME_LIMIT" ]; then echo "GIVING_UP: same failure ${same}x -> real error, not flakiness"; break; fi
  sleep 5
done
echo "BUILD_EXIT=${b} attempts=${attempt} $(date -Is)"
exit "$b"
