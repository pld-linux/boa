#
# Conditional build:
%bcond_without 	ipv6	# IPv4-only version (doesn't require IPv6 in kernel)
#
Summary:	Boa high speed HTTP server
Summary(pl):	Boa - szybki serwer HTTP
Name:		boa
Version:	0.94.14
%define	_rc	rc20
Release:	0.%{_rc}.3
Epoch:		1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.boa.org/%{name}-%{version}%{_rc}.tar.gz
# Source0-md5:	046d1764cd8f325109da9c80c993b2ef
Source1:	%{name}.init
Patch0:		%{name}-PLD.patch
URL:		http://www.boa.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	flex
BuildRequires:	rpmbuild(macros) >= 1.159
BuildRequires:	texinfo
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(post,preun):	/sbin/chkconfig
Provides:	group(http)
Provides:	user(http)
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# FIXME: Other location?  Should belong to httpd-common (or alike) package?
# NOTE:  Not needed, as we shouldn't put anything there.
#%define		_cgi_bin	/usr/lib/cgi-bin

%description
A high speed, lightweight web server (HTTP protocol). Based on direct
use of the select(2) system call, it internally multiplexes all
connections without forking, for maximum speed and minimum system
resource use.

%description -l pl
Niezwykle szybki i wysoko wydajny serwer WWW (protok� HTTP). Bazuje
na bezpo�rednim u�yciu funkcji systemowej select(2) dzi�ki czemu mo�e
obs�ugiwa� wiele po��cze� r�wnocze�nie bez fork()owania co w efekcie
znacznie zwi�ksza szybko�� dzia�ania oraz zmniejsza zu�ycie zasob�w
systemowych.

%prep
%setup -q -n %{name}-%{version}%{_rc}
cp examples/boa.conf .
%patch0 -p0

%build
cp -f /usr/share/automake/config.sub .
CFLAGS="%{rpmcflags} %{?with_ipv6:-DINET6} -DSERVER_ROOT='\"%{_sysconfdir}\"'"
%{__autoconf}
%configure
%{__make}
%{__make} -C docs boa.html

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d/ \
	$RPM_BUILD_ROOT/var/log/{,archiv/}boa \
	$RPM_BUILD_ROOT%{_sbindir} \
	$RPM_BUILD_ROOT%{_mandir}/man8 \
	$RPM_BUILD_ROOT/etc/logrotate.d \
	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
#	$RPM_BUILD_ROOT%{_cgi_bin}

install src/{boa,boa_indexer} $RPM_BUILD_ROOT%{_sbindir}/

install src/*.pl examples/*.pl examples/*.cgi \
	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
install	%{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install boa.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install contrib/rpm/boa.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

install docs/boa.8 $RPM_BUILD_ROOT%{_mandir}/man8/

touch $RPM_BUILD_ROOT/var/log/boa/{access_log,agent_log,error_log,referer_log}

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
	/usr/sbin/useradd -u 51 -r -d /usr/share/empty -s /bin/false -c "HTTP User" -g http http 1>&2
fi

%postun
if [ "$1" = "0" ]; then
	%userremove http
	%groupremove http
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
%doc README CHANGES docs/*.html docs/*.png
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/boa.conf
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/%{name}
#%attr(755,root,root) %{_cgi_bin}
%attr(750,root,root) %dir /var/log/%{name}/
%attr(750,root,root) %dir /var/log/archiv/%{name}/
%attr(640,root,root) %ghost /var/log/%{name}/*
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_mandir}/man8/*
%{_examplesdir}/%{name}-%{version}
