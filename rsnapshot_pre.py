#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from rsnapshot_monitor import rsnapshot_monitor


def rsnapshot_pre():

    #/* function rsnapshot_monitor() will inform to PLC instantly!!! */
    rsnapshot_monitor()


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_pre, sys.argv[1:]))

