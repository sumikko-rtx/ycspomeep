#!/bin/sh

#
# A sh script to remove ycspomeep backup program.
#
# To use it, run
#
# sh uninstall.sh 
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
#	# on cygwin, use net session instead
#	if uname -a | grep -i "cygwin"
#	then
#		net session > /dev/null 2>&1
#		rc="$?"
#	else
#		test "$(id -u)" -eq 0 > /dev/null
#		rc="$?"
#	fi
#
#	if test "$rc" -eq 0
#	then
#		true
#	else
#		echo "ERROR: This script must be run by root!!!"
#		return 1
#	fi
	true
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

usage: $0

where options are:

    -N --level-name  backup level name (alpha)

    -n --interval    interval of the type --backup-level-name (0, 1, 2, ...)

    -p --print-path  Print the backup file path and then exit.

    -h --help        Show this help message and then exit.

EOF
}




#
# parse input arguments $@
#
parse_args()
{
	# list of default values
	level_name="alpha"
	interval="0"
	print_path="0"

	# get rsnapshot_root
	PY3="/usr/bin/python3"
	RSNAPSHOT_SNAPSHOT_ROOT="$("$PY3" "$this_script_dirname/rsnapconfig_getparam_snapshot_root.py")"


	# read options goes here!!!
	parsed_options="$(getopt --options "N:n:ph" --longoptions 'level-name:,interval:,--print-path,help' -- "$@")"
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
		
			-N|--level-name)
				level_name="$2"
				shift 2
				;;
				
			-n|--interval)
				interval="$2"
				shift 2
				;;
				
			-p|--print_path)
				print_path="1"
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
}




#
# show backuped files by given $level_name and $interval
#
show_backuped_files_at()
{
	# we are going to open that directory...
	target_dir="$RSNAPSHOT_SNAPSHOT_ROOT/$level_name.$interval/"

	# if print_path=1, print $target_dir and then exit
	if test "$print_path" -eq 0
	then
		true
	else
		echo "$target_dir"
		return 0
	fi


	# get the program path of xdg-open
	XDG_OPEN="$(command -v xdg-open)"


	# in case we have xdg-open...
	if test -f "$XDG_OPEN"
	then
	
cat << EOF

Your file manager should see all files in directory
$target_dir

Also this script should exit when the file manager closes. If not,
return this terminal window and press CTRL + C to exit.

EOF

		xdg-open "$target_dir/"
		rc="$?"
		
	# in case we do not have xdg-open...
	else
		rc=1
	fi


	if test "$rc" -eq 0
	then
		true
	else
	
cat << EOF

$0 requires a desktop environment (GNOME, KDE, etc) to run!!

Try manually list the backed up files using the following command:

cd "$target_dir"
ls -Alh

EOF

	fi
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

	true &&
		show_backuped_files_at
		
fi

exit_program 0
