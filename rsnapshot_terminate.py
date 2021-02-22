#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import psutil
from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* terminate process. including its child process */
def __terminate_process(proc):
    proc_children = proc.children()
    
    for x in proc_children:
        __terminate_process(x)
        
    try:
        proc.terminate()
    except Exception as e:
        pass
    
    

#/* programlly terminate ycspomeep's rsnapshot, including the child processes
# *
# * Note: this only search for process: rsnapshot -c RSNAPSHOT_CONFIG_FILE ...
# */
def rsnapshot_terminate():
    
    #/*---------------------------------------------------------------------*/

    for proc in psutil.process_iter():

        #proc_name = proc.name()

        #/* proc.cwd() may raise Permission Denined error */
        #try:
        #    proc_cwd = proc.cwd()
        #except Exception as e:
        #    proc_cwd = ''

        proc_cmd = proc.cmdline()

        have_rsnapshot = False
        have_rsnapshot_c_switch = False
        have_rsnapshot_config_file = False
        j = 0

        #/* look for rsnapshot executable */
        while j < len(proc_cmd):
            if proc_cmd[j].endswith('rsnapshot.bin') or proc_cmd[j].endswith('rsnapshot.exe') or proc_cmd[j].endswith('rsnapshot'):
                have_rsnapshot = True
                break
            j = j + 1

        #/* look for -c switch */
        while j < len(proc_cmd):
            if proc_cmd[j] == '-c':
                have_rsnapshot_c_switch = True
                break
            j = j + 1

        #/* look for argument contains RSNAPSHOT_CONFIG_FILE */
        while j < len(proc_cmd):
            if proc_cmd[j] == DEFAULT_RSNAPSHOT_CONFIG_FILE:
                have_rsnapshot_config_file = True
                break
            j = j + 1

        #print('cmd:', proc_cmd)
        #print('cwd:', proc_cwd)
        #print('have_rsnapshot:', have_rsnapshot)
        #print('have_rsnapshot_c_switch:', have_rsnapshot_c_switch)
        #print('have_rsnapshot_config_file:', have_rsnapshot_config_file)

        #/* if all condintions fufilled, terminate that rsnapshot process */
        if have_rsnapshot and have_rsnapshot_c_switch and have_rsnapshot_config_file:

            #/* remove all lockfiles
            # * (ensure no ycspomeep rsnapshot is runnning)
            # */
            __terminate_process(proc)


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_terminate, sys.argv[1:]))
