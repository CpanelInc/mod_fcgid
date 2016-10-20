# Namespace
%global ns_name ea-apache24
%global module_name mod_fcgid

# Prevent debuginfo from being generated
%define debug_package %{nil}

%if 0%{?fedora} >= 18 || 0%{?rhel} > 6
%global _http_apxs %{_bindir}/apxs
%else
%global _http_apxs %{_sbindir}/apxs
%endif

Summary: FastCGI interface module for Apache HTTP Server
Name: %{ns_name}-%{module_name}
Version: 2.3.9
Vendor: cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, see EA-4560 for more details
%define release_prefix 6
Release: %{release_prefix}%{?dist}.cpanel
Group: System Environment/Daemons
URL: http://httpd.apache.org/mod_fcgid/
Source0: http://www.apache.org/dist/httpd/mod_fcgid/mod_fcgid-%{version}.tar.bz2
Source1: fcgid.conf
Source4: mod_fcgid-tmpfs.conf
License: ASL 2.0
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{ns_name}-devel >= 2.4.0
BuildRequires: pkgconfig
Requires: %{ns_name}-mmn = %{_httpd_mmn}
Requires: %{ns_name} >= 2.4.0
Requires: %{ns_name}-config
# sed required for fixconf script
Requires: /bin/sed
%if 0%{?fedora} >= 18 || 0%{?rhel} > 6
# systemd-units needed for ownership of /usr/lib/tmpfiles.d directory
Requires: systemd-units
%endif
Conflicts: %{ns_name}-mod_ruid2
Conflicts: %{ns_name}-mod_mpm_itk

Patch0: mod_fcgid-2.3.4-fixconf-shellbang.patch
Patch1: 0001-only_signal_running.patch

%description
mod_fcgid is a binary-compatible alternative to the Apache module mod_fastcgi.
mod_fcgid has a new process management strategy, which concentrates on reducing
the number of fastcgi servers, and kicking out corrupt fastcgi servers as soon
as possible.

%prep
%setup -q -n %{module_name}-%{version}
# Fix shellbang in fixconf script for our location of sed
%patch0 -p1 -b .shellbang
%patch1 -p1 -b .only_signal_running

cp -p %{SOURCE1} fcgid.conf

%build
APXS=%{_httpd_apxs} ./configure.apxs
make

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} MKINSTALLDIRS="mkdir -p" install

mkdir -p %{buildroot}{%{_httpd_confdir},%{_httpd_modconfdir}}
echo "LoadModule fcgid_module modules/mod_fcgid.so" > %{buildroot}%{_httpd_modconfdir}/500-fcgid.conf

# Include the manual as %%doc, don't need it elsewhere
rm -rf %{buildroot}%{_httpd_contentdir}/manual

# Make sure %%{rundir}/mod_fcgid exists at boot time for systems
# with %%{rundir} on tmpfs (#656625)
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
install -d -m 755 %{buildroot}%{_prefix}/lib/tmpfiles.d
install -p -m 644 %{SOURCE4} %{buildroot}%{_prefix}/lib/tmpfiles.d/mod_fcgid.conf
install -d -m 755 %{buildroot}/run/mod_fcgid/
%else
install -d -m 755 %{buildroot}%{_localstatedir}/run/mod_fcgid/
sed -e 's#/run/mod_fcgid#'%{_localstatedir}'/run/mod_fcgid#' fcgid.conf > fcgid.conf.patched
mv fcgid.conf.patched fcgid.conf
%endif

install -D -m 644 fcgid.conf %{buildroot}%{_httpd_confdir}/fcgid.conf
install -d -m 755 %{buildroot}%{rundir}/mod_fcgid

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
# mod_fcgid.html.en is explicitly encoded as ISO-8859-1
%doc CHANGES-FCGID LICENSE-FCGID NOTICE-FCGID README-FCGID STATUS-FCGID
%doc docs/manual/mod/mod_fcgid.html.en modules/fcgid/ChangeLog
%doc build/fixconf.sed
%{_httpd_moddir}/mod_fcgid.so
%config(noreplace) %{_httpd_modconfdir}/500-fcgid.conf
%config(noreplace) %{_httpd_confdir}/fcgid.conf
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
%{_prefix}/lib/tmpfiles.d/mod_fcgid.conf
%dir %attr(0700,nobody,root) /run/mod_fcgid/
%else
%dir %attr(0700,nobody,root) %{_localstatedir}/run/mod_fcgid/
%endif

%changelog
* Wed Oct 19 2016 Edwin Buck <e.buck@cpanel.com> - 2.3.9-6
- EA-5436: Fix mod_fcgid directory for CentOS 6.

* Tue Oct 18 2016 Edwin Buck <e.buck@cpanel.com> - 2.3.9-5
- EA-5436: Change ownership of /run/mod_fcgid to allow httpd writes

* Tue Oct 18 2016 Edwin Buck <e.buck@cpanel.com> - 2.3.9-4
- Added conflicts with ea-apache24-mod_mpm_itk.

* Mon Oct 17 2016 Dan Muey <dan@cpanel.com> - 2.3.9-3
- EA-5387: Use CloudLinux patch to limit process signaling to started processes

* Mon Oct 17 2016 Edwin Buck <e.buck@cpanel.com> - 2.3.9-2
- Added conflicts with ea-apache24-mod_ruid2.

* Fri Oct 14 2016 Edwin Buck <e.buck@cpanel.com> - 2.3.9-1
- First cPanel release
