FROM debian:trixie

RUN apt-get update && apt-get install -y --no-install-recommends \
    live-build \
    live-config \
    live-boot \
    debootstrap \
    ca-certificates \
    curl \
    wget \
    gnupg \
    xz-utils \
    squashfs-tools \
    dosfstools \
    xorriso \
    isolinux \
    syslinux-common \
    fakeroot \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
