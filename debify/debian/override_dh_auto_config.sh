#!/bin/bash

source debian/vars.sh

cp -p $SOURCE1 fcgid.conf

set -x

# pulled from apr-util
mkdir -p config
cp $ea_apr_config config/apr-1-config
cp $ea_apr_config config/apr-config
cp /usr/share/pkgconfig/ea-apr16-1.pc config/apr-1.pc
cp /usr/share/pkgconfig/ea-apr16-util-1.pc config/apr-util-1.pc
cp /usr/share/pkgconfig/ea-apr16-1.pc config
cp /usr/share/pkgconfig/ea-apr16-util-1.pc config

export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:`pwd`/config"
touch configure
touch configure.apxs

export APR_CONFIG=/opt/cpanel/ea-apr16/bin/apr-1-config
export libtool=/opt/cpanel/ea-apr16/lib64/apr-1/build/libtool
export LIBTOOL=/opt/cpanel/ea-apr16/lib64/apr-1/build/libtool

# Fix shellbang in fixconf script for our location of sed
export APXS=$_httpd_apxs

/bin/bash ./configure.apxs

# This has to be forced, none of the normal configuration stuff makes it happen
sed -i '21iLIBTOOL=/opt/cpanel/ea-apr16/lib64/apr-1/build/libtool --silent' modules/fcgid/Makefile

make

