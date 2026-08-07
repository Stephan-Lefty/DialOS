#!/bin/sh
# Builds the DialOS ISO inside a Debian trixie Docker container,
# since live-build needs a Debian/Ubuntu host and the dev machine runs
# Manjaro. Run from the iso-build/ directory.
#
# Two chroot-environment quirks this works around (both discovered the
# hard way over several failed builds):
#
# 1. live-build only mounts /dev/pts into the chroot (see
#    /usr/lib/live/build/chroot_devpts), not /dev itself - it relies on
#    debootstrap's minimal static device nodes for everything else. That
#    reproducibly broke /dev/null access ("Permission denied") partway
#    through package postinst scripts. Fix: bind-mount just the specific
#    device files that broke (null, zero, random, urandom, full) from
#    the host, one by one - NOT the whole /dev directory. Bind-mounting
#    all of /dev shadows the devpts mount live-build already set up
#    inside chroot/dev/pts (silently, since the mount still exists in
#    the kernel's mount table but becomes unreachable at that path), so
#    its own teardown logic (grep for the mount + `umount
#    chroot/dev/pts`, no `|| true`) fails with "not mounted" and aborts
#    the whole build.
#
# 2. There is no D-Bus system bus running inside the chroot, which
#    makes some packages' postinst scripts fail - most notably
#    dictionaries-common, a hard transitive dependency of gnome-core
#    (via gnome-text-editor -> libspelling -> libenchant), so it can't
#    just be excluded. Fix: install the dbus package early (right after
#    chroot_prep, once apt sources are set up) and start a dbus-daemon
#    chrooted into chroot/ itself (not bind-mounted from the host), so
#    it creates its socket natively at chroot/run/dbus.
#
# Both fixes must be applied AFTER `lb bootstrap` and after
# `lb chroot_prep install` - debootstrap repopulates chroot/dev and
# chroot/run while unpacking the base system, which silently orphans
# anything mounted/started beforehand. Since `lb build`/`lb chroot` are
# monolithic (no hook point exists between chroot_prep and package
# installation), this script replicates live-build's own stage sequence
# (see /usr/lib/live/build/build and /usr/lib/live/build/chroot)
# manually so the fixes can be inserted at the right point.
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
    set -e
    lb clean --purge || true
    auto/config
    lb bootstrap

    lb chroot_cache restore
    lb chroot_prep install all mode-archives-chroot

    mkdir -p chroot/run/dbus
    for _DEV in null zero random urandom full; do
      touch chroot/dev/\$_DEV
      mount --bind /dev/\$_DEV chroot/dev/\$_DEV
    done
    chroot chroot apt-get install -y --no-install-recommends dbus
    chroot chroot dbus-daemon --system --fork

    lb chroot_linux-image
    lb chroot_firmware
    lb chroot_preseed
    lb chroot_includes_before_packages
    for _PASS in install live; do
      lb chroot_package-lists \$_PASS
      lb chroot_install-packages \$_PASS
    done
    lb chroot_includes_after_packages
    lb chroot_hooks
    lb chroot_hacks
    lb chroot_interactive

    chroot chroot pkill dbus-daemon || true

    lb chroot_prep remove all mode-archives-chroot
    for _DEV in null zero random urandom full; do
      umount chroot/dev/\$_DEV 2>/dev/null || true
    done
    lb chroot_cache save

    lb installer
    lb binary
    lb source
  "
