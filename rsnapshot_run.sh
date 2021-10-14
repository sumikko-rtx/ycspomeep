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


RSNAPSHOT_CRON_FILE="$THIS_SCRIPT_DIRNAME/configs/rsnapshot_cron"
RSNAPSHOT_CRON_FILE_BASENAME="$(basename "$RSNAPSHOT_CRON_FILE")"
RSNAPSHOT_CONFIG_FILE="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE; print(DEFAULT_RSNAPSHOT_CONFIG_FILE)")"
RSNAPSHOT_SNAPSHOT_ROOT="$("$PY3" "$THIS_SCRIPT_DIRNAME/rsnapconfig_getparam_snapshot_root.py")"
RSNAPSHOT_RETAIN_LEVEL="$("$PY3" "$THIS_SCRIPT_DIRNAME/rsnapconfig_get_retain_levels.py" --idx 0)"
#echo "RSNAPSHOT_CRON_FILE=$RSNAPSHOT_CRON_FILE"
#echo "RSNAPSHOT_CRON_FILE_BASENAME=$RSNAPSHOT_CRON_FILE_BASENAME"
#echo "RSNAPSHOT_CONFIG_FILE=$RSNAPSHOT_CONFIG_FILE"
#echo "RSNAPSHOT_SNAPSHOT_ROOT=$RSNAPSHOT_SNAPSHOT_ROOT"
#echo "RSNAPSHOT_RETAIN_LEVEL=$RSNAPSHOT_RETAIN_LEVEL"


RSNAPSHOT_ALPHA_0="$RSNAPSHOT_SNAPSHOT_ROOT/$RSNAPSHOT_RETAIN_LEVEL.0"
RSNAPSHOT_LOGFILE="$RSNAPSHOT_ALPHA_0/rsnapshot.log"
RSNAPSHOT_LOGFILE_TMP="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE; print(DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE)")"
RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE="$("$PY3" "$THIS_SCRIPT_DIRNAME/rsnapconfig_getparam_lockfile.py")"
#echo "RSNAPSHOT_ALPHA_0=$RSNAPSHOT_ALPHA_0"
#echo "RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE"
#echo "RSNAPSHOT_LOGFILE_TMP=$RSNAPSHOT_LOGFILE_TMP"
#echo "RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE=$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE"


# note: these values are zero(0) or one(1)
UPDATE_FROM_GIT_ENABLE="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import UPDATE_FROM_GIT_ENABLE; print(1 if UPDATE_FROM_GIT_ENABLE else 0)")"
UPDATE_FROM_PKGMGR_ENABLE="$(cd "$THIS_SCRIPT_DIRNAME" && "$PY3" -c "from constants import UPDATE_FROM_PKGMGR_ENABLE; print(1 if UPDATE_FROM_PKGMGR_ENABLE else 0)")"
#echo "UPDATE_FROM_GIT_ENABLE=$UPDATE_FROM_GIT_ENABLE"
#echo "UPDATE_FROM_PKGMGR_ENABLE=$UPDATE_FROM_PKGMGR_ENABLE"


REPORT_CONTENT=""


msg_info()
{
	echo "INFO: $1"
	echo "INFO: $1" 1>&2
}




