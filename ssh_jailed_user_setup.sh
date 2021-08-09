#!/bin/sh

#
# A sh script to setup ssh chrooted jail, which
# Restrict an SSH user session to a specific directory.
#
# To use it, run
#
# sh ssh_jailed_user_create.sh <jailroot> <user> 
#
# note:
#
# (1) you may be asked for the <user>'s password
#
# (2) if you added or deleted or made any changes to the user or password in /etc/passwd file,
#       please re-run this script again!!!
#

#
# Get this script path
#
this_script_file="$(readlink -f "$0")"
this_script_dirname="$(dirname "$this_script_file")"
this_script_basename="$(basename "$this_script_file")"




#
# Check if user is root
#
check_if_root()
{
	# on cygwin, use net session instead
	if uname -a | grep -i "cygwin"
	then
		net session > /dev/null 2>&1
		rc="$?"
	else
		test "$(id -u)" -eq 0 > /dev/null
		rc="$?"
	fi

	if test "$rc" -eq 0
	then
		true
	else
		echo "ERROR: This script must be run by root!!!"
		return 1
	fi
}




#
# aquire lockfile
#
lockfile="/tmp/$(basename "$this_script_file").pid"
acquire_lockfile()
{
	# aquire lockfile
	if test -f "$lockfile"
	then
		echo "ERROR: $0 is running!!!"
		return 1
	else
		touch "$lockfile"
	fi
}




#
# release lockfile
#
release_lockfile()
{
	rm -f "$lockfile"
}




#
# Show help messages
#
helpmsg()
{
cat << EOF

usage: $0 [options...]

where options are:

    -j --jailroot       Specify the directory to be chroot(ed).

    -u --user           Specify the ssh user to be jailed.

    -p --password       Specify the ssh user's password.
                        If empty string "" is leaved, a password entry is prompted for user input.
    
    -p --progs          Specify the programs which allow the jailed user to use.
                        (Separated by commas)

    -m --minimal-progs  Include the basic command utilites
                        (e.g. ls, cat, cp, etc.)

    -s --shell          Specify the ssh user's shell (/bin/sh).

    -h --help           Show this help message and then exit.

EOF
}




#
# parse input arguments $@
#
parse_args()
{
	# list of default values
	jailroot=""
	user=""
	shell=""
	progs=""
	delete_user="0"
	minimal_progs="0"
	password=""
	password_need_prompt="0"

	# read options goes here!!!
	parsed_options="$(getopt --options "j:u:s:p:q:mdh" --longoptions 'jailed-root:,user:,password:,shell:,progs:,minimal-progs,delete-user,help' -- "$@")"
	if test ! "$?" -eq 0
	then
		exit 1
	fi
	
	eval set -- "$parsed_options"
	unset parsed_options


	# extract options and their arguments into variables.
	while true
	do
		case "$1" in
		
			-j|--jailed-root)
				jailroot="$2"
				shift 2
				;;

			-u|--user)
				user="$2"
				shift 2
				;;

			-p|--password)
				password="$2"
				
				if test -z "$password"
				then
					password_need_prompt="1"
				fi
				
				shift 2
				;;

			-s|--shell)
				shell="$2"
				shift 2
				;;

			-q|--progs)
				progs="$2"
				shift 2
				;;

			-m|--minimal-progs)
				minimal_progs="1"
				shift 1
				;;

			-d|--delete-user)
				delete_user="1"
				shift 1
				;;
				
			-h|--help)
				helpmsg
				exit 0
				shift 1
				;;
				
				
				
			--) # end of script
				shift 1
				break
				;;

			*)
				echo "ERROR: $1: unrecognized options"
				return 1
				;;
		esac
	done
	

	# jailroot is required!!!
	if test -z "${jailroot}"
	then
		echo "ERROR: no jailroot!!!"
		exit 1
	fi


	# We can't accept any empty user!!!
	if test -z "${user}"
	then
		echo "ERROR: no user!!!"
		exit 1
	fi


	# default shell is /bin/sh
	if test -z "${shell}"
	then
		shell="/bin/sh"
	fi


	# progs also include shell
	progs="$shell,$progs"


	# if minimal_progs is used, include these...
	if test ! "$minimal_progs" -eq 0
	then
		progs="$progs,zcat,xargs,wc,vi,vim,unlink,uniq,unexpand,tsort,true,tr,touch"
		progs="$progs,time,test,tee,tail,sort,sleep,sh,sed,rmdir,rm,read,pws,ps"
		progs="$progs,printf,mv,more,mkdir,man,ls,id,iconv,head,grep,getopts,getopt,"
		progs="$progs,find,fg,false,expr,echo,du,dirname,diff,df,date,cut,chmod,cp,cd,cat,bg,bc,basename"
		progs="$progs,awk"
	fi
}




#
# Start by making the chroot directory
#
setup_jailroot()
{
	mkdir -p "$jailroot/"

	# copy some essential /dev nodes over to the chroot directory, which
	# allows users basic use of the terminal.	
	mkdir -p "$jailroot/dev/"

	# mknod returns non-zero exit status if the filenames above is exists!!!
	mknod -m 666 "$jailroot/dev/null" c 1 3
	mknod -m 666 "$jailroot/dev/tty" c 5 0
	mknod -m 666 "$jailroot/dev/zero" c 1 5
	mknod -m 666 "$jailroot/dev/random" c 1 8

	# set permissions on the chroot directory. The root user will need to own the
	# directory in order to make sure that the jailed users can't leave it.
	# Other users can only have read and execute permissions. 
	chown root:root "$jailroot"
	chmod 0755 "$jailroot"
}




