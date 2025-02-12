#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Uso: $0 [lte|wifi] src_dir dst_dir"
  exit 1
fi

export IMAGE_TYPE="$1"
export SRC_DIR="$2"
export DST_DIR="$3"

echo "Copying common files..."
rsync -av --progress "$SRC_DIR/" "$DST_DIR/"

echo "Copying conf files..."
mkdir -p "$DST_DIR/etc/wpa_supplicant/"
cp "$SRC_DIR/home/pi/scripts/conf/${IMAGE_TYPE}/wpa_supplicant.conf" "$DST_DIR/etc/wpa_supplicant/"
chmod 600 "$DST_DIR/etc/wpa_supplicant/wpa_supplicant.conf"
chown root:root "$DST_DIR/etc/wpa_supplicant/wpa_supplicant.conf"

cp "$SRC_DIR/home/pi/scripts/conf/${IMAGE_TYPE}/hub_config.ini" "$DST_DIR/home/pi/hub_config.ini"
