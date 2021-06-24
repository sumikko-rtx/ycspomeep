#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse

from plc_report import plc_report

from rsnapshot_check_snapshot_root_usage import rsnapshot_check_snapshot_root_usage
from rsnapshot_check_running_progress import rsnapshot_check_running_progress

from rsnapshot_terminate import rsnapshot_terminate
from rsnapconfig_getparam_snapshot_root import rsnapconfig_getparam_snapshot_root
from email_report2 import email_report2
from constants import PLC_RWADDR_BACKUP_STATUS,\
    PLC_RWCODE_BACKUP_STATUS_FAILED, PLC_RWCODE_BACKUP_STATUS_OK,\
    PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS, PLC_RWADDR_SERVER_PRESENCE_DETECT,\
    PLC_RWCODE_SERVER_PRESENT
from rsnapshot_check_last_errors import rsnapshot_check_last_errors


def rsnapshot_monitor():

    warning_msgs = []
    error_msgs = []

    #/*---------------------------------------------------------------------*/

    #/* presence detect */

    plc_report(write_rw_values=[
               PLC_RWADDR_SERVER_PRESENCE_DETECT, PLC_RWCODE_SERVER_PRESENT])

    #/*---------------------------------------------------------------------*/

    #/* monitor rsnapshot snapshot_root usage */
    snapshot_root = rsnapconfig_getparam_snapshot_root()
    have_snapshot_root_exist, have_low_disk_space, bytes_used, bytes_free, bytes_total, percent_used, percent_free = rsnapshot_check_snapshot_root_usage(
        negate=False)

    #/* TODO we will write bytes_usedto plc in future version */
    #/* TODO we will write bytes_total to plc in future version */

    #/* can this program read snapshot_root? */
    if have_snapshot_root_exist:

        warning_msgs.append(
            '{0}: directory cannot be read!!! It may be removed to somewhere else!!!'.format(
                snapshot_root,
            )
        )

    #/* exceed NOTIFY_MAX_DISK_USED_PERCENT? */
    if have_low_disk_space:

        warning_msgs.append(
            '{0} has only {1:.1f}% ({2} bytes) disk space remaining!!! Try to delete some old or unnecessary files!!!'.format(
                snapshot_root,
                percent_free,
                bytes_free,
            )
        )

    #/*---------------------------------------------------------------------*/

    #/* monitor rsnapshot running progress */
    have_rsnapshot_running, have_rsnapshot_time_reach_soft_limit, have_rsnapshot_time_reach_hard_limit, progress_percent, h, m, s, duration_total_seconds = rsnapshot_check_running_progress(
        negate=False)

    if have_rsnapshot_running:

        print('INFO: rsnapshot is running: progress: {0}%'.format(
            progress_percent))

        #/* tell plc backup is running + progress %*/
        plc_report(write_rw_values=[
                   PLC_RWADDR_BACKUP_STATUS, PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS])

        #/* TODO we will write progress% to plc in future version */

        print('INFO: time elapses: {0} hours {1} minutes {2} seconds'.format(
            h, m, s))

        #/* hit soft backup time limit */
        if have_rsnapshot_time_reach_soft_limit:

            warning_msgs.append(
                'you have started a file backup for over {0} hours {1} minutes.'.format(
                    h, m,
                )
            )

        #/* hit hard backup time limit
        # * in this case, terminate ycspomeep's rsnapshot
        # * the effect is same as CTRL+C
        # */
        if have_rsnapshot_time_reach_hard_limit:

            error_msgs.append(
                'Your backup job was interrupted since the duration exceeds the hard limit of {0} hours {1} minutes!!!'.format(
                    h, m,
                )
            )

            rsnapshot_terminate()

    #/*---------------------------------------------------------------------*/

    #/* if rsnapshot not running, check for the last backup log */
    else:

        print('INFO: rsnapshot is now not running!!! Checking the status from last backup log...')

        rsnapshot_errors = rsnapshot_check_last_errors()
        #print('rsnapshot_errors:',rsnapshot_errors)

        #/* 0: backup success
        # * 1: backup failed
        # * 2: backup in progress
        # */
        if rsnapshot_errors:
            plc_report(write_rw_values=[
                       PLC_RWADDR_BACKUP_STATUS, PLC_RWCODE_BACKUP_STATUS_FAILED])

        else:
            plc_report(write_rw_values=[
                       PLC_RWADDR_BACKUP_STATUS, PLC_RWCODE_BACKUP_STATUS_OK])

    #/*---------------------------------------------------------------------*/

    if warning_msgs or error_msgs:

        #/* controls the notification intervals */
        pidname = ''
        wait_interval_seconds = 0

        if have_rsnapshot_time_reach_hard_limit:
            #/* the message will be informed immediately!!! */
            pass

        else:
            pidname = 'plc_b_backup_too_long_soft'
            wait_interval_seconds = 3600  # /* << 1 hours */

        #/* send notification message... */
        email_report2(
            warning_msgs=warning_msgs,
            error_msgs=error_msgs,
            pidname=pidname,
            wait_interval_seconds=wait_interval_seconds,
        )


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_monitor, sys.argv[1:]))

