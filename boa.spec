Summary:	Boa high speed HTTP server
Summary(pl):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.93.16.1
Release:	1
Copyright:	GPL
Group:		Networking/Daemons
Group(pl):	Sieciowe/Serwery
Source0:	http://www.cz.boa.org/updates/%{name}-%{version}.tar.gz
Source1:	boa.init
Patch0:		boa-PLD.patch
Patch1:		boa-0.93.16.1-ipv6-fix.patch
Provides:       httpd                                                           
Provides:       webserver                                                       
Prereq:		sh-utils
Prereq:		%{_sbindir}/groupadd
Prereq:		%{_sbindir}/groupdel
Prereq:		%{_sbindir}/useradd
Prereq:		%{_sbindir}/userdel
Requires:	rc-scripts
BuildRoot:	/tmp/%{name}-%{version}-root

%define		_sysconfdir	/etc/httpd

%description
A high speed, lightweight web server (HTTP protocol).
Based on direct use of the select(2) system call, it internally multiplexes 
all connections without forking, for maximum speed and minimum system 
resource use.

%description -l pl
Niezwykle szybki i wysoko wydajny serwer WWW (protokó³ HTTP).
Bazuje na bezpo¶rednim u¿yciu funkcji systemowej select(2)
dziêki czemu mo¿e obs³ugiwaæ wiele po³±czeñ równocze¶nie bez
fork()owania co w efekcie znacznie zwiêksza szybko¶æ
dzia³ania oraz zmniejsza zu¿ycie zasobów systemowych.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
cd src
%configure
make
(cd ../util; make )
(cd ../docs; make boa.html )

%install
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d/,/var/log/httpd} \
	$RPM_BUILD_ROOT/home/httpd/{cgi-bin,html} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/conf,%{_mandir}/man1}

install -s		src/boa $RPM_BUILD_ROOT%{_sbindir}
install -s		util/boa_indexer $RPM_BUILD_ROOT%{_sbindir}

install -s		util/cpsel $RPM_BUILD_ROOT/home/httpd/cgi-bin
install			util/*.pl $RPM_BUILD_ROOT/home/httpd/cgi-bin
install	%{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install examples/*.conf $RPM_BUILD_ROOT/etc/httpd/%{name}.conf
install docs/boa.1	$RPM_BUILD_ROOT%{_mandir}/man1/

touch			$RPM_BUILD_ROOT/var/log/httpd/{access_log,agent_log,error_log,referer_log}
gzip -9nf		README $RPM_BUILD_ROOT%{_mandir}/man*/* || :

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -g 51 -f http > /dev/null 2>&1
%{_sbindir}/useradd -u 51 -f http -g http > /dev/null 2>&1

%postun
if [ "$1" = "0" ]; then
	%{_sbindir}/groupdel http > /dev/null 2>&1
	%{_sbindir}/userdel http > /dev/null 2>&1
fi

%post
/sbin/chkconfig -add %{name}

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/boa ]; then
                /etc/rc.d/init.d/boa stop 1>&2
        fi
        /sbin/chkconfig --del boa
fi

%files
%defattr(644,root,root,755)
%doc README.gz docs/*.html docs/*.gif
%attr(750, root,http) %dir /etc/httpd
%attr(640, root,http) %config /etc/httpd/*
%attr(755, root,http) /home/httpd/html
%attr(755, root,http) /home/httpd/cgi-bin
%attr(750, root,http) %dir /var/log/httpd/
%attr(640, root,http) %ghost /var/log/httpd/*
%attr(755, root,root) %{_sbindir}/*
%attr(754, root,root) /etc/rc.d/init.d/%{name}
%{_mandir}/man1/*
