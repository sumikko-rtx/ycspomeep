#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import re
from file_modified_since import file_modified_since

from rsnapconfig_getparam_lockfile import rsnapconfig_getparam_lockfile

from constants import NOTIFY_SOFT_BACKUP_SECONDS_LIMIT,\
    NOTIFY_HARD_BACKUP_SECONDS_LIMIT
    
from constants import DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE


#
# Check for rsnapshot running progress
# If rsnapshot is running, give a progress%  and backup dration seconds
#
def rsnapshot_check_running_progress(complete=False, negate=False):

    #/* this lockfile is generated during rsnapshot */
    backup_in_progress_lockfile = rsnapconfig_getparam_lockfile()

    #/* the file is generated during backup process
    # * (by rsnapshot_run.update_from_git)
    # */
    intermediate_logfile = DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE

    #/* This store progress% (assume 0%) */
    progress_percent = 0

    #/* This store backup duration seconds */
    duration_total_seconds = 0
    h = 0
    m = 0
    s = 0

    #/* True if rsnapshot is running, false otherwise */
    have_rsnapshot_running = bool(os.path.exists(backup_in_progress_lockfile))

    #/* True if duration_seconds reaches NOTIFY_SOFT_BACKUP_SECONDS_LIMIT */
    have_rsnapshot_time_reach_soft_limit = False

    #/* True if duration_seconds reaches NOTIFY_HARD_BACKUP_SECONDS_LIMIT */
    have_rsnapshot_time_reach_hard_limit = False

    #/************************************************************************/

    #/* --- check progress% --- */
    if have_rsnapshot_running:

        #/* get progress% from log file */
        try:

            with open(intermediate_logfile, 'r') as f:

                lines = f.readlines()

                #/* start read from the end of the line */
                j = len(lines) - 1
                while j >= 0:

                    g = re.search(
                        r"^\s*((?:[0-9]{1,3}(?:,[0-9]{3})*)|(?:[0-9]+[.][0-9]+[YZEPTGMk]))\s+([0-9]+)%", lines[j])
                    if g:
                        progress_percent = int(g.group(2))
                        break

                    #/* previous line... */
                    j = j - 1

        except Exception as e:
            pass

    #/************************************************************************/

    #/* --- get backup duration seconds --- */
    if have_rsnapshot_running:

        try:

            duration_total_seconds = file_modified_since(backup_in_progress_lockfile)

            #/* https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds */
            m, s = divmod(duration_total_seconds, 60)
            h, m = divmod(m, 60)

        except Exception as e:
            pass

    #/************************************************************************/

    #/* --- check rsnapshot duration (soft limit) --- */

    condition = (NOTIFY_SOFT_BACKUP_SECONDS_LIMIT > 0 and
                 duration_total_seconds >= NOTIFY_SOFT_BACKUP_SECONDS_LIMIT)

    #if negate:
    #    condition = (not condition)

    if condition:
        have_rsnapshot_time_reach_soft_limit = True

    #/************************************************************************/

    #/* --- check rsnapshot duration (hard limit) --- */

    condition = (NOTIFY_HARD_BACKUP_SECONDS_LIMIT > 0 and
                 duration_total_seconds >= NOTIFY_HARD_BACKUP_SECONDS_LIMIT)

    #if negate:
    #    condition = (not condition)

    if condition:
        have_rsnapshot_time_reach_hard_limit = True

    return have_rsnapshot_running, have_rsnapshot_time_reach_soft_limit, have_rsnapshot_time_reach_hard_limit, progress_percent, h, m, s, duration_total_seconds


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_check_running_progress, sys.argv[1:]))
