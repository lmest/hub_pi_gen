#!/bin/bash

if [ -z "$1" ]; then
  echo "Uso: $0 versao"
  exit 1
fi

export RELEASE_INFO="$1"

# config file
cat <<EOF > ./pi-gen/config
IMG_NAME="hub"
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


