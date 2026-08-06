#!/bin/sh
# Builds the Stephan-OS ISO inside a Debian trixie Docker container,
# since live-build needs a Debian/Ubuntu host and the dev machine runs
# Manjaro. Run from the iso-build/ directory.
#
# Note: live-build only mounts /dev/pts into the chroot (see
# /usr/lib/live/build/chroot_devpts), not /dev itself - it relies on
# debootstrap's minimal static device nodes for everything else. That
# reproducibly broke /dev/null access ("Permission denied") partway
# through installing libreoffice-common's postinst script inside this
# Docker setup. Fix: bind-mount the host's real /dev over chroot/dev
# for the whole build, so every device node behaves like a normal host
# device instead of a container-local static one.
set -e

cd "$(dirname "$0")"

docker build -t stephan-os-builder .

docker run --rm -it \
  --privileged \
  --device-cgroup-rule='a *:* rmw' \
  -v "$(pwd)":/build \
  -w /build \
  stephan-os-builder \
  sh -c "lb clean --purge || true; mkdir -p chroot/dev && mount --bind /dev chroot/dev && auto/config && lb build; ret=\$?; umount chroot/dev 2>/dev/null || true; exit \$ret"
