#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Uso: $0 [lte|wifi] version_tag"
  exit 1
fi

export IMAGE_TYPE="$1"
export RELEASE_INFO="$2"

if [ $IMAGE_TYPE != "lte" ] && [ $IMAGE_TYPE != "wifi" ]; then
  echo "Uso: $0 [lte|wifi] version_tag"
  exit 1
fi

# config file
cat <<EOF > ./pi-gen/config
IMG_NAME="hub_$IMAGE_TYPE"
#PI_GEN_RELEASE="UFU-PETROBRAS $VER"
KEYBOARD_KEYMAP="us"
KEYBOARD_LAYOUT="English (US)"
TIMEZONE_DEFAULT="America/Sao_Paulo"
FIRST_USER_NAME="pi"
FIRST_USER_PASS="LmEst&UFU22"
WPA_COUNTRY="BR"
LOCALE_DEFAULT="en_US.UTF-8"
#USE_QEMU=1
EOF

# remove UI stages
touch ./pi-gen/stage3/SKIP ./pi-gen/stage4/SKIP ./pi-gen/stage5/SKIP
touch ./pi-gen/stage4/SKIP_IMAGES ./pi-gen/stage5/SKIP_IMAGES

# add custom files
cp -a custom/04-custom ./pi-gen/stage2/

(cd pi-gen ; ./build.sh)


