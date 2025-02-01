#!/bin/bash -e
# $1 destination
log "Installing radio server..."
if [ -d "${ROOTFS_DIR}/tmp/radio/" ]; then
    rm -fR "${ROOTFS_DIR}/tmp/radio/"
fi
cp -a files/rpi/home/pi/radio "${ROOTFS_DIR}/tmp/"
on_chroot << EOF
(cd /tmp/radio/ ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="/")
(cd /tmp/radio/ ; make CROSS_PREFIX=arm-linux-gnueabihf- ROOTFS_DIR="/" install)
EOF

log "Updating version info..."
echo "${RELEASE_INFO}" > files/rpi/etc/release.info

log "Copying file system..."
rsync -av --progress files/rpi/ "${ROOTFS_DIR}/"

cp "files/conf/${IMAGE_TYPE}/wpa_supplicant.conf" "${ROOTFS_DIR}/etc/wpa_supplicant/"
chmod 600 "${ROOTFS_DIR}/etc/wpa_supplicant/"
chown root:root "${ROOTFS_DIR}/etc/wpa_supplicant/wpa_supplicant.conf"

log "Configuring AMQP..."
on_chroot << EOF
#rabbitmqctl add_user smccedfw.petro UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe
#rabbitmqctl set_user_tags smccedfw.petro administrator
#rabbitmqctl set_permissions -p / smccedfw.petro ".*" ".*" ".*"
#systemctl enable rabbitmq-server
#rabbitmq-plugins enable rabbitmq_management
EOF

log "Configuring Petrobras user..."
on_chroot << EOF
if id "ptbr" &>/dev/null; then
    userdel ptbr
fi
useradd ptbr
adduser ptbr sudo
echo "ptbr:PtBr2022!" | sudo chpasswd
echo "pi:LmEst&22" | sudo chpasswd
EOF

