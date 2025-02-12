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
TIMEZONE_DEFAULT="America/Sao_Paulo"
FIRST_USER_NAME="pi"
FIRST_USER_PASS="LmEst&UFU22"
WPA_COUNTRY="BR"
KEYBOARD_KEYMAP="us"
KEYBOARD_LAYOUT="English (US)"
LOCALE_DEFAULT="en_US.UTF-8"
#USE_QEMU=1
EOF

export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# remove UI stages
touch ./pi-gen/stage3/SKIP ./pi-gen/stage4/SKIP ./pi-gen/stage5/SKIP
touch ./pi-gen/stage4/SKIP_IMAGES ./pi-gen/stage5/SKIP_IMAGES

# add custom files
rm -fR ./pi-gen/stage2/04-remove
rm -fR ./pi-gen/stage2/05-packages
rm -fR ./pi-gen/stage2/06-fwl

cp custom/prerun.sh      ./pi-gen/export-image/prerun.sh
cp -a custom/04-remove   ./pi-gen/stage2/
cp -a custom/05-packages ./pi-gen/stage2/
cp -a custom/06-fwl      ./pi-gen/stage2/

(cd pi-gen ; ./build.sh)


