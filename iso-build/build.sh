#!/bin/sh
# Builds the Stephan-OS ISO inside a Debian trixie Docker container,
# since live-build needs a Debian/Ubuntu host and the dev machine runs
# Manjaro. Run from the iso-build/ directory.
set -e

cd "$(dirname "$0")"

docker build -t stephan-os-builder .

docker run --rm -it \
  --privileged \
  -v "$(pwd)":/build \
  -w /build \
  stephan-os-builder \
  sh -c "lb clean --purge || true; auto/config && lb build"
