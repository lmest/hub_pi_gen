#!/bin/bash -e
# $1 destination

log "-----------------------------------------------------"
log "        Full Wireless removing packages"
log "-----------------------------------------------------"
on_chroot << EOF
apt remove -y --purge modemmanager libqt5core5a mkvtoolnix libdouble-conversion3 libdvdread8 \
                      libebml5 libflac12 libmatroska7 libogg0 libpcre2-16-0 libpugixml1v5 libqt5core5a \
                      libvorbis0a libcamera-ipa libcamera0.4 rpicam-apps-lite libboost-filesystem1.74.0 \
                      libboost-log1.74.0 libboost-program-options1.74.0 libboost-thread1.74.0 libexif12  \
                      liblttng-ust-common1 liblttng-ust-ctl5 liblttng-ust1 libpisp-common libpisp1 libunwind8 \
                      libyuv0 libavif15 libgd3 fontconfig-config fonts-dejavu-core libabsl20220623 libaom3 \
                      libdav1d6 libde265-0 libdeflate0 libfontconfig1 libfreetype6 libgav1-1 libheif1 libjbig0 \
                      liblerc4 libpng16-16 librav1e0 libsvtav1enc1 libtiff6 libwebp7 libx265-199 libxpm4 \
                      v4l-utils libjpeg62-turbo libv4l-0 libv4l2rds0 libv4lconvert0 gdb libbabeltrace1 \
                      libboost-regex1.74.0 libc6-dbg libdebuginfod-common libdebuginfod1 libsource-highlight-common \
                      libsource-highlight4v5 libatlas-base-dev libx11-6 libxext6 xauth libxmuu1 \
                      libx11-data libxau6 libxcb1 libxdmcp6 javascript-common libmtp-common libmtp-runtime libmtp9 \
                      p7zip p7zip-full
EOF
