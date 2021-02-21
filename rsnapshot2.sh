#!/bin/sh
# this script does the following:
#
# rsnapshot rsnapshot.cfg alpha 2>&1 | tee snapshot_root/alpha.0/rsnapshot.log | rsnapreport.pl | email_report.py
# (1)                                  (2)                                       (3)              (4)
#
# (1) run rsnapshot backup
# (2) convert the rsnapshot output as log
# (3) generate the backup summary
# (4) email that summary to recipents
#
MYCWD="$(dirname "$0")"
MYCWD="$(readlink -f "$MYCWD")"

ALPHA_ZERO="$(/usr/bin/python3 "$MYCWD/rsnapconfig_get_retain_levels.py" --include-snapshot-root True --idx 0).0"
INTERMEDIATE_LOGFILE=$(/usr/bin/python3 -c "from configs.other_settings import DEFAULT_RSNAPSHOT_INTERMEDIATE_LOGFILE; print(DEFAULT_RSNAPSHOT_INTERMEDIATE_LOGFILE)")
FINAL_LOGFILE="$ALPHA_ZERO/rsnapshot.log"

#echo $SNAPSHOT_ROOT
#echo $ALPHA_ZERO
#echo $INTERMEDIATE_LOGFILE
#echo $FINAL_LOGFILE


/usr/bin/rsnapshot -c "$MYCWD/configs/rsnapshot.cfg" alpha 2>&1 |
	/usr/bin/perl $MYCWD/rsnapreport.pl
	#/usr/bin/python3 email_report.py --message-file - --subject "rsnapshot summary: `/usr/bin/date +%Y-%m-%d`"

echo "saving rsnapshot log..."
if true
then
	rm -f "$FINAL_LOGFILE"
	cp "$INTERMEDIATE_LOGFILE" "$FINAL_LOGFILE"
fi 2>/dev/null
