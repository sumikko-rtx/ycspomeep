#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd


#
# Return the output from command: uname -a
#
def cmd_future_reboot():

    if sys.platform in ['win32', 'cygwin', 'msys']:
        
        #/* /t 0: reboot immediately */
        system_cmd(*['shutdown', '/r', '/t', '0'])
        
    else:
        system_cmd(*['reboot'])


if __name__ == '__main__':
    print(simple_argparse(cmd_future_reboot, sys.argv[1:]))
