Summary:	Boa high speed HTTP server
Summary(pl):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.94.8.2
Release:	2
License:	GPL
Group:		Networking/Daemons
Group(pl):	Sieciowe/Serwery
Group(de):	Netzwerkwesen/Server
Source0:	http://www.boa.org/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Patch0:		%{name}-PLD.patch
Provides:	httpd                                                           
Provides:	webserver                                                       
Prereq:		sh-utils
Prereq:		%{_sbindir}/groupadd
Prereq:		%{_sbindir}/groupdel
Prereq:		%{_sbindir}/useradd
Prereq:		%{_sbindir}/userdel
BuildRequires:	flex
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
%define		_sysconfdir	/etc/httpd
Obsoletes:	apache

%description
A high speed, lightweight web server (HTTP protocol). Based on direct
use of the select(2) system call, it internally multiplexes all
connections without forking, for maximum speed and minimum system
resource use.

%description -l pl
Niezwykle szybki i wysoko wydajny serwer WWW (protokó³ HTTP). Bazuje
na bezpo¶rednim u¿yciu funkcji systemowej select(2) dziêki czemu mo¿e
obs³ugiwaæ wiele po³±czeñ równocze¶nie bez fork()owania co w efekcie
znacznie zwiêksza szybko¶æ dzia³ania oraz zmniejsza zu¿ycie zasobów
systemowych.

%prep
%setup -q
%patch0 -p1

%build
cd src
CFLAGS="$RPM_OPT_FLAGS -DINET6"
%configure
%{__make}
(cd ../docs; make boa.html )

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d/,/var/log/httpd} \
	$RPM_BUILD_ROOT/home/httpd/{cgi-bin,html} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/conf,%{_mandir}/man8}

install src/{boa,boa_indexer} $RPM_BUILD_ROOT%{_sbindir}

install src/*.pl $RPM_BUILD_ROOT/home/httpd/cgi-bin
install examples/resolver.pl $RPM_BUILD_ROOT/home/httpd/cgi-bin
install	%{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install boa.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

install docs/boa.8 $RPM_BUILD_ROOT%{_mandir}/man8/

touch $RPM_BUILD_ROOT/var/log/httpd/{access_log,agent_log,error_log,referer_log}

gzip -9nf README $RPM_BUILD_ROOT%{_mandir}/man*/*

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -g 51 -f http > /dev/null 2>&1
%{_sbindir}/useradd -u 51 -f http -g http > /dev/null 2>&1

%postun
if [ "$1" = "0" ]; then
	%{_sbindir}/userdel http > /dev/null 2>&1
	%{_sbindir}/groupdel http > /dev/null 2>&1
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
%doc README.gz docs/*.html docs/*.png docs/boa.{ps,sgml}
%attr(750, root,http) %dir %{_sysconfdir}
%attr(640, root,http) %config %{_sysconfdir}/*
%attr(755, root,http) /home/httpd/html
%attr(755, root,http) /home/httpd/cgi-bin
%attr(750, root,http) %dir /var/log/httpd/
%attr(640, root,http) %ghost /var/log/httpd/*
%attr(755, root,root) %{_sbindir}/*
%attr(754, root,root) /etc/rc.d/init.d/%{name}
%{_mandir}/man8/*
