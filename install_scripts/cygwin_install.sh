#!/bin/sh

#
# software packages required for ycspomeep backup server system
# for cygwin
#
# to install: 
#   sh cygwin_install.sh
#

# must run by root...

#
# Note: do not use $(id -u) in cygwin. use $(net session) instead
#       see ttps://superuser.com/questions/660191/how-to-check-if-cygwin-mintty-bash-is-run-as-administrator
#
net session > /dev/null 2>&1
if test "$?" -eq 0
then
	true
else
	echo "This script must be run by root."
	exit 1
fi




#
# notes:
# ( there is no cygwin version of apt, yum, pacman... etc. !!! )
#
# cygwin ships with a gui package installer, setup-x86.exe or setup-x86_64.exe
# put the latestest verison of setup-x86.exe or setup-x86_64.exe into your cygwin directory.
#
# (by default: %SystemDrive%/cygwin or %SystemDrive%/cygwin64)
#
SETUP_EXE=""
if test -f /setup-x86_64.exe
then
	SETUP_EXE="/setup-x86_64.exe"

elif test -f /setup-x86.exe
then
	SETUP_EXE="/setup-x86.exe"

else
	echo ""
	echo "cannot found your cygwin installer: setup-x86.exe or setup-x86_64.exe"
	echo ""
	echo "Download a cygwin installer using the link:"
	echo ""
	echo "  https://cygwin.com/setup-x86.exe or "
	echo "  https://cygwin.com/setup-x86_64.exe"
	echo ""
	echo "And put the dowbloaded into your cygwin directory."
	echo "(by default: %SystemDrive%/cygwin or %SystemDrive%/cygwin64)"
	echo ""
	exit 1
fi




# update everything
# https://superuser.com/questions/214831/how-to-update-cygwin-from-cygwins-command-line
"$SETUP_EXE" --no-desktop --no-shortcuts --no-startmenu --quiet-mode


# --- END OF INSTALLATION SCRIPT --- 
echo ""
echo "--- The ycspomeep backup system program installation is now complete!!! ---"
echo ""



# install software for PLC program
REQUIRED_PKG="$(echo \
	man-db \
	smartmontools \
	$(true "network-manager: not included in msys2 version. use 'netsh' command to configure your network.") \
	rsync \
	perl \
	rsnapshot \
	$(true "samba-client: not included in msys2 version. use 'net use' command to connect your samba share.") \
	$(true "cifs-utils: not included in msys2 version. use 'net use' command to connect your samba share.") \
	$(true "cron: see section 'manually install cron' for details ") \
	python3 \
	$(true "python3-pip: already included in python3. use 'pip3'.") \
	$(true "python3-chardet: see manually install chardet for details.") \
	openssh \
	$(true "openssh-clients: already included in openssh.") \
	git \
	util-linux \
	psmisc \
	procps-ng \
	`true "end of package list***"`
)"

"$SETUP_EXE" --no-desktop --no-shortcuts --no-startmenu --quiet-mode -P "$(echo "$REQUIRED_PKG" | tr "[:space:]" ",")"




# update pip if any
python3 -m pip install --upgrade pip
umask 022




# manually install modbus_tk
pip3 install modbus_tk




# manually install python3-chardet
pip3 install chardet




# install webmin
# reference: http://www.webmin.com/deb.html

# add to repository
#mkdir -p /etc/apt/sources.list.d/
#cat > /etc/apt/sources.list.d/webmin.list << EOF
#deb https://download.webmin.com/download/repository sarge contrib
#EOF




# install gpg key
#wget https://download.webmin.com/jcameron-key.asc
#apt-key add jcameron-key.asc
#rm -f jcameron-key.asc

# install webmin
#apt -y install apt-transport-https
#apt -y update
#apt -y install webmin

# --- END OF INSTALLATION SCRIPT --- 
echo ""
echo "--- The ycspomeep backup system program installation is now complete!!! ---"
echo ""
