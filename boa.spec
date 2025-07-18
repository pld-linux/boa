#
# Conditional build:
%bcond_without	ipv6	# IPv4-only version (doesn't require IPv6 in kernel)
#
%define	_rc		rc21
%define	_rel	3
Summary:	Boa high speed HTTP server
Summary(pl.UTF-8):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.94.14
Release:	0.%{_rc}.%{_rel}
Epoch:		1
License:	GPL v2
Group:		Networking/Daemons/HTTP
Source0:	http://www.boa.org/%{name}-%{version}%{_rc}.tar.gz
# Source0-md5:	e24b570bd767a124fcfb40a34d148ba9
Source1:	%{name}.init
Patch0:		%{name}-PLD.patch
URL:		http://www.boa.org/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	flex
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
BuildRequires:	texinfo
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(http)
Provides:	user(http)
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A high speed, lightweight web server (HTTP protocol). Based on direct
use of the select(2) system call, it internally multiplexes all
connections without forking, for maximum speed and minimum system
resource use.

%description -l pl.UTF-8
Niezwykle szybki i wysoko wydajny serwer WWW (protokół HTTP). Bazuje
na bezpośrednim użyciu funkcji systemowej select(2) dzięki czemu może
obsługiwać wiele połączeń równocześnie bez fork()owania co w efekcie
znacznie zwiększa szybkość działania oraz zmniejsza zużycie zasobów
systemowych.

%prep
%setup -q -n %{name}-%{version}%{_rc}
cp examples/boa.conf .
%patch -P0 -p0

%build
cp -f /usr/share/automake/config.sub .
%{__sed} -i 's,},  olddir /var/log/archive/boa\x0a},' contrib/rpm/boa.logrotate
CFLAGS="%{rpmcflags} %{?with_ipv6:-DINET6} -DSERVER_ROOT='\"%{_sysconfdir}\"'"
%{__autoconf}
%configure
%{__make}
%{__make} -C docs boa.html

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d \
	$RPM_BUILD_ROOT/var/log/{,archive/}boa \
	$RPM_BUILD_ROOT%{_sbindir} \
	$RPM_BUILD_ROOT%{_mandir}/man8 \
	$RPM_BUILD_ROOT/etc/logrotate.d \
	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

install src/{boa,boa_indexer} $RPM_BUILD_ROOT%{_sbindir}

install examples/*.pl examples/*.cgi \
	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install boa.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install contrib/rpm/boa.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

install docs/boa.8 $RPM_BUILD_ROOT%{_mandir}/man8

touch $RPM_BUILD_ROOT/var/log/boa/{access_log,agent_log,error_log,referer_log}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 51 -r -f http
%useradd -u 51 -r -d /usr/share/empty -s /bin/false -c "HTTP User" -g http http

%postun
if [ "$1" = "0" ]; then
	%userremove http
	%groupremove http
fi

%post
/sbin/chkconfig --add boa
%service boa restart "boa HTTP daemon"

%preun
if [ "$1" = "0" ]; then
	%service boa stop
	/sbin/chkconfig --del boa
fi

%triggerpostun -- boa < 0.94.14-0.rc20.0
if [ -f /etc/httpd/boa.conf.rpmsave ]; then
	echo "warning: installing /etc/boa.conf as /etc/boa.conf.rpmnew"
	mv /etc/boa.conf /etc/boa.conf.rpmnew
	echo "warning: moving /etc/httpd/boa.conf.rpmsave to /etc/boa.conf"
	mv /etc/httpd/boa.conf.rpmsave /etc/boa.conf
fi

%files
%defattr(644,root,root,755)
%doc CHANGES README docs/*.html docs/*.png
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/boa.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%attr(750,root,root) %dir /var/log/%{name}/
%attr(750,root,root) %dir /var/log/archive/%{name}/
%attr(640,root,root) %ghost /var/log/%{name}/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_mandir}/man8/*
%{_examplesdir}/%{name}-%{version}
