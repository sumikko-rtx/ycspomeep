#!/bin/shcd 

#
# software packages required for ycspomeep backup server system
# for rpm-based distributions (RHEL >=8 / CentOS >=8 / Fedora >= 22)
#
# to install: 
#   sh fedora_plcbackup_install.sh
#

#
# must run by root...
# on cygwin, use net session instead
#
test `id -u` -eq 0 > /dev/null || net session > /dev/null 2>&1
if test "$?" -eq 0
then
	true
else
	echo "ERROR: This script must be run by root!!!"
	exit 1
fi




#
# replace "dnf" by "yum" if encountered an error message
# "dnf: command not found"
#

# update everything
dnf -y update




# install software
# util-linux provides mountpoint
# psmisc provides killall, pstree
# procps-ng provides ps, free, skill, pkill, pgrep, snice, tload, top, uptime, vmstat, pidof, pmap, slabtop, w, watch, pwdx and pidwait
dnf -y install \
	acpid \
	smartmontools \
	rsync \
	perl \
	rsnapshot \
	cronie \
	python3 \
	python3-pip \
	python3-chardet \
	python3-psutil \
	git \
	util-linux \
	psmisc \
	procps-ng \
	dnf-utils \
	`true "*** end of package list ***"`




# install modbus_tk
umask 022
pip3 install modbus_tk




## install webmin (deprecated, see the next section below)
## reference: http://www.webmin.com/rpm.html
#
## add to repository
#mkdir -p /etc/yum.repos.d/
#cat > /etc/yum.repos.d/webmin.repo << EOF
#[Webmin]
#name=Webmin Distribution Neutral
##baseurl=https://download.webmin.com/download/yum
#mirrorlist=https://download.webmin.com/download/yum/mirrorlist
#enabled=1
#EOF
#
## install gpg key
#wget https://download.webmin.com/jcameron-key.asc
#rpm --import jcameron-key.asc
#rm -f jcameron-key.asc
#
## install webmin
#dnf -y install webmin




# install webmin
# reference: https://webmin.com/download/
curl -o /tmp/setup-repos.sh https://raw.githubusercontent.com/webmin/webmin/master/setup-repos.sh
yes | sh /tmp/setup-repos.sh
dnf -y install webmin




# enable this server shutdown by simply pressing a power button
# https://unix.stackexchange.com/questions/242129/how-to-set-power-button-to-shutdown-instead-of-suspend
mkdir -p /etc/acpi/events/ && \
	printf "event=button/power\naction=/sbin/poweroff\n" > /etc/acpi/events/power && \
	systemctl restart acpid.service




# --- END OF INSTALLATION SCRIPT --- 
echo ""
echo "--- The ycspomeep backup program installation is now complete!!! ---"
echo ""
