# Namespace
%global ns_name ea-apache24
%global module_name mod_fcgid

# Prevent debuginfo from being generated
%define debug_package %{nil}

%if 0%{?fedora} >= 18 || 0%{?rhel} > 6
%global _http_apxs %{_bindir}/apxs
%global _rundir /run
%else
%global _http_apxs %{_sbindir}/apxs
%global _rundir %{_localstatedir}/run
%endif

%global _tmpd %{_prefix}/lib/tmpfiles.d

Summary: FastCGI interface module for Apache HTTP Server
Name: %{ns_name}-%{module_name}
Version: 2.3.9
Vendor: cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, see EA-4560 for more details
%define release_prefix 9
Release: %{release_prefix}%{?dist}.cpanel
Group: System Environment/Daemons
URL: http://httpd.apache.org/mod_fcgid/
Source0: http://www.apache.org/dist/httpd/mod_fcgid/mod_fcgid-%{version}.tar.bz2
Source1: fcgid.conf
Source4: mod_fcgid-tmpfs.conf
Source5: 500-mod_fcgid.conf
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
mod_fcgid is a high performance alternative to mod_cgi or mod_cgid, which
starts a sufficient number instances of the CGI program to handle concurrent
requests, and these programs remain running to handle further incoming
requests.

%prep
%setup -q -n %{module_name}-%{version}
# Fix shellbang in fixconf script for our location of sed
%patch0 -p1 -b .shellbang
%patch1 -p1 -b .only_signal_running

%__cp -p %{SOURCE1} fcgid.conf

%build
APXS=%{_httpd_apxs} ./configure.apxs
%__make

%install
%__rm -rf %{buildroot}
%__make DESTDIR=%{buildroot} MKINSTALLDIRS="mkdir -p" install

%__mkdir_p %{buildroot}{%{_httpd_confdir},%{_httpd_modconfdir}}
%__install -p %{SOURCE5} %{buildroot}%{_httpd_modconfdir}/

# Include the manual as %%doc, don't need it elsewhere
%__rm -rf %{buildroot}%{_httpd_contentdir}/manual

# Make sure %%{_rundir}/mod_fcgid exists at boot time for systems
# with %%{_rundir} on tmpfs (#656625)
%__mkdir_p %{buildroot}%{_rundir}/mod_fcgid
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
%__mkdir_p %{buildroot}%{_tmpd}
%__install -p %{SOURCE4} %{buildroot}%{_tmpd}/mod_fcgid.conf
%else
%__sed -e 's#/run/mod_fcgid#'%{_rundir}'/mod_fcgid#' fcgid.conf > fcgid.conf.patched
%__mv fcgid.conf.patched fcgid.conf
%endif

%__install -D fcgid.conf %{buildroot}%{_httpd_confdir}/fcgid.conf

%preun
%__rm -f %{_rundir}/mod_fcgid/*

%clean
%__rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
# mod_fcgid.html.en is explicitly encoded as ISO-8859-1
%doc CHANGES-FCGID LICENSE-FCGID NOTICE-FCGID README-FCGID STATUS-FCGID
%doc docs/manual/mod/mod_fcgid.html.en modules/fcgid/ChangeLog
%doc build/fixconf.sed
%attr(0755,root,root) %{_httpd_moddir}/mod_fcgid.so
%config %{_httpd_modconfdir}/500-mod_fcgid.conf
%config(noreplace) %{_httpd_confdir}/fcgid.conf
%attr(0750,nobody,root) %{_rundir}/mod_fcgid
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
%{_tmpd}/mod_fcgid.conf
%endif

%changelog
* Wed Jan 02 2019 Cory McIntire <cory@cpanel.net> - 2.3.9-9
- EA-7976: Remove EXPERIMENTAL verbage from fcgid.conf file comments

* Wed Dec 07 2016 Dan Muey <dan@cpanel.com> - 2.3.9-8
- EA-5744: correct path, user, and group in tmp path config

* Fri Nov 04 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 2.3.9-7
- General cleanup (EA-5395)
- Cleans up run/mod_fcgid directory when package is uninstalled (EA-5594)
- Switch to rpm macros

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
