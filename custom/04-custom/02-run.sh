#!/bin/bash -e
# $1 destination

log "Instaling python dependencies"

on_chroot << EOF

apt-get install -y python3 python3-pip python3-zmq python3-tz python3-json-tricks python3-pika 
apt-get install -y python3-numpy python3-flask python3-serial python3-retry 
apt-get install -y libatlas-base-dev rabbitmq-server screen mc
apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf build-essential libtool pkg-config make

EOF

log "Installing PIGPIO..."
cp files/pigpio-79.zip  "${ROOTFS_DIR}/tmp/"
if [ -d  "${ROOTFS_DIR}/tmp/pigpio-79/" ]; then
    rm -fR "${ROOTFS_DIR}/tmp/pigpio-79/"
fi
on_chroot << EOF
unzip /tmp/pigpio-79.zip -d /tmp/
(cd /tmp/pigpio-79/ ; make CROSS_PREFIX=arm-linux-gnueabihf- DESTDIR="/")
(cd /tmp/pigpio-79/ ; make CROSS_PREFIX=arm-linux-gnueabihf- DESTDIR="/" install)
EOF

log "Installing ZEROMQ..."
if [ -d "${ROOTFS_DIR}/tmp/zeromq-4.3.5/" ]; then
    rm -fR "${ROOTFS_DIR}/tmp/zeromq-4.3.5/"
fi
cp files/zeromq-4.3.5.zip "${ROOTFS_DIR}/tmp/"
on_chroot << EOF
unzip /tmp/zeromq-4.3.5.zip -d /tmp
(cd /tmp/zeromq-4.3.5/ ; ./autogen.sh)
(cd /tmp/zeromq-4.3.5/ ; ./configure --enable-static --host=arm-linux-gnueabihf CC=arm-linux-gnueabihf-gcc CXX=arm-linux-gnueabihf-g++ --prefix="/")
(cd /tmp/zeromq-4.3.5/ ; make -j8)
(cd /tmp/zeromq-4.3.5/ ; make install)
EOF

log "Installing Multitimer..."
if [ -d "${ROOTFS_DIR}/tmp/multitimer-master/" ]; then
    rm -fR "${ROOTFS_DIR}/tmp/multitimer-master/"
fi
cp files/multitimer-master.zip "${ROOTFS_DIR}/tmp/"
on_chroot << EOF
unzip /tmp/multitimer-master.zip -d /tmp
(cd /tmp/multitimer-master/ ; python3 setup.py install)
EOF
