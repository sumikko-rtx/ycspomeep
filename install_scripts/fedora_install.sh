#!/bin/sh

#
# software packages required for PLC backup server system
# for rpm-based distributions (RHEL >=8 / CentOS >=8 / Fedora >= 22)
#
# to install: 
#   sh fedora_plcbackup_install.sh
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
# replace "dnf" by "yum" if encountered an error message
# "dnf: command not found"
#


















# update everything
dnf -y update


# install software
dnf -y install \
	smartmontools \
	NetworkManager \
	rsync \
	rsnapshot \
	samba-client \
	cifs-utils \
	python3 \
	cronie \
	python3-pip \
	python3-psutil \
	openssh \
	openssh-clients \
	openssh-server \
	git \
	`true "end of package list***"`

# install modbus_tk
umask 022
pip3 install modbus_tk

# install webmin
# reference: http://www.webmin.com/rpm.html

# add to repository
mkdir -p /etc/yum.repos.d/
cat > /etc/yum.repos.d/webmin.repo << EOF
[Webmin]
name=Webmin Distribution Neutral
#baseurl=https://download.webmin.com/download/yum
mirrorlist=https://download.webmin.com/download/yum/mirrorlist
enabled=1
EOF

# install gpg key
wget https://download.webmin.com/jcameron-key.asc
rpm --import jcameron-key.asc
rm -f jcameron-key.asc

# install webmin
dnf -y install webmin



# --- END OF INSTALLATION SCRIPT ---
