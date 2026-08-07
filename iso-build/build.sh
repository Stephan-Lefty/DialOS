#!/bin/sh
# Builds the DialOS ISO inside a Debian trixie Docker container,
# since live-build needs a Debian/Ubuntu host and the dev machine runs
# Manjaro. Run from the iso-build/ directory.
#
# Notes on two chroot-environment quirks this works around:
#
# 1. live-build only mounts /dev/pts into the chroot (see
#    /usr/lib/live/build/chroot_devpts), not /dev itself - it relies on
#    debootstrap's minimal static device nodes for everything else. That
#    reproducibly broke /dev/null access ("Permission denied") partway
#    through package postinst scripts. Fix: bind-mount the host's real
#    /dev over chroot/dev for the whole build.
#
# 2. There is no D-Bus system bus running inside the chroot (nothing
#    started it), which makes some packages' postinst scripts fail -
#    most notably dictionaries-common, a hard transitive dependency of
#    gnome-core (via gnome-text-editor -> libspelling -> libenchant),
#    so it can't just be excluded. Fix: start a real dbus-daemon in
#    this outer container and bind-mount its socket directory into
#    chroot/run/dbus, so chroot'd processes can reach a working bus.
set -e

cd "$(dirname "$0")"

docker build -t dialos-builder .

docker run --rm -it \
  --privileged \
  --device-cgroup-rule='a *:* rmw' \
  -v "$(pwd)":/build \
  -w /build \
  dialos-builder \
  sh -c "
    lb clean --purge || true
    mkdir -p /run/dbus
    dbus-daemon --system --fork
    mkdir -p chroot/dev chroot/run/dbus
    mount --bind /dev chroot/dev
    mount --bind /run/dbus chroot/run/dbus
    auto/config && lb build
    ret=\$?
    umount chroot/run/dbus 2>/dev/null || true
    umount chroot/dev 2>/dev/null || true
    exit \$ret
  "
