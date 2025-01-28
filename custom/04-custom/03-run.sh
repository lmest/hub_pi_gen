#!/bin/bash -e
# $1 destination
log "Installing SERVER..."
cp -a files/radio "${ROOTFS_DIR}/tmp"

(cd "${STAGE_WORK_DIR}/radio/" ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="${ROOTFS_DIR}/")
(cd "${STAGE_WORK_DIR}/radio/" ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="${ROOTFS_DIR}/" install)

# Updating version info
echo "${RELEASE_INFO}" > "${ROOTFS_DIR}/etc/release.info"

