#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from file_list import file_list
import os
import re



def __cmd_future_ps_list_linux():

    #
    # list file content in /proc
    # then extract sub-directories where directory name is number only
    #
    # to get command is running: tr '\000' ' ' < /proc/<PID>/cmdline 
    #
    processes = []

    proc_dir = os.path.join(os.sep,'proc')

    proc_subdirs = file_list(proc_dir,
              list_directories=True,
              min_filesize=0,
              max_filesize=-1,
              regex='/[0-9]+$',
              )

    for x in proc_subdirs:
        
        pid = os.path.basename(x)
        target_file = os.path.join(x,'cmdline')


        try:
            with open(target_file, 'rb') as f:

                #/* remove any empty entries */
                cmdline = []
                for y in f.read().split(b'\0'):
                    y = y.decode()
                    if y:
                        cmdline.append(y)

                processes.append(
                        dict(
                            #caption=caption,
                            pid=int(pid),
                            cmdline=cmdline,
                            )
                        )
                
        except Exception as e:
            print(e)
            pass

    return processes





def __cmd_future_ps_list_windows():

    #/* wmic process via WMI */
    rc, output, unused, unused = system_cmd(*['wmic', 'process', 'get', 'Caption,CommandLine,ProcessId'])
    
    processes = []
    output_lines = output.splitlines()

    #/* display order: Caption, CommandLine, ProcessId */
    #/* NOTE: exclude table header */
    for line in output_lines[1:]:

        #/* remove empty line... */
        line = line.strip()
        #print('line:', line)
        if not line:
            continue


        #/* get pid, caption */
        tmp = line.split()
        pid = tmp[-1]
        caption = tmp[0]


        #/* get cmdline by removing pid and caption in line ONCE_only */
        line = line.replace(pid,'', 1)
        line = line.replace(caption,'', 1)
        line = line.strip()
        #print('line:', line)


        cmdline = list(re.findall("(?:\".*?\"|\S)+", line))
        #print(cmdline)
       

        processes.append(
                dict(
                    caption=caption,
                    pid=int(pid),
                    cmdline=cmdline,
                    )
                )

    return processes






#
# Show All Running Processes
#
# This is a temporary code for current ycspomeep code
# and will be removed in future.
#
def cmd_future_ps_list():

    processes=[]

    if sys.platform in ['win32','cygwin','msys']:

        if sys.platform in ['cygwin','msys']:

            try:
                tmp=__cmd_future_ps_list_linux()
                processes.extend(tmp)

            except Exception as e:
                pass

        tmp = __cmd_future_ps_list_windows()
        processes.extend(tmp)

    else:
        tmp = __cmd_future_ps_list_linux()
        processes.extend(tmp)

    ''' 
    for x in processes:
        print(x['pid'],x['caption'],x['cmdline'])
    return None
    '''
    
    return processes

    '''
    #/* ps -aux also work!!! */
    
    #/* sample output:
    # *
    # * USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    # * root           1  0.0  0.0 167928 11804 ?        Ss   09:32   0:11 /sbin/init splash
    # * root         390  0.0  0.1 103224 62256 ?        S<s  09:32   0:02 /lib/systemd/systemd-journald
    # * root         425  0.0  0.0  24140  7712 ?        Ss   09:32   0:01 /lib/systemd/systemd-udevd
    # */

    rc, output, unused, unused = system_cmd(
        *['ps', 'aux'],
    )

    output_lines = output.splitlines()
    
    processes = []

    #/* NOTE: exclude table header!!! */
    for line in output_lines[1:]:

        #/* split by whitespaces up to 10 times */
        entries = line.split(None, 10)

        tmp = {
            'user': entries[0],
            'pid': entries[1],
            'cpu_percent': entries[2],
            'mem_percent': entries[3],
            'user': entries[4],
            'rss': entries[5],
            'tty': entries[6],
            'stat': entries[7],
            'start': entries[8],
            'time': entries[9],
        }
        
        #/* parse cmd into list */
        #/* tr '000' ' ' < /proc/<PID>/cmdline */
        target_file = os.path.join(
            os.sep, 'proc', tmp['pid'], 'cmdline'
        )

        try:
            with open(target_file, 'rb') as f:
                tmp['cmdline'] = [x.decode() for x in f.read().split(b'\0')]
                tmp['pid'] = int(tmp['pid'])
                processes.append(tmp)
                
        except Exception as e:
            #print(e)
            pass

    return processes
    '''



if __name__ == '__main__':
    print(simple_argparse(cmd_future_ps_list, sys.argv[1:]))

