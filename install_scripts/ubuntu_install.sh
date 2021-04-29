#!/bin/sh

#
# software packages required for PLC backup server system
# for deb-based distributions (Debian, Ubuntu)
#
# to install: 
#   sh debian_plcbackup_install.sh
#

# must run by root...
if test `id -u` -eq 0
then
	true
else
	echo "This script must be run by root."
	exit 1
	fi

#
# Workaround for
# dpkg: error: dpkg frontend is locked by another process xxxx
#
rm -f /var/lib/dpkg/lock-frontend


#
# Workaround for 
# E: Could not get lock /var/lib/apt/lists/lock – open (11: Resource temporarily unavailable)
# E: Unable to lock directory /var/lib/apt/lists/
# E: Could not get lock /var/lib/dpkg/lock – open (11: Resource temporarily unavailable)
# E: Unable to lock the administration directory (/var/lib/dpkg/), is another process using it?
#
# https://itsfoss.com/could-not-get-lock-error/
#
killall apt apt-get
rm /var/lib/apt/lists/lock
rm /var/cache/apt/archives/lock
rm /var/lib/dpkg/lock
dpkg --configure -a

# update everything
apt -y update
apt -y upgrade

# install software
# util-linux provides mountpoint
apt -yq install \
	smartmontools \
	network-manager \
	rsync \
	rsnapshot \
	smbclient \
	cifs-utils \
	python3 \
	cron \
	python3-pip \
	python3-psutil \
	ssh \
	openssh-client \
	git \
	util-linux \
	psmisc \
	`true "*** end of package list ***"`

# install modbus_tk
umask 022
pip3 install modbus_tk

# install webmin
# reference: http://www.webmin.com/deb.html

# add to repository
mkdir -p /etc/apt/sources.list.d/
cat > /etc/apt/sources.list.d/webmin.list << EOF
deb https://download.webmin.com/download/repository sarge contrib
EOF





# install gpg key
wget https://download.webmin.com/jcameron-key.asc
apt-key add jcameron-key.asc
rm -f jcameron-key.asc

# install webmin
apt -y install apt-transport-https
apt -y update
apt -y install webmin

# --- END OF INSTALLATION SCRIPT --- 
