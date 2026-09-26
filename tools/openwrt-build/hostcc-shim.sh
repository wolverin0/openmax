#!/bin/bash
# FuturaMAX FMX-0011 — host-compiler shim (runs INSIDE WSL).
# Why: Ubuntu 24.04's gcc 13.3.0 hits a deterministic internal compiler error
# ("in try_forward_edges, at cfgcleanup.cc:580") compiling OpenWrt's host cmake 3.30.5
# (Source/cmLocalGenerator.cxx). gcc-12 builds it. OpenWrt's prereq picks the host
# compiler via `command -v gcc|g++`, so putting this dir first in PATH is enough.
set -eu
SHIM="$HOME/futuramax/hostcc-shim"
mkdir -p "$SHIM"
ln -sf /usr/bin/gcc-12 "$SHIM/gcc"
ln -sf /usr/bin/gcc-12 "$SHIM/cc"
ln -sf /usr/bin/g++-12 "$SHIM/g++"
ln -sf /usr/bin/g++-12 "$SHIM/c++"
echo "shim at $SHIM:"; ls -l "$SHIM"
PATH="$SHIM:$PATH" gcc --version | head -1
PATH="$SHIM:$PATH" g++ --version | head -1