#
# Copy all given files $@ to $jailroot
#
cp_2_jailroot()
{
	for x in "$@"
	do
		x_dir="$(dirname "$x")"
		mkdir -p "$jailroot/$x_dir"
		cp -f "$x" "$jailroot/$x_dir" 2>/dev/null
	done
}




#
# Setup the jailed programs
#
setup_jailed_progs()
{
	OLD_IFS1="$IFS"
	IFS=","
	
	for x in $progs
	do

		# copy the purly binaries and versioning symlinks!!!
		x="$(command -v "$x")"
		x_real="$(readlink -f "$x")" 
		x_dir="$(dirname "$x")"

		#echo "x=[$x]"
		#echo "x_real=$x_real"
		#echo "x_dir=$x_dir"

		cp_2_jailroot "$x" "$x_real"

		# we also copy the required libraries that
		# program $x requires
		x_libs="$(ldd "$x" 2>/dev/null | sed --regexp-extended  's/\(0x[A-Za-z0-9]+\)//g;s/.*=>//g')"


		OLD_IFS2="$IFS"
		IFS="$OLD_IFS1"
		
		for y in $x_libs
		do
		
			# once again, copy the purly binaries and versioning symlinks!!!
			y_real="$(readlink -f "$y")"
			y_dir="$(dirname "$y")"

			#echo "y=$y"
			#echo "y_real=$y_real"
			#echo "y_dir=$y_dir"
			
			# note: The linux-vdso.so.1 is virtual so you can ignore this dependency.
			cp_2_jailroot "$y" "$y_real"
			
		done
		IFS="$OLD_IFS2"

	done
	IFS="$OLD_IFS1"
	
	
	# In case you want to translate the user and group ids into readable
	# strings you will need to setup the NSS by copying the following
	# files into the chroot environment:
	possible_libdirs="/lib /lib64 /lib32 /usr/lib /usr/lib64 /usr/lib32 /usr/local/lib /usr/local/lib64 /usr/local/lib32 $LD_LIBRARY_PATH"
	
	for x in $possible_libdirs
	do
		# https://community.hetzner.com/tutorials/setup-chroot-jail
		x_libs=""
		x_libs="$x_libs $(find "$x" -name "libnss_files*" 2>/dev/null)"
		x_libs="$x_libs $(find "$x" -name "libnss_systemd*" 2>/dev/null)"
		x_libs="$x_libs $(find "$x" -name "libcrypt*" 2>/dev/null)"
			
		for y in $x_libs
		do
			cp_2_jailroot "$y"
		done	
	done
	
	cp_2_jailroot "/etc/nsswitch.conf"
	
	true
}





#
# Now we can create the user and set a password for the account. 
#
setup_jailed_user()
{
	# useradd ignores if $user exists!!!
	useradd "$user" 2>&1 >/dev/null


	# here you may be asked to enter $user's password!!!
	if test ! "$password_need_prompt" -eq 0
	then
	
		# password_need_prompt=0, show password entry for user input
		echo "Please enter $user's password..."
		passwd "$user"
		
	else
	
		# otherwise direct to specify password
		# https://stackoverflow.com/questions/714915/using-the-passwd-command-from-within-a-shell-script
passwd "$user" << EOF
		${password}
		${password}
EOF
	fi


	# Select for $user's shell
	usermod --shell "$shell" "$user"
	
	
	# Add the /etc/passwd and /etc/group files into the chroot directory. 
	mkdir -p "$jailroot/etc/"
	cp /etc/passwd "$jailroot/etc/"
	cp /etc/group "$jailroot/etc/"


	# setup home directory for the jailed users
	jailed_home_dir="$jailroot/home/$user"
	mkdir -p "$jailed_home_dir"
	chown "$user:$user" "$jailed_home_dir"
	chmod 744 "$jailed_home_dir"


	# create a ssh config file containins the jail user configuration
	#
	# AuthorizedKeysFile is the key!!!
	# ssh looks for this files every session start
	#
	cat > "/etc/ssh/sshd_config.d/ssh_jailed_user_${user}.conf" <<EOF
Match User $user
ChrootDirectory $jailroot
AuthorizedKeysFile $jailroot/home/$user/.ssh/authorized_keys
EOF


	# After editing, Save it and restart sshd!!!
	systemctl restart sshd
}




#
# Create a home directory for the user and give it proper permissions. 
#
finish_jailed_user_setup()
{
host="$(hostname -I)"
cat<<EOF

You have created a jailed ssh user, $user.
Try "ssh $user@$host" on the another machine to test if a ssh chroot jail is working!!! 

If it is not working, it is possibly indicated that the jail user profile is not loaded completely.

Add the following content on top of /etc/ssh/sshd_config:

	Match All
	Include /etc/ssh/sshd_config.d/*.conf

Save it and run command "systemctl restart sshd" to restart ssh server.

EOF
}




#
# clean up procedures
#
clean_up()
{
	true
}




#
# exit this program
#
exit_program()
{
	clean_up
	release_lockfile
	
	rc="$1"
	if test -z "$rc"
	then
		rc=0
	fi
	exit "$rc"
}

#-----------------------------------------------------------------------------------------

#
# The main program
#

trap exit_program INT TERM
check_if_root && acquire_lockfile && parse_args "$@"

if test "$?" -eq 0
then
	if test "$delete_user" -eq 1
	then
	
		# --- begin of deleting user code --
		true &&
			delete_jailed_user
		# --- end of deleting user code --
		
	else

		# --- begin of creating user code --
		true &&
			setup_jailroot &&
			setup_jailed_progs &&
			setup_jailed_user &&
			finish_jailed_user_setup
		# --- end of creating user code --

	fi
fi

exit_program 0
