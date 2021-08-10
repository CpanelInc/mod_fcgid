#!/bin/bash

source debian/vars.sh

set -x

echo "override_dh_auto_local"

make install DESTDIR=$DEB_INSTALL_ROOT

mkdir -p debian/tmp/etc/apache2/conf.d
mkdir -p debian/tmp/etc/apache2/conf.modules.d
mkdir -p debian/tmp/run/mod_fcgid
mkdir -p debian/tmp/usr/lib/tmpfiles.d
mkdir -p debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version

cp fcgid.conf debian/tmp/etc/apache2/conf.d
cp debian/SOURCES_FROM_SPEC/500-mod_fcgid.conf debian/tmp/etc/apache2/conf.modules.d
cp debian/SOURCES_FROM_SPEC/mod_fcgid-tmpfs.conf debian/tmp/usr/lib/tmpfiles.d/mod_fcgid.conf
cp CHANGES-FCGID debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp modules/fcgid/ChangeLog debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp LICENSE-FCGID debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp NOTICE-FCGID debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp README-FCGID debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp STATUS-FCGID debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp build/fixconf.sed debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version
cp debian/tmp/usr/share/apache2/manual/mod/mod_fcgid.html.en debian/tmp/usr/share/doc/ea-apache24-mod_fcgid-$version

