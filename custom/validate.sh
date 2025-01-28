#!/bin/bash

log() {
  echo "$1"
}

export -f log
usr_dir=/home/$USER

rm -fR $usr_dir/temp/work
mkdir -p $usr_dir/temp/work
rm -fR $usr_dir/temp/rootfs
mkdir -p $usr_dir/temp/rootfs

export STAGE_WORK_DIR=$usr_dir/temp/work
export ROOTFS_DIR=$usr_dir/temp/rootfs

(cd ./custom/04-custom; ./02-run.sh)
