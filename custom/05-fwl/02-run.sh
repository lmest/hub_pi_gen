#!/bin/bash -e
# $1 destination

log "-----------------------------------------------------"
log "          Full Wireless custom files"
log "-----------------------------------------------------"
#log "Installing Multitimer..."
#if [ -d "${ROOTFS_DIR}/tmp/multitimer-master/" ]; then
#    rm -fR "${ROOTFS_DIR}/tmp/multitimer-master/"
#fi
#cp files/multitimer-master.zip "${ROOTFS_DIR}/tmp/"
#on_chroot << EOF
#unzip /tmp/multitimer-master.zip -d /tmp
#(cd /tmp/multitimer-master/ ; python3 setup.py install)
#EOF

log "Installing pip dependencies: atcom, multitimer, pyserial"
#if [ -d "${ROOTFS_DIR}/tmp/atcom-master/" ]; then
#    rm -fR "${ROOTFS_DIR}/tmp/atcom-master/"
#fi
#cp files/atcom-master.zip "${ROOTFS_DIR}/tmp/"
#on_chroot << EOF
#unzip /tmp/atcom-master.zip -d /tmp
#(cd /tmp/atcom-master/ ; python3 setup.py install)
#EOF
on_chroot << EOF
pip3 install atcom multitimer pyserial --break-system-packages 
EOF

if [ ${IMAGE_TYPE} = "lte" ]; then
    log "Installing Sixfab PPP support..."
    if [ -d "${ROOTFS_DIR}/tmp/Sixfab_PPP_Installer-master/" ]; then
        rm -fR "${ROOTFS_DIR}/tmp/Sixfab_PPP_Installer-master/"
    fi
    cp files/Sixfab_PPP_Installer-master.zip "${ROOTFS_DIR}/tmp/"
    on_chroot << EOF
    unzip /tmp/Sixfab_PPP_Installer-master.zip -d /tmp
    (cd /tmp/Sixfab_PPP_Installer-master/ ; chmod +x ppp_install.sh ; ./ppp_install.sh)
EOF
fi

log "Removing swap..."
on_chroot << EOF
sudo apt remove -y --purge dphys-swapfile
if [ -f /var/swap ]; then
    sudo rm /var/swap
fi
EOF
