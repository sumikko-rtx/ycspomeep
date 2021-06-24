#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
import os
import signal


def __cmd_future_ps_terminate_windows(pid):

    system_cmd(cmd=[

        #/* Windows XP Professional or later */
        'TASKKILL', '/PID', str([pid]), '||',

        #/* Windows XP Home */
        'TSKILL', str([pid]), '||',

        #/* Pskill, with sysinternal installed */
        'pskill', str([pid]),

    ])









def __cmd_future_ps_terminate_unix(pid):
    os.kill(pid, signal.SIGTERM)
    
    
    
    

#
# Raise SIGTERM to given process
#
# This is a temporary code for current ycspomeep code
# and will be removed in future.
#
def cmd_future_ps_terminate(pid):
    
    pid = int(pid)

    #/* window: use taskkill /pid */
    if sys.platform in ['win32', 'cygwin', 'msys']:

        #/* try unix-like first!!! */
        if sys.platform in ['cygwin', 'msys']:
            try:
                __cmd_future_ps_terminate_unix(pid)
            except Exception as e:
                pass

        __cmd_future_ps_terminate_windows(pid)

    else:
        __cmd_future_ps_terminate_unix(pid)


    
    

    


if __name__ == '__main__':
    print(simple_argparse(cmd_future_ps_terminate, sys.argv[1:]))
