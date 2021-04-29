#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_rm_r import cmd_rm_r
from rsnapshot_compare_files import rsnapshot_compare_files
from rsnapshot_monitor import rsnapshot_monitor
from constants import DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE,\
    DEEPLY_COMPARE_FILES, NOTIFY_MAX_MISSING_FILES

import os
import datetime


def rsnapshot_post():

    #/* record start backup time */
    end_time = datetime.datetime.now()
    print('INFO: end backup time: {0}'.format(end_time))

    #/* compute backup duration */
    start_time = datetime.datetime.fromtimestamp(
        os.stat(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE).st_ctime
    )

    #/* note: duration is a timedelta obj!!! */
    duration = end_time - start_time
    print('INFO: backup duration: {0}'.format(duration))


    #/* backup end, now delete a inner lock file */
    cmd_rm_r(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE, force=True)

    #/*---------------------------------------------------------------------*/

    #/* verify files on alpha.0 by comparing src and dest directory
    # * (backup only)
    # */
    files_added, files_modified, files_removed = rsnapshot_compare_files(
        deeply=DEEPLY_COMPARE_FILES)

    #/* when successfully rsnapshot(ed) files_added, files_modified, files_removed
    # * should leave empty
    # *
    # * if found, raise warning
    # */
    missing_files = len(files_added) + len(files_modified)

    if missing_files >= 0 and missing_files >= NOTIFY_MAX_MISSING_FILES:

        print('ERROR: Over {0} file(s) in the source location was/were not still transferred! The source and/or destination location(s) may encountered some problems!'.format(
            missing_files))

    else:

        #if not files_added:
        #    files_added.append('meepmeep.txt')
        #if not files_modified:
        #    files_modified.append('meepmeep.jpg')

        for x in files_added:
            print(
                'WARNING: file {0} was added in the source location but not successfully transferred!'.format(x))

        for x in files_modified:
            print(
                'WARNING: file {0} was modified in the source location but not successfully transferred!'.format(x))

    #/*---------------------------------------------------------------------*/

    #/* TODO place additional post procedure here */

    #/*---------------------------------------------------------------------*/

    #/* after removing file: DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE
    # * function rsnapshot_monitor() will inform to PLC instantly!!!*/
    # */
    rsnapshot_monitor()


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_post, sys.argv[1:]))
