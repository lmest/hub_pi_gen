#!/bin/bash -e
# $1 destination
log "Installing radio server..."
if [ -d "${ROOTFS_DIR}/tmp/radio/" ]; then
    rm -fR "${ROOTFS_DIR}/tmp/radio/"
fi
cp -a files/radio "${ROOTFS_DIR}/tmp/"
on_chroot << EOF
(cd /tmp/radio/ ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="/")
(cd /tmp/radio/ ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="/" install)
EOF

log "Updating version info..."
echo "${RELEASE_INFO}" > files/rpi/etc/release.info

log "Copying file system..."
rsync -av --progress files/rpi/ "${ROOTFS_DIR}/"
