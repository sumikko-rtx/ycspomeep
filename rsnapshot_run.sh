#!/bin/sh

# this script does the following:
#
# rsnapshot rsnapshot.cfg alpha 2>&1 | tee snapshot_root/alpha.0/rsnapshot.log | rsnapreport.pl | email_report.py
# (1)                                  (2)                                       (3)              (4)
#
# (1) run rsnapshot backup
# (2) save all rsnapshot progress into log
# (3) use that file generate the backup summary
# (4) email that summary to recipients
#
# to properly run this script, you must set
#
# (1) verbose >= 4
# (2) add --stats to rsync_long_args
#
# in the rsnapshot.conf
#
# this script shall capture all rsnapshot errors
# including CTRL+C interrupt
#


THIS_SCRIPT_FILE="$(readlink -f "$0")"
THIS_SCRIPT_DIRNAME="$(dirname "$THIS_SCRIPT_FILE")"
THIS_SCRIPT_BASENAME="$(basename "$THIS_SCRIPT_FILE")"
THIS_SCRIPT_LOCKFILE="/tmp/$THIS_SCRIPT_BASENAME.lock"
#echo "THIS_SCRIPT_FILE=$THIS_SCRIPT_FILE"
#echo "THIS_SCRIPT_DIRNAME=$THIS_SCRIPT_DIRNAME"
#echo "THIS_SCRIPT_BASENAME=$THIS_SCRIPT_BASENAME"
#echo "THIS_SCRIPT_LOCKFILE=$THIS_SCRIPT_LOCKFILE"


PY3="/usr/bin/python3"
PERL="/usr/bin/perl"


RSNAPSHOT_CONFIG_FILE="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE; print(DEFAULT_RSNAPSHOT_CONFIG_FILE)")"
RSNAPSHOT_SNAPSHOT_ROOT="$("$PY3" "$THIS_SCRIPT_DIRNAME/rsnapconfig_getparam_snapshot_root.py")"
RSNAPSHOT_RETAIN_LEVEL="$("$PY3" "$THIS_SCRIPT_DIRNAME/rsnapconfig_get_retain_levels.py" --idx 0)"
#echo "RSNAPSHOT_CONFIG_FILE=$RSNAPSHOT_CONFIG_FILE"
#echo "RSNAPSHOT_SNAPSHOT_ROOT=$RSNAPSHOT_SNAPSHOT_ROOT"
#echo "RSNAPSHOT_RETAIN_LEVEL=$RSNAPSHOT_RETAIN_LEVEL"


RSNAPSHOT_ALPHA_0="$RSNAPSHOT_SNAPSHOT_ROOT/$RSNAPSHOT_RETAIN_LEVEL.0"
RSNAPSHOT_LOGFILE="$RSNAPSHOT_ALPHA_0/rsnapshot.log"
RSNAPSHOT_LOGFILE_TMP="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE; print(DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE)")"
#echo "RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE"
#echo "RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE"


RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE; print(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE)")"


REPORT_CONTENT=""


msg_info()
{
	echo "INFO: $1"
	echo "INFO: $1" 1>&2
}




msg_error()
{
	echo "ERROR: $1"
	echo "ERROR: $1" 1>&2
}




report()
{
	tee "$RSNAPSHOT_LOGFILE_TMP" |
		/usr/bin/perl "${THIS_SCRIPT_DIRNAME}/rsnapreport.pl" |
	"$PY3" "${THIS_SCRIPT_DIRNAME}/email_report.py" --message-file - --subject "rsnapshot summary"
}




