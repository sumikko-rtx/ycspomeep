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
THIS_SCRIPT_DIR="$(dirname "$THIS_SCRIPT_FILE")"
#echo "THIS_SCRIPT_FILE=$THIS_SCRIPT_FILE"
#echo "THIS_SCRIPT_DIR=$THIS_SCRIPT_DIR"


RSNAPSHOT_CONFIG_FILE="$(cd "$THIS_SCRIPT_DIR" && /usr/bin/python3 -c "from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE; print(DEFAULT_RSNAPSHOT_CONFIG_FILE)")"
RSNAPSHOT_SNAPSHOT_ROOT="$(/usr/bin/python3 "$THIS_SCRIPT_DIR/rsnapconfig_getparam_snapshot_root.py")"
RSNAPSHOT_RETAIN_LEVEL="$(/usr/bin/python3 "$THIS_SCRIPT_DIR/rsnapconfig_get_retain_levels.py" --idx 0)"
#echo "RSNAPSHOT_CONFIG_FILE=$RSNAPSHOT_CONFIG_FILE"
#echo "RSNAPSHOT_SNAPSHOT_ROOT=$RSNAPSHOT_SNAPSHOT_ROOT"
#echo "RSNAPSHOT_RETAIN_LEVEL=$RSNAPSHOT_RETAIN_LEVEL"

RSNAPSHOT_ALPHA_0="$RSNAPSHOT_SNAPSHOT_ROOT/$RSNAPSHOT_RETAIN_LEVEL.0"
RSNAPSHOT_LOGFILE="$RSNAPSHOT_ALPHA_0/rsnapshot.log"
RSNAPSHOT_LOGFILE_TMP="/tmp/plc_rsnapshot_output.log"
#echo "RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE"
#echo "RSNAPSHOT_LOGFILE=$RSNAPSHOT_LOGFILE"


RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE="$(cd "$THIS_SCRIPT_DIR" && /usr/bin/python3 -c "from constants import DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE; print(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE)")"


cleanup()
{
	rm -f "$RSNAPSHOT_BACKUP_IN_PROGRESS_LOCKFILE" 2>&1
	/usr/bin/python3 "${THIS_SCRIPT_DIR}/rsnapshot_monitor.py" 
}



report()
{
	tee "$RSNAPSHOT_LOGFILE_TMP" "$RSNAPSHOT_LOGFILE" |
		/usr/bin/perl "${THIS_SCRIPT_DIR}/rsnapreport.pl" |
		/usr/bin/python3 "${THIS_SCRIPT_DIR}/email_report.py" --message-file - --subject "rsnapshot summary"
}


handle_interrupt()
{
	echo "ERROR: rsnapshot was interrupt by user!" | report
	cleanup
	exit 1
}


# *** This is the key, handle CTRL+C errors!!! ***
trap handle_interrupt INT
trap handle_interrupt TERM
trap handle_interrupt KILL




# *** copy configs/rsnapshot_cron to /etc/cron.d first ***
cp "$THIS_SCRIPT_DIR/configs/rsnapshot_cron" /etc/cron.d





# *** run rsnapshot ***

#
# Accoring to manpage:
# 0: backup success
# 1: fatal error occured
# 2: same as 0, but have some warnings
#

STEP1_OUTPUT="$(test 0 -eq 0 && mkdir -p "$RSNAPSHOT_ALPHA_0" 2>&1)"
STEP1_RC="$?"
if test ! "$STEP1_RC" -eq 0 && test -n "$STEP1_OUTPUT"
then
	RSNAPSHOT_OUTPUT="ERROR: cannot start rsnapshot: $STEP1_OUTPUT"
fi


STEP2_OUTPUT="$(test "$STEP1_RC" -eq 0 && rm -f "$RSNAPSHOT_LOGFILE" 2>&1)"
STEP2_RC="$?"
if test ! "$STEP2_RC" -eq 0 && test -n "${STEP2_OUTPUT}"
then
	RSNAPSHOT_OUTPUT="ERROR: cannot start rsnapshot: $STEP2_OUTPUT"
fi


RSNAPSHOT_OUTPUT="$(test "$STEP2_RC" -eq 0 && /usr/bin/rsnapshot -c "$RSNAPSHOT_CONFIG_FILE" alpha 2>&1)"
RSNAPSHOT_RC="$?"

echo "$RSNAPSHOT_OUTPUT" | report
