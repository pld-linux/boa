Summary:	Boa high speed HTTP server
Summary(pl):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.93.16.1
Release:	1
Copyright:	GPL
Group:		Networking/Daemons
Source:		http://www.cz.boa.org/updates/%{name}-%{version}.tar.gz
Patch:		boa-PLD.patch
Provides:       httpd                                                           
Provides:       webserver                                                       
BuildRoot:	/tmp/%{name}-%{version}-root

%define		_sysconfdir	/etc/httpd

%description
A high speed, lightweight web server (HTTP protocol).
Based on direct use of the select(2) system call, it internally multiplexes 
all connections without forking, for maximum speed and minimum system 
resource use.

%description -l pl
Szybki serwer HTTP, byæ mo¿e alternatywa dla Apache HTTP Server.
Nie korzystaj±cy z funkcji fork().

%prep
%setup -q
%patch -p1

%build
cd src
%configure
make
(cd ../util; make )
(cd ../docs; make boa.html )

%install
install -d $RPM_BUILD_ROOT/home/httpd/{htdocs,cgi-bin,html}
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/conf,%{_mandir}/man1}
install -d $RPM_BUILD_ROOT/var/log/httpd

install -s src/boa $RPM_BUILD_ROOT%{_sbindir}
install -s util/boa_indexer $RPM_BUILD_ROOT%{_sbindir}

install -s util/cpsel $RPM_BUILD_ROOT/home/httpd/cgi-bin
install util/*.pl $RPM_BUILD_ROOT/home/httpd/cgi-bin

install examples/*.conf $RPM_BUILD_ROOT/etc/httpd/conf/
install docs/boa.1 $RPM_BUILD_ROOT%{_mandir}/man1/

gzip -9nf README $RPM_BUILD_ROOT%{_mandir}/man1/*

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.gz docs/*.html docs/*.gif
%attr(750, http,http) %dir /etc/httpd/conf
%attr(640, http,http) %config /etc/httpd/conf/*
%attr(755, http,http) /home/httpd/htdocs
%attr(755, http,http) /home/httpd/cgi-bin
%attr(755, http,http) /home/httpd/html
%attr(750, http,http) /var/log/httpd/
%attr(755, root,root) %{_sbindir}/*
%{_mandir}/man1/*
