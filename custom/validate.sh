#!/bin/bash

log() {
  echo "$1"
}

export -f log

rm -fR /home/marcelo/temp/work
mkdir -p /home/marcelo/temp/work
rm -fR /home/marcelo/temp/rootfs
mkdir -p /home/marcelo/temp/rootfs

export STAGE_WORK_DIR=/home/marcelo/temp/work
export ROOTFS_DIR=/home/marcelo/temp/rootfs

(cd ../hub_pi_gen/custom/04-custom; ./run.sh)
