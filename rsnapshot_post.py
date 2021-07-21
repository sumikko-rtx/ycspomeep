#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_rm import cmd_rm
from rsnapshot_compare_files import rsnapshot_compare_files
from rsnapshot_monitor import rsnapshot_monitor
from rsnapconfig_getparam_lockfile import rsnapconfig_getparam_lockfile
from constants import DEEPLY_COMPARE_FILES, NOTIFY_MAX_MISSING_FILES

import os
import datetime


def rsnapshot_post():

    #/* the file indicate the rsnapshot is in progress */
    rsnapshot_lockfile = rsnapconfig_getparam_lockfile()
    
    #/* record start backup time */
    end_time = datetime.datetime.now()
    print('INFO: end backup time: {0}'.format(end_time))

    #/* compute backup duration */
    start_time = datetime.datetime.fromtimestamp(
        os.stat(rsnapshot_lockfile).st_ctime
    )

    #/* note: duration is a timedelta obj!!! */
    duration = end_time - start_time
    print('INFO: backup duration: {0}'.format(duration))

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

        for x in files_added:
            print(
                'WARNING: file {0} was added in the source location but not successfully transferred!'.format(x))

        for x in files_modified:
            print(
                'WARNING: file {0} was modified in the source location but not successfully transferred!'.format(x))

    #/*---------------------------------------------------------------------*/

    #/* TODO place additional post procedure here */

    #/*---------------------------------------------------------------------*/

    #/* after removing file: rsnapshot_lockfile
    # * function rsnapshot_monitor() will inform to PLC instantly!!!*/
    # */
    cmd_rm(rsnapshot_lockfile, force=True)
    rsnapshot_monitor()


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_post, sys.argv[1:]))
