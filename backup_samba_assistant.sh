#!/bin/sh

this_script_file="$(readlink -f "$0")"
this_script_dirname="$(dirname "$this_script_file")"
this_script_basename="$(basename "$this_script_file")"

# tab
T="$(printf "\011x")"
T="${T%x}"

# newline
NL="$(printf "\012x")"
NL="${NL%x}"

# double qoute
DQ="$(printf "\042x")"
DQ="${DQ%x}"

# dollar sign
D="$(printf "\044x")"
D="${D%x}"

MAX_WIDTH=78
MAX_HEIGHT=18
MAX_LIST_HEIGHT=8

YCSPOMEEP_CONFIG_BEGIN="#YCSPOMEEP_CONFIG_BEGIN"
YCSPOMEEP_CONFIG_END="#YCSPOMEEP_CONFIG_END"

AUTO_MASTER="/etc/auto.master"
AUTO_YCSPOMEEP_SAMBA="/etc/auto.ycspomeep_samba"
AUTO_YCSPOMEEP_SAMBA_LOGIN="/etc/auto.ycspomeep_samba_login"

#  maps ycspomeep dir
RSNAPSHOT_CFG="$this_script_dirname/configs/rsnapshot.cfg"





intro()
{
	whiptail --msgbox "
This script helps you to create configuration files for auto-mounting and
backing up your samba shares (using rsnapshot).

Make sure that...
    * your file server has samba service enabled, and ...
    * this machine (backup server) has samba client and autofs installed.

Hit OK to continue...
" $MAX_HEIGHT $MAX_WIDTH

	return 0
}




SAMBA_HOST=""
select_samba_host()
{
	rc=0

	while test 1 -eq 1
	do

		SAMBA_HOST=$(whiptail --inputbox "Enter your hostname or IP address of your samba server." $MAX_HEIGHT $MAX_WIDTH "" 3>&1 1>&2 2>&3)
		rc=$?

		if test -n "$SAMBA_HOST" || test ! "$rc" -eq 0
		then
			break
		fi

	done

	return $rc
}




BACKUP_USER=""
select_backup_user()
{
	rc=0

	while test 1 -eq 1
	do

		BACKUP_USER=$(whiptail --inputbox "Enter the username used for backing up samba shares from $SAMBA_HOST." $MAX_HEIGHT $MAX_WIDTH "" 3>&1 1>&2 2>&3)
		rc=$?

		if test -n "$BACKUP_USER" || test ! "$rc" -eq 0
		then
			break
		fi

	done

	return $rc
}




BACKUP_USER_PASSWORD=""
select_backup_user_password()
{
	rc=0

	while test 1 -eq 1
	do

		BACKUP_USER_PASSWORD=$(whiptail --passwordbox "Enter the ${BACKUP_USER}'s password to access." $MAX_HEIGHT $MAX_WIDTH "" 3>&1 1>&2 2>&3)
		rc=$?

		if test -n "$BACKUP_USER_PASSWORD" || test ! "$rc" -eq 0
		then
			break
		fi

	done

	return $rc
}




DOMAIN=""
select_domain()
{
	DOMAIN=$(whiptail --inputbox "If your samba server has been joined into domain, enter that domain name; otherwise leave it blank." $MAX_HEIGHT $MAX_WIDTH "" 3>&1 1>&2 2>&3)
	rc=$?
	return $rc
}




SAMBA_SHARES=""
scan_samba_share()
{
	tmp_domain=""
	if test -n  "$DOMAIN"
	then
		tmp_domain="$DOMAIN\\"
	fi

	result=$(smbclient -g -L $SAMBA_HOST -U "$tmp_domain$BACKUP_USER%$BACKUP_USER_PASSWORD")
	rc=$?

	# if samba server listed...
	if test "$rc" -eq 0
	then
		# looking for result begin with 'Disk'
		# on each rows, get the 2nd entries
		SAMBA_SHARES=$(echo "$result" | grep -Ei "^disk" | cut -d "|" -f 2)


	# if not listed
	else

		whiptail --msgbox "
Cannot list samba share from $SAMBA_HOST.

Make sure all given informations are correct.
" $MAX_HEIGHT $MAX_WIDTH

		rc=1
	fi

	return $rc
}




