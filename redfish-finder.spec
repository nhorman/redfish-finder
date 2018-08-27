%global shortcommit     %(c=%{githash}; echo ${c:0:7})

Name: redfish-finder 
Version: 0
Release: 0.1.%{gitdate}git%{shortcommit}
Summary: utility for parsing smbios information and configuring canonical bmc access
BuildArch: noarch

License: GPLV2
URL: https://github.com/nhorman/redfish-finder
Source0: %url/archive/%{githash}/%{name}-%{shortcommit}.tar.gz

BuildRequires: python
Requires: python NetworkManager dmidecode

%description
Scans Smbios information for type 42 management controller information, and uses
that to configure the appropriate network interface so that the bmc is
canonically accessible via the hostname redfish-localhost

%prep
%setup -q -n %{name}-%{githash}


%build
#noop here

%install
install -D -p -m 0755 redfish-finder %{buildroot}/%{_bindir}/redfish-finder
install -D -p -m 0644 redfish-finder.1 %{buildroot}/%{_mandir}/man1/redfish-finder.1
install -D -p -m 0644 ./redfish-finder.service %{buildroot}/%{_unitdir}/redfish-finder.service

%post
%systemd_post redfish-finder.service

%preun
%systemd_preun redfish-finder.service

%postun
%systemd_postun_with_restart redfish-finder.service


%files
%doc README.md COPYING
%{_bindir}/redfish-finder
%{_mandir}/man1/redfish-finder.1.gz
%{_unitdir}/redfish-finder.service

%changelog
* Tue Aug 28 2018 Neil Horman <nhorman@tuxdriver.com> - 0-0.1.20180828git
- Initial import

