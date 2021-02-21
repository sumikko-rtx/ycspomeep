#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_rm_r import cmd_rm_r
from rsnapconfig_get_lockfile import rsnapconfig_get_lockfile
from rsnapshot_monitor import rsnapshot_monitor


def rsnapshot_post():

    #/* function rsnapshot_monitor() will inform to PLC instantly!!! */

    #/* to change state from PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS to
    # * PLC_RWCODE_BACKUP_STATUS_OK / PLC_RWCODE_BACKUP_STATUS_FAILED
    # * a rsnapshot lockfile must be removed
    # *
    # * the lockfile will be found from lockfile tage in default rsnapshot config file
    # */
    lockfile = rsnapconfig_get_lockfile()
    cmd_rm_r(lockfile, force=True)
    rsnapshot_monitor()


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_post, sys.argv[1:]))