# note: backup share will be store to $@!
BACKUP_SAMBA_SHARES=""
select_samba_shares()
{
	rc=0

	# we will use newline as separator!!!
	IFSOLD=$IFS
	IFS=$NL

	# tweak to convert samba share list into correspoinding
	# parameters
	set --

	for x in $SAMBA_SHARES
	do
		set -- "$@" "$x" "" "OFF"
	done

	# restore previous seperator
	IFS=$IFSOLD

	while test 1 -eq 1
	do

		BACKUP_SAMBA_SHARES=$(whiptail --separate-output --checklist \
			"Choose the following avaliable samba shares to backup." $MAX_HEIGHT $MAX_WIDTH $MAX_LIST_HEIGHT \
			"$@"  3>&1 1>&2 2>&3)

		rc=$?

		if test -n "$BACKUP_SAMBA_SHARES" || test ! "$rc" -eq 0
		then
			break
		fi
	done

	return $rc

}




SAMBA_PROTOCOL_VERSION=""
detect_smb_version()
{
	# try smbcliemt -m options
	# -m NT1: smbv1
	# -m SMB2: smbv2
	# -m SMB3: smbv3

	smbclient -L "$SAMBA_HOST" -m NT1 -U "${BACKUP_USER}%${BACKUP_USER_PASSWORD}" 2>&1 1>/dev/null
	use_smb1_rc=$?

	smbclient -L "$SAMBA_HOST" -m SMB2 -U "${BACKUP_USER}%${BACKUP_USER_PASSWORD}" 2>&1 1>/dev/null
	use_smb2_rc=$?

	smbclient -L "$SAMBA_HOST" -m SMB3 -U "${BACKUP_USER}%${BACKUP_USER_PASSWORD}" 2>&1 1>/dev/null
	use_smb3_rc=$?


	# SMB1
	if test "$use_smb1_rc" -eq 0
	then

		whiptail --yesno "
Warning: Insecured SMBv1 protocol detected!

Your file server ${SAMBA_HOST} requires the outdated SMBv1 protocol, which
has already been proven to be insecure, and may leave your system and/or
your entire network vulnerable. Contact your system administrator to fix
this issue as soon as possible.

Will you still need to make backup copies from ${SAMBA_HOST}?
" $MAX_HEIGHT $MAX_WIDTH

		rc=$?

		# if user choose YES...
		# force set 1.0
		if test "$rc" -eq 0
		then
			SAMBA_PROTOCOL_VERSION=1.0
		fi
	
	# OTHERS
	else

		if test "$use_smb2_rc" -eq 0
		then
			SAMBA_PROTOCOL_VERSION=2.0
		else
			SAMBA_PROTOCOL_VERSION=3.0
		fi

		rc=0
	fi

	return $rc
}




update_ycspommep_config()
{
	# $1: filename
	config_file="$1"

	# $2, $3, ...: content to be inserted
	
	# Try remove between YCSPOMEEP_CONFIG_BEGIN and YCSPOMEEP_CONFIG_END
	# # if any
	sed -i "/^$YCSPOMEEP_CONFIG_BEGIN/,/^$YCSPOMEEP_CONFIG_END/d" "$config_file" 2>/dev/null

	# insert content
	shift 1
	while test -n "$1"
	do
		#echo "$1"
		printf "%s\n%s\n%s\n" "$YCSPOMEEP_CONFIG_BEGIN" "$1" "$YCSPOMEEP_CONFIG_END" >> "$config_file"
		shift 1
	done

	rc=$?
	return $rc
}




