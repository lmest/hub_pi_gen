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
echo "${IMAGE_TYPE} ${RELEASE_INFO}" > files/rpi/etc/release.info

log "Copying file system..."
rsync -av --progress files/rpi/ "${ROOTFS_DIR}/"

mkdir -p "$DST_DIR/etc/wpa_supplicant/"
cp "files/rpi/home/pi/scripts/conf/${IMAGE_TYPE}/wpa_supplicant.conf" "${ROOTFS_DIR}/etc/wpa_supplicant/"
chmod 600 "${ROOTFS_DIR}/etc/wpa_supplicant/wpa_supplicant.conf"
chown root:root "${ROOTFS_DIR}/etc/wpa_supplicant/wpa_supplicant.conf"
cp "files/rpi/home/pi/scripts/conf/${IMAGE_TYPE}/hub_config.ini" "${ROOTFS_DIR}/home/pi/hub_config.ini"

log "Configuring Petrobras user..."
on_chroot << EOF
if id "ptbr" &>/dev/null; then
    userdel ptbr
fi
useradd ptbr
adduser ptbr sudo
adduser pi dialout
echo "ptbr:PtBr2022!" | sudo chpasswd
echo "pi:LmEst&UFU22" | sudo chpasswd
EOF

log "Fixing permissions..."
on_chroot << EOF
(cd /home/pi/ ; sudo chown -R pi:pi *)
(cd /etc/ ; sudo chown -R root:root *)
(cd /etc/ ; sudo chmod a+x rc.local)
chmod 755 /home/pi/radio/fwl_hub
chmod 755 /home/pi/scripts/*.sh
chmod 755 /home/pi/scripts/*.py
EOF
