#
# Conditional build:
# _without_ipv6	- IPv4-only version (doesn't require IPv6 in kernel)
#
Summary:	Boa high speed HTTP server
Summary(pl):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.94.12
Release:	1
Epoch:		1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.boa.org/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-logrotate.patch
URL:		http://www.boa.org/
BuildRequires:	autoconf
BuildRequires:	flex
BuildRequires:	sgml-tools
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(post,preun):	/sbin/chkconfig
Provides:	httpd
Provides:	webserver
Obsoletes:	apache
Obsoletes:	httpd
Obsoletes:	thttpd
Obsoletes:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/httpd

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
%patch1	-p1

%build
cd src
CFLAGS="%{rpmcflags} %{!?_without_ipv6:-DINET6}"
%{__autoconf}
%configure
%{__make}
cd ../docs
%{__make} boa.html

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d/ \
	$RPM_BUILD_ROOT/var/log/httpd \
	$RPM_BUILD_ROOT/home/httpd/{cgi-bin,html} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/conf,%{_mandir}/man8} \
	$RPM_BUILD_ROOT/etc/logrotate.d


install src/{boa,boa_indexer} $RPM_BUILD_ROOT%{_sbindir}/

install src/*.pl $RPM_BUILD_ROOT/home/httpd/cgi-bin/
install examples/* $RPM_BUILD_ROOT/home/httpd/cgi-bin/
install	%{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install boa.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install contrib/redhat/boa.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

install docs/boa.8 $RPM_BUILD_ROOT%{_mandir}/man8/

touch $RPM_BUILD_ROOT/var/log/httpd/{access_log,agent_log,error_log,referer_log}

gzip -9nf README ChangeLog

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid http`" ]; then
        if [ "`getgid http`" != "51" ]; then
                echo "Error: group http doesn't have gid=51. Correct this before installing boa." 1>&2
                exit 1
        fi
else
	echo "Creating group http GID=51"
        /usr/sbin/groupadd -g 51 -r -f http
fi
if [ -n "`id -u http 2>/dev/null`" ]; then
        if [ "`id -u http`" != "51" ]; then
                echo "Error: user http doesn't have uid=51. Correct this before installing boa." 1>&2
                exit 1
        fi
else
	echo "Creating user http UID=51"
        /usr/sbin/useradd -u 51 -r -d /home/httpd -s /bin/false -c "HTTP User" -g http http 1>&2
fi

%postun
if [ "$1" = "0" ]; then
	echo "Removing user http UID=51"
	/usr/sbin/userdel http > /dev/null 2>&1
	echo "Removing group http GID=51"
	/usr/sbin/groupdel http > /dev/null 2>&1
fi

%post
/sbin/chkconfig --add boa
if [ -f /var/lock/subsys/boa ]; then
        /etc/rc.d/init.d/boa restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/boa start\" to start boa http daemon."
fi

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/boa ]; then
                /etc/rc.d/init.d/boa stop 1>&2
        fi
        /sbin/chkconfig --del boa
fi

%files
%defattr(644,root,root,755)
%doc *.gz docs/*.html docs/*.png
%attr(750, root,http) %dir %{_sysconfdir}
%attr(640, root,http) %config(noreplace) %{_sysconfdir}/*
%attr(640, root,http) %config(noreplace) /etc/logrotate.d/%{name}
%attr(755, root,http) /home/httpd/html
%attr(755, root,http) /home/httpd/cgi-bin
%attr(750, root,http) %dir /var/log/httpd/
%attr(640, root,http) %ghost /var/log/httpd/*
%attr(755, root,root) %{_sbindir}/*
%attr(754, root,root) /etc/rc.d/init.d/%{name}
%{_mandir}/man8/*
