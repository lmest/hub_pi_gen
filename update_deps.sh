#!/bin/bash

PROGS="coreutils quilt parted qemu-user-static debootstrap zerofree zip \
      dosfstools libarchive-tools libcap2-bin grep rsync xz-utils file git curl bc \
      gpg pigz xxd arch-test mc gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf\
      build-essential libtool pkg-config make python3 python3-pip"

apt update -y
apt upgrade -y
apt-get install -y $PROGS