msg_warning()
{
	echo "WARNING: $1"
	echo "WARNING: $1" 1>&2
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




check_if_running()
{
	tmp_rc=0


	# *** IMPORTANT!!!: check if this script is running ***
	#test -f "$THIS_SCRIPT_LOCKFILE" && msg_info "THIS_SCRIPT_LOCKFILE"
	#test -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE" && msg_info "RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE"

	if test -f "$THIS_SCRIPT_LOCKFILE" || test -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE"
	then
		msg_error "$0 has already been running!!!"
		return 1
	fi


	# *** IMPORTANT!!!: check if root ***
	test "$tmp_rc" -eq 0 &&
		"$PY3" "$THIS_SCRIPT_DIRNAME/check_if_root.py" 2>&1 1>/dev/null || exit 1
	tmp_rc="$?"


	# To quickly show on PLC screen...
	test "$tmp_rc" -eq 0 &&
		touch "$THIS_SCRIPT_LOCKFILE" &&
		"$PY3" "${THIS_SCRIPT_DIRNAME}/rsnapshot_monitor.py" 
	tmp_rc="$?"


	return "$tmp_rc"
}




cron_update_config()
{
	tmp_rc=0

	# update rsnapshot_cron
	#
	# instead of copying to /etc/cron.d
	# use crontab file to import cronfig file
	#
	# remove the 6th user entry
	#
	msg_info "updating cron settings: $RSNAPSHOT_CRON_FILE ..."
	test "$tmp_rc" -eq 0 && python3 "${THIS_SCRIPT_DIRNAME}/cron_update_config.py"


	# start cron
	# (this does not check any errors and not update the rc variable)
	"$PY3" "${THIS_SCRIPT_DIRNAME}/cron_start.py"

	return "$tmp_rc"
}




mount_backup_disks()
{
	tmp_rc=0


	msg_info "turning on and mounting the backup disks..."
	test "$tmp_rc" -eq 0 &&
		"$PY3" "$THIS_SCRIPT_DIRNAME/disk_isolate_online.py" 2>&1 #|| exit 1
	tmp_rc="$?"
	
	
	return "$tmp_rc"
}




# *** the entire backup process ***
backup()
{
	tmp_rc=0


	msg_info "running rsnapshot..."
	test "$tmp_rc" -eq 0 &&
		/usr/bin/rsnapshot -c "$RSNAPSHOT_CONFIG_FILE" alpha 2>&1 #|| exit 1
	#rc="$?"
	rsnapshot_rc="$?"


	#
	# rsnapshot exit code:
	#
	# 0: all operation completed successfully
	# 1: a fatal error occured
	# 2: some warining occured, but the backup still finished
	#
	if test "$rsnapshot_rc" -eq 0 || test "$rsnapshot_rc" -eq 2
	then
		rsnapshot_rc=0
	fi
	msg_warning "rsnapshot_run.sh: backup: rsnapshot_rc=$rsnapshot_rc" #<< debug


	
	#
	# Is rsnapshot encountered an error???
	#
	"$PY3" "$THIS_SCRIPT_DIRNAME/rsnapshot_check_last_errors.py" --raise-exception True 2>&1 >/dev/null
	rsnapshot_rc="$?"
	msg_warning "rsnapshot_run.sh: backup: rsnapshot_last_error_rc=$rsnapshot_rc" #<< debug

	
	#
	# Saving backup log...
	#
	msg_info "saving rsnapshot backup log..."
	#test "0" -eq 0 &&
	#	rm -f "$RSNAPSHOT_LOGFILE" 2>&1 &&
	#	cp "$RSNAPSHOT_LOGFILE_TMP" "$RSNAPSHOT_LOGFILE"
	rsnapshot_remove_old_backup_log_error=$(rm -f "$RSNAPSHOT_LOGFILE" 2>&1 1>/dev/null)
	rsnapshot_remove_old_backup_log_rc="$?"
	rsnapshot_save_backup_log_error=$(cp "$RSNAPSHOT_LOGFILE_TMP" "$RSNAPSHOT_LOGFILE" 2>&1 1>/dev/null)
	rsnapshot_save_backup_log_rc="$?"

	msg_warning "rsnapshot_run.sh: backup: rsnapshot_remove_old_backup_log_rc=$rsnapshot_remove_old_backup_log_rc" #<< debug
	msg_warning "rsnapshot_run.sh: backup: rsnapshot_remove_old_backup_log_error=$rsnapshot_remove_old_backup_log_error" #<< debug
	
	msg_warning "rsnapshot_run.sh: backup: rsnapshot_save_backup_log_rc=$rsnapshot_save_backup_log_rc" #<< debug
	msg_warning "rsnapshot_run.sh: backup: rsnapshot_save_backup_log_error=$rsnapshot_save_backup_log_error" #<< debug
	
	msg_warning "rsnapshot_run.sh: backup: RSNAPSHOT_SNAPSHOT_ROOT=$RSNAPSHOT_SNAPSHOT_ROOT" #<< debug
	msg_warning "rsnapshot_run.sh: backup: RSNAPSHOT_LOGFILE_TMP=$RSNAPSHOT_LOGFILE_TMP" #<< debug
	msg_warning "rsnapshot_run.sh: backup: RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE" #<< debug
	
	if test "$rsnapshot_save_backup_log_rc" -eq 0 && test "$rsnapshot_rc" -eq 0
	then
		true
		#tmp_rc=0
	else
		tmp_rc=1
	fi


	return "$tmp_rc"
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




update_from_git()
{
	if test "$UPDATE_FROM_GIT_ENABLE" -eq 0
	then
		true
	else
		msg_info "updating ycspomeep if any..."
		"$PY3" "$THIS_SCRIPT_DIRNAME/update_from_git.py"
	fi
	return 0
}




update_from_pkgmgr()
{
	if test "$UPDATE_FROM_PKGMGR_ENABLE" -eq 0
	then
		true
	else
		msg_info "updating your system using package manager if any..."
		"$PY3" "$THIS_SCRIPT_DIRNAME/update_from_pkgmgr.py" 2>&1
	fi
	return 0
}




exit_program()
{
	# $1: exit code
	rc="$1"
	stage_no="$(get_backup_stage_no)"

	if test ! "$rc" -eq 0
	then
		msg_error "$0 has encounted an error(s) (exit_status=$rc)"
		msg_error "    see a log file $RSNAPSHOT_LOGFILE_TMP or $RSNAPSHOT_LOGFILE for more details"
	fi


	# umount backup disk, if any
	umount_backup_disks


	# clean up
	rm -f "$THIS_SCRIPT_LOCKFILE" 2>&1
	"$PY3" "${THIS_SCRIPT_DIRNAME}/rsnapshot_monitor.py"
	
	return "$rc"
}




interrupted=0
handle_sigint()
{
	if test "0" -eq 0
	then
		rc=1
		stage_no="$(get_backup_stage_no)"
		exit_program "$rc"
		msg_error "rsnapshot was interrupt by user! (at stage $stage_no)"
	fi | report
	exit 1
}




# *** This is the key, handle CTRL+C errors!!! ***
trap handle_sigint INT
trap handle_sigint TERM





# check if this script is running
# this should not be appeared in the backup summary!!!
check_if_running
rc="$?"





# --- the rsnapshot_run.sh main program ---
if test "$rc" -eq 0
then
	if test 1 -eq 1
	then
		rc=0

		# updating ycspomeep goes here
		set_backup_stage_no 1
		test "$rc" -eq 0 && update_from_git # << OK
		rc="$?"
		
		set_backup_stage_no 2
		test "$rc" -eq 0 && cron_update_config # << OK
		rc="$?"

		set_backup_stage_no 3
		test "$rc" -eq 0 && mount_backup_disks # << OK
		rc="$?"

		set_backup_stage_no 4
		test "$rc" -eq 0 && backup # << OK
		rc="$?"

		# exit_program will run umount_backup_disks
		set_backup_stage_no 5
		exit_program "$rc"

	fi | report
	rc=0
fi



# apply system update
# this should not be appeared in the backup summary!!!
if test "$rc" -eq 0
then
	update_from_pkgmgr
fi

exit "$?"
