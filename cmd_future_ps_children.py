#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
import os




def __cmd_future_ps_children_linux(pid):

    pid_children = []

    #/* cat /proc/<PID>/task/<PID>/children
    # * 
    # * child ps are space-separated
    # */
    target_file = os.path.join(
        os.sep, 'proc', str(pid), 'task', str(pid), 'children'
    )

    try:
        with open(target_file, 'rb') as f:
            for x in f.read().split(b' '):
                if x:
                    pid_children.append(int(x))

    except Exception as e:
        #print(e)
        pass

    return pid_children








def __cmd_future_ps_children_windows(pid):

    pid_children = []

    rc,output,unused,unused = system_cmd(
            *[
                'wmic',
                'process',
                'where',
                '(ParentProcessId={0})'.format(pid),
                'get',
                'ProcessId',
                ]
            )

    #/* NOTE: ignore the table header */
    output_lines = output.splitlines()
    for line in output_lines[1:]:

        #/* skip empty line */
        if not line:
            continue

        pid_children.append(int(line))


    return pid_children











#
# List child process by given parent pids
#
# This is a temporary code for current ycspomeep code
# and will be removed in future.
#
def cmd_future_ps_children(pid):

    pid_children = []

    if sys.platform in ['win32', 'cygwin', 'msys']:

        if sys.platform in ['cygwin', 'msys']:

            try:
                tmp = __cmd_future_ps_children_linux(pid)
                pid_children.extend(tmp)

            except Exception as e:
                pass

        tmp = __cmd_future_ps_children_windows(pid)
        pid_children.extend(tmp)

    else:
        tmp = __cmd_future_ps_children_linux(pid)
        pid_children.extend(tmp)

    ''' 
    for x in pid_children:
        print(x['pid'],x['caption'],x['cmdline'])
    return None
    '''
    
    return pid_children


 





if __name__ == '__main__':
    print(simple_argparse(cmd_future_ps_children, sys.argv[1:]))

