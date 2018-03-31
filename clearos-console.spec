Name: clearos-console
Version: 7.4.1
Release: 1%{dist}
Summary: Administration console module
License: GPLv3 or later
Group: System Environment/Base
Source: %{name}-%{version}.tar.gz
Vendor: ClearFoundation
Requires: clearos-base
Requires: iptraf
Requires: kbd
Requires: tconsole >= 3.3-8
Requires: ethtool
Requires: systemd
BuildArch: noarch

%description
Administration console module

%prep
%setup -q
%build

%install
mkdir -p -m 755 $RPM_BUILD_ROOT/etc/systemd/system/getty@tty1.service.d
install -m 644 autologin.conf $RPM_BUILD_ROOT/etc/systemd/system/getty@tty1.service.d/

mkdir -p -m 755 $RPM_BUILD_ROOT/var/lib/clearconsole
install -m 644 bash_profile $RPM_BUILD_ROOT/var/lib/clearconsole/.bash_profile

%pre
getent group clearconsole >/dev/null || groupadd -r clearconsole
getent passwd clearconsole >/dev/null || \
    useradd -r -g clearconsole -d /var/lib/clearconsole/ -s /bin/bash \
    -c "Console" clearconsole
exit 0

%post

# Add sudoers stuff
#------------------

CHECK=`grep "^Cmnd_Alias CLEARCONSOLE =" /etc/sudoers`
if [ -z "$CHECK" ]; then
    echo "Cmnd_Alias CLEARCONSOLE = /usr/bin/iptraf, /usr/sbin/console_start, /usr/sbin/tc-yum, /bin/rpm, /sbin/halt, /sbin/reboot, /usr/sbin/app-passwd, /usr/sbin/gconsole-setup" >> /etc/sudoers
fi

CHECK=`grep "^clearconsole[[:space:]]*" /etc/sudoers`
if [ -z "$CHECK" ]; then
    echo "clearconsole ALL=NOPASSWD: CLEARCONSOLE" >> /etc/sudoers
fi

# Add new commands, e.g. /usr/sbin/gconsole-setup
CHECK=`grep "^Cmnd_Alias CLEARCONSOLE =.*/usr/sbin/gconsole-setup" /etc/sudoers`
if [ -z "$CHECK" ]; then
    sed -i -e 's/^Cmnd_Alias CLEARCONSOLE =/Cmnd_Alias CLEARCONSOLE = \/usr\/sbin\/gconsole-setup,/' /etc/sudoers
fi
CHECK=`grep "^Cmnd_Alias CLEARCONSOLE =.*/sbin/ethtool" /etc/sudoers`
if [ -z "$CHECK" ]; then
    sed -i -e 's/^Cmnd_Alias CLEARCONSOLE =/Cmnd_Alias CLEARCONSOLE = \/sbin\/ethtool,/' /etc/sudoers
fi
CHECK=`grep "^Cmnd_Alias CLEARCONSOLE =.*/usr/bin/systemctl" /etc/sudoers`
if [ -z "$CHECK" ]; then
    sed -i -e 's/^Cmnd_Alias CLEARCONSOLE =/Cmnd_Alias CLEARCONSOLE = \/usr\/bin\/systemctl,/' /etc/sudoers
fi

/usr/sbin/addsudo /sbin/halt clearos-console
/usr/sbin/addsudo /sbin/reboot clearos-console

# Avoid excessive loggin
CHECK=`grep "^Defaults:clearconsole" /etc/sudoers`
if [ -z "$CHECK" ]; then
    echo "Defaults:clearconsole !syslog" >> /etc/sudoers
fi

# Install new console
#--------------------

CHECK=`grep "ACTIVE_CONSOLES=\/dev\/tty\[1-6\]" /etc/sysconfig/init 2>/dev/null`
if [ -n "$CHECK" ]; then
    sed -i -e 's/ACTIVE_CONSOLES=\/dev\/tty\[1-6\]/ACTIVE_CONSOLES=\/dev\/tty\[2-6\]/' /etc/sysconfig/init
fi

# TODO tconsole should use new path.  Symlink for now.
#-----------------------------------------------------

if [ ! -e /usr/sbin/iptraf ]; then
    ln -sf /usr/sbin/iptraf-ng /usr/bin/iptraf
fi

exit 0

%preun
if [ $1 -eq 0 ]; then
    CHECK=`grep "ACTIVE_CONSOLES=\/dev\/tty\[2-6\]" /etc/sysconfig/init 2>/dev/null`
    if [ -n "$CHECK" ]; then
        sed -i -e 's/ACTIVE_CONSOLES=\/dev\/tty\[2-6\]/ACTIVE_CONSOLES=\/dev\/tty\[1-6\]/' /etc/sysconfig/init
        sleep 1
        initctl reload-configuration >/dev/null 2>&1
        killall X >/dev/null 2>&1
    fi    
fi

exit 0

%files
%defattr(-,root,root)
/etc/systemd/system/getty@tty1.service.d
/var/lib/clearconsole/.bash_profile
%dir %attr(-,clearconsole,root) /var/lib/clearconsole
