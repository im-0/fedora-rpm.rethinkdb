Name:       rethinkdb
Version:    2.4.4
Release:    2%{?dist}
Summary:    The open-source database for the realtime web

License:    Apache-2.0
URL:        https://github.com/rethinkdb/rethinkdb
Source0:    https://github.com/rethinkdb/rethinkdb/archive/v%{version}/%{name}-%{version}.tar.gz

# Contains `rethinkdb-$VERSION/external/*` after running `make fetch`.
Source1:    %{name}-%{version}.external.tar.xz

Source2:    %{name}@.service

Patch0: 0001-security-fix-buffer-overflow-vulnerability-in-cJSON-.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python-unversioned-command
BuildRequires:  systemd-rpm-macros
BuildRequires:  protobuf-compiler
BuildRequires:  protobuf-devel
BuildRequires:  libcurl-devel
BuildRequires:  boost-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  ncurses-devel


%description
RethinkDB is the first open-source scalable database built for realtime
applications. It exposes a new database access model, in which the developer
can tell the database to continuously push updated query results to applications
without polling for changes. RethinkDB allows developers to build scalable
realtime apps in a fraction of the time with less effort.


%prep
%setup -q -D -T -b0 -n %{name}-%{version}
%setup -q -D -T -b1 -n %{name}-%{version}

%patch -P 0 -p 1


%build
# Unset custom Fedora's CXXFLAGS and LDFLAGS, otherwise ld fails on libquickjs.
unset CXXFLAGS
unset LDFLAGS
./configure --with-system-malloc
make %{?_smp_mflags}


%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/%{_sharedstatedir}/%{name}

mv build/release_system/rethinkdb %{buildroot}/%{_bindir}/
cp \
        packaging/assets/config/default.conf.sample \
        %{buildroot}/%{_sysconfdir}/%{name}/
mv %{SOURCE2} %{buildroot}/%{_unitdir}/


%files
%{_bindir}/rethinkdb
%attr(0750,root,%{name}) %dir %{_sysconfdir}/%{name}
%attr(0640,root,%{name}) %config %{_sysconfdir}/%{name}/default.conf.sample
%attr(0750,%{name},%{name}) %dir %{_sharedstatedir}/%{name}
%{_unitdir}/%{name}@.service


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{_sharedstatedir}/%{name} -M \
        -c 'RethinkDB' -g %{name} %{name}
exit 0


%post
%systemd_post %{name}@.service


%preun
%systemd_preun '%{name}@*.service'


%postun
%systemd_postun_with_restart '%{name}@*.service'


%changelog
* Mon Aug 25 2025 Ivan Mironov <mironov.ivan@gmail.com> - 2.4.4-2
- Add security fix

* Fri Mar 22 2024 Ivan Mironov <mironov.ivan@gmail.com> - 2.4.4-1
- Update to 2.4.4

* Wed Sep 27 2023 Ivan Mironov <mironov.ivan@gmail.com> - 2.4.3-2
- Run as daemon, otherwise it does not create normal access control tables

* Tue Sep 26 2023 Ivan Mironov <mironov.ivan@gmail.com> - 2.4.3-1
- Initial packaging
