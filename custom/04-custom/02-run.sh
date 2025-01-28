#!/bin/bash -e
# $1 destination
log "Installing PIGPIO..."
unzip files/pigpio-79.zip -d "${STAGE_WORK_DIR}/"
(cd "${STAGE_WORK_DIR}/pigpio-79/" ; make CROSS_PREFIX=arm-linux-gnueabihf- DESTDIR="${ROOTFS_DIR}/")
(cd "${STAGE_WORK_DIR}/pigpio-79/" ; make CROSS_PREFIX=arm-linux-gnueabihf- DESTDIR="${ROOTFS_DIR}/" install)

log "Installing ZEROMQ..."
unzip files/zeromq-4.3.5.zip -d "${STAGE_WORK_DIR}/"
(cd "${STAGE_WORK_DIR}/zeromq-4.3.5/" ; ./autogen.sh)
(cd "${STAGE_WORK_DIR}/zeromq-4.3.5/" ; ./configure --enable-static --host=arm-linux-gnueabihf CC=arm-linux-gnueabihf-gcc CXX=arm-linux-gnueabihf-g++ --prefix="${ROOTFS_DIR}/")
(cd "${STAGE_WORK_DIR}/zeromq-4.3.5/" ; make)
(cd "${STAGE_WORK_DIR}/zeromq-4.3.5/" ; make install)


