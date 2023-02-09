#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from rsnapshot_monitor import rsnapshot_monitor
#from cmd_touch import cmd_touch
from rsnapconfig_getparam_lockfile import rsnapconfig_getparam_lockfile

import os
import datetime
from rsnapshot_check_snapshot_root_usage import rsnapshot_check_snapshot_root_usage


def rsnapshot_pre():

    #/* function rsnapshot_monitor() will inform to PLC instantly!!! */
    rsnapshot_monitor()
    
    #/* check rsnapshot disk usage first before backup */
    rsnapshot_check_snapshot_root_usage()

    #/* the a lockfile, indicate rsnapshot is in progress */
    rsnapshot_lockfile = rsnapconfig_getparam_lockfile()

    #/* get the datetime created of a rsnapshot_lockfile  */
    #/* this indicated a  start backup time */
    start_time = datetime.datetime.fromtimestamp(
        os.stat(rsnapshot_lockfile).st_ctime
    )

    print('INFO: start backup time: {0}'.format(start_time))


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_pre, sys.argv[1:]))

