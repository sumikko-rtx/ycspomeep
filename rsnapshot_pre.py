#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from rsnapshot_monitor import rsnapshot_monitor
#from cmd_touch import cmd_touch
from rsnapconfig_getparam_lockfile import rsnapconfig_getparam_lockfile

import os
import datetime
from update_from_pkgmgr import update_from_pkgmgr
from update_from_git import update_from_git


def rsnapshot_pre():

    #/* the file indicate the rsnapshot is in progress */
    rsnapshot_lockfile = rsnapconfig_getparam_lockfile()

    #/* function rsnapshot_monitor() will inform to PLC instantly!!! */
    rsnapshot_monitor()

    #/* record start backup time */
    start_time = datetime.datetime.fromtimestamp(
        os.stat(rsnapshot_lockfile).st_ctime
    )

    print('INFO: start backup time: {0}'.format(start_time))


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_pre, sys.argv[1:]))

