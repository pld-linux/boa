Summary:     Boa high speed HTTP server
Summary(pl): Boa - szyki serwer HTTP
Name:        boa
Version:     0.92
Release:     1
Copyright:   GPL
Group:       Networking/Daemons
Source:      %{name}-%{version}.tar.gz
Patch:       PLD-boa.diff
Buildroot:   /tmp/%{name}-%{version}-root

%description
A high speed, lightweight web server (HTTP protocol).
Based on direct use of the select(2) system call, it internally multiplexes 
all connections without forking, for maximum speed and minimum system 
resource use.

%description -l pl
Szybki serwer HTTP, by� mo�e alternatywa dla Apache HTTP Server.
Nie korzystaj�cy z funkcji fork().

%prep
%setup -q
%patch 

%build
cd src
make

%install
install -d $RPM_BUILD_ROOT/home/httpd/{conf,logs,util,html}

install -s src/boa $RPM_BUILD_ROOT/home/httpd/

install conf/* $RPM_BUILD_ROOT/etc/httpd/conf/
install docs/* $RPM_BUILD_ROOT/home/boa/docs/
install util/* $RPM_BUILD_ROOT/home/boa/util/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644, root, root, 755)
%doc README docs
%attr(750, http, www) %dir /etc/httpd/conf
%attr(750, http, www) %config /etc/httpd/conf/*
%attr(755, http, www) /home/httpd/util
%attr(755, http, www) /home/httpd/html
%attr(750, http, www) /var/log/httpd/

%changelog
* Fri Sep 25 1998 Wojciech "Sas" Ci�ciwa <alpha@zarz.agh.edu.pl>
- building RPM.
