#!/bin/bash -e
# $1 destination

log "Instaling python dependencies"

on_chroot << EOF

apt-get install -y python3 python3-pip

#pip install pyzmq==25.0.0
#pip install pytz==2019.3
#pip install json-tricks==3.14.0
#pip install pika==1.1.0
#pip install numpy==1.18.1
#pip install multitimer==0.3
#pip install flask==2.2.2
#pip install serial==3.5
#pip install retry==0.9.2

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