configure_auto_master()
{
	update_ycspommep_config "$AUTO_MASTER" \
		"/mnt/autofs_ycspomeep_samba $AUTO_YCSPOMEEP_SAMBA --timeout=600 --ghost"

	rc=$?
	return $rc
}




configure_auto_ycspomeep_samba()
{
	# we will use newline as separator!!!
	IFSOLD=$IFS
	IFS=$NL

	# tweak to convert samba share list into correspoinding
	# parameters
	set --

	for x in $BACKUP_SAMBA_SHARES
	do
		set -- "$@" "$DQ$x$DQ -fstype=cifs,ro,noperm,credentials=$AUTO_YCSPOMEEP_SAMBA_LOGIN,vers=$SAMBA_PROTOCOL_VERSION $DQ://$SAMBA_HOST/$x$DQ"
	done

	# restore previous seperator
	IFS=$IFSOLD

	update_ycspommep_config "$AUTO_YCSPOMEEP_SAMBA" "$@"
	chmod 644 "$AUTO_YCSPOMEEP_SAMBA"

	rc=$?
	return $rc
}




configure_auto_ycspomeep_samba_login()
{
	if test 1 -eq 1
	then

		echo "username=$BACKUP_USER"
		echo "password=$BACKUP_USER_PASSWORD"
		
		if test -n "$DOMAIN"
		then
			echo "domain=$DOMAIN"
		fi

	fi > "$AUTO_YCSPOMEEP_SAMBA_LOGIN"
	chmod 600 "$AUTO_YCSPOMEEP_SAMBA_LOGIN"

	rc=$?
	return $?
}




restart_autofs()
{
	# try advance systemd first, then following classic init!
	systemctl restart autofs ||
		/etc/init.d/autofs restart

	rc=$?
	return $?
}





configure_rsnapshot()
{
	# get line no. which contains "rsnapshot_pre"
	start_lineno="$(grep -wn "rsnapshot_pre" "$RSNAPSHOT_CFG" | head -n1 | cut -d: -f1 )"
	if test -z "$start_lineno"
	then
		return 0
	fi

	# get line no. which contains "rsnapshot_post"
	end_lineno="$(grep -wn "rsnapshot_post" "$RSNAPSHOT_CFG" | tail -n1 | cut -d: -f1 )"
	if test -z "$start_lineno"
	then
		return 0
	fi


	# extract portions
	start_portions=$(sed -n "1,${start_lineno}p" "$RSNAPSHOT_CFG")	
	end_portions=$(sed -n "$end_lineno,${D}p" "$RSNAPSHOT_CFG")	

	# merge....
	if test 1 -eq 1
	then	

		echo "$start_portions"

		# we will use newline as separator!!!
		IFSOLD=$IFS
		IFS=$NL

		for x in $BACKUP_SAMBA_SHARES
		do
			echo "backup$T/mnt/autofs_ycspomeep_samba/$x/${T}autofs_ycspomeep_samba/$x/"
		done

		# restore previous seperator
		IFS=$IFSOLD

		echo "$end_portions"

	fi > "$RSNAPSHOT_CFG"
	rc=$?

	return $rc
}




finialise()
{
	whiptail --msgbox "
Your samba auto-mount and rsnapshot backup configuration is now ready.

For the rsnapshot backup part, the configuration is added to
configs/rsnapshot.cfg.

Please run rsnapshot_run.sh or rsnapshot_run.py to start your backup.
" $MAX_HEIGHT $MAX_WIDTH

}



#-----------------------------------------------------------------------------------------

#
# The main program
#

intro

select_samba_host && select_backup_user && select_backup_user_password && select_domain && detect_smb_version
rc=$?

if test $rc -eq 0
then
	scan_samba_share && select_samba_shares
	rc=$?
fi

if test $rc -eq 0
then
	configure_auto_master
	configure_auto_ycspomeep_samba
	configure_auto_ycspomeep_samba_login
	restart_autofs
	configure_rsnapshot
	finialise
fi

