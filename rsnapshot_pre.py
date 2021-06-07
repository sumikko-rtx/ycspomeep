#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from rsnapshot_monitor import rsnapshot_monitor
from cmd_touch import cmd_touch
from constants import DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE

import os
import datetime
from update_from_pkgmgr import update_from_pkgmgr
import update_from_git


def rsnapshot_pre():
    
    #/* Try to update os via package manager */
    try:
        update_from_pkgmgr()
    except Exception as e:
        pass
    
    #/* Try to update ycspomeep via git */
    try:
        update_from_git()
    except Exception as e:
        pass
        

    #/* backup start, now create a inner lock file to indicate the progress */
    cmd_touch(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE)

    #/* function rsnapshot_monitor() will inform to PLC instantly!!! */
    rsnapshot_monitor()

    #/* record start backup time */
    start_time = datetime.datetime.fromtimestamp(
        os.stat(DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE).st_ctime
    )

    print('INFO: start backup time: {0}'.format(start_time))


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_pre, sys.argv[1:]))

