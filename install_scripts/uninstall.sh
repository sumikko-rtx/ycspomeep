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
ycspomeep_prog_dir="$(readlink -f "$this_script_dirname/../")"
ycspomeep_configs_dir="$(readlink -f "$ycspomeep_prog_dir/configs/")"



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

    -e --export-config-dir  Export the user's configurations (Files in directory <ycspomeep_root>/config/).
                            to the given directory before removing.

    -n --dry-run            Dry run. Do not make any changes.

    -h --help               Show this help message and then exit.

EOF
}




#
# parse input arguments $@
#
parse_args()
{
	# list of default values
	export_config_dir=""
	dry_run="0"
	
	# read options goes here!!!
	parsed_options="$(getopt --options "e:nh" --longoptions 'export-config-dir:,dry-run,help' -- "$@")"
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
		
			-e|--export-config-dir)
				export_config_dir="$2"
				shift 2
				;;
				
			-n|--dry-run)
				dry_run="1"
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
# export ycspomeep user's config
#
export_config()
{
	x="$ycspomeep_configs_dir"
	if test -n "$ycspomeep_configs_dir"
	then
		if test ! "$dry_run" -eq 0
		then
			echo rsync -avn "$x/" "$export_config_dir/"
			rsync -avn "$x/" "$export_config_dir/"
		else
			# -q: slient rsync
			rsync -avq "$x/" "$export_config_dir/"
		fi
	fi
}




#
# completely remove ycspomeep
#
remove_ycspomeep()
{
	x="$ycspomeep_prog_dir"
	if test ! "$dry_run" -eq 0
	then
		echo rm -rf "$x/"
	else
		rm -rf "$x/"
	fi
}




#
# tell what should we do when reinstalling ycspomeep
#
tips_after_reinstall_ycspomeep()
{
cat << EOF

--- Your ycspomeep backup program has been uninstalled successfully!!! ---

EOF

	if test -n "$export_config_dir"
	then
	
cat << EOF

The backup configuation(s) has been backed up to the direcory
$export_config_dir.

If you suppose to use ycspomeep backup program again, you have
to restore those configuration(s) manaually using the following
commands by root:

rsync -av "$export_config_dir/" "$ycspomeep_configs_dir/"
sh "$ycspomeep_prog_dir/rsnapshot_run.sh"

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
	# --- begin of uninstall code ---
	true &&
		export_config &&
		remove_ycspomeep &&
		tips_after_reinstall_ycspomeep
	# --- end of uninstall code ---
fi

exit_program 0