check_if_running()
{
	rc=0


	# *** IMPORTANT!!!: check if this script is running ***
	test -f "$THIS_SCRIPT_LOCKFILE" && msg_info "THIS_SCRIPT_LOCKFILE"
	test -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE" && msg_info "RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE"

	if test -f "$THIS_SCRIPT_LOCKFILE" || test -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE"
	then
		msg_error "$0 has already been running!!!"
		return 1
	fi


	# *** IMPORTANT!!!: check if root ***
	test "$rc" -eq 0 &&
		"$PY3" "$THIS_SCRIPT_DIRNAME/check_if_root.py" 2>&1 || exit 1
	rc="$?"

	msg_info "copying $THIS_SCRIPT_DIRNAME/configs/rsnapshot_cron to /etc/cron.d ..."
	test "$rc" -eq 0 &&
		cp "$THIS_SCRIPT_DIRNAME/configs/rsnapshot_cron" /etc/cron.d 2>&1 || exit 1
	rc="$?"


	# To quickly show on PLC screen...
	test "$rc" -eq 0 &&
		touch "$THIS_SCRIPT_LOCKFILE" &&
		touch "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE" &&
		"$PY3" "${THIS_SCRIPT_DIRNAME}/rsnapshot_monitor.py" 
	rc="$?"


	return "$rc"
}




set_backup_stage_no()
{
	# make sure $1 is a number!!!
	if test "$1" -eq 0
	then
		true
	fi
	echo "$1" > "$THIS_SCRIPT_LOCKFILE"
}




get_backup_stage_no()
{
       cat "$THIS_SCRIPT_LOCKFILE"	
}




mount_backup_disks()
{
	rc=0


	msg_info "turning on and mounting the backup disks..."
	test "$rc" -eq 0 &&
		"$PY3" "$THIS_SCRIPT_DIRNAME/disk_isolate_online.py" 2>&1 || exit 1
	rc="$?"
	
	
	return "$rc"
}




# *** the entire backup process ***
backup()
{
	rc=0


	msg_info "running rsnapshot..."
	test "$rc" -eq 0 &&
		/usr/bin/rsnapshot -c "$RSNAPSHOT_CONFIG_FILE" alpha 2>&1 #|| exit 1
	#rc="$?"
	rsnapshot_rc="$?"


	msg_info "saving rsnapshot backup log..."
	test "0" -eq 0 &&
		rm -f "$RSNAPSHOT_LOGFILE" 2>&1 &&
		cp "$RSNAPSHOT_LOGFILE_TMP" "$RSNAPSHOT_LOGFILE"
	rc="$?"


	if test "$rc" -eq 0 && test "$rsnapshot_rc" -eq 0
	then
		true
	else
		rc=1
	fi


	return "$rc"
}




umount_backup_disks()
{
	rc=0


	msg_info "unmounting and turning off the backup disks..."
	test "$rc" -eq 0 &&
		"$PY3" "$THIS_SCRIPT_DIRNAME/disk_isolate_offline.py" 2>&1 || exit 1
	rc="$?"


	return "$rc"
}




exit_program()
{
	stage_no="$(get_backup_stage_no)"

	if test ! "$rc" -eq 0
	then

		msg_error "$0 has encounted an error(s) (exit_status=$rc)"
		msg_error "    see a log file $RSNAPSHOT_LOGFILE_TMP for more details"

		# umount backup disk, if any
		if test "$stage_no" -ge 2
		then
			umount_backup_disks
		fi

	fi


	# clean up
	rm -f "$THIS_SCRIPT_LOCKFILE" 2>&1
	rm -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE" 2>&1
	"$PY3" "${THIS_SCRIPT_DIRNAME}/rsnapshot_monitor.py" 
}




interrupted=0
handle_interrupt()
{
	if test "$interrupted" -eq 0
	then
		interrupted=1
		if test "0" -eq 0
		then
			rc=1
			stage_no="$(get_backup_stage_no)"
			exit_program
			msg_error "rsnapshot was interrupt by user! (at stage $stage_no)"
		fi | report
	fi
	exit 1
}





# *** This is the key, handle CTRL+C errors!!! ***
trap handle_interrupt INT
trap handle_interrupt TERM
#trap handle_interrupt KILL



if test "0" -eq 0
then

	rc=0

	#set_backup_stage_no 0
	test "$rc" -eq 0 && check_if_running # << OK
	rc="$?"

	set_backup_stage_no 1
	test "$rc" -eq 0 && mount_backup_disks # << OK
	rc="$?"

	set_backup_stage_no 2
	test "$rc" -eq 0 && backup # << OK
	rc="$?"

	set_backup_stage_no 3
	test "$rc" -eq 0 && umount_backup_disks 
	rc="$?"

	exit_program

fi | report
exit 0
