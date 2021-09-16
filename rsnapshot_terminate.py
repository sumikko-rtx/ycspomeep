
#!/usr/bin/env python3
import os
import sys
from simple_argparse import simple_argparse
from cmd_future_ps_list import cmd_future_ps_list
from cmd_future_ps_children import cmd_future_ps_children
from cmd_future_ps_terminate import cmd_future_ps_terminate

from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* terminate process. including its child process */
def __terminate_process(pid):
   
    proc_children_pids=[]

    #/* FIXME on windows, cmd_future_ps_terminate failed if no found */
    try:
        tmp = cmd_future_ps_children(pid)
        proc_children_pids.extend(tmp)
    except Exception as e:
        pass
    
    for x in proc_children_pids:
        __terminate_process(x)
        
    try:
        cmd_future_ps_terminate(pid)
    except Exception as e:
        pass
    
    

#/* programlly terminate ycspomeep's rsnapshot, including the child processes
# *
# * Note: this only search for process: rsnapshot -c RSNAPSHOT_CONFIG_FILE ...
# */
def rsnapshot_terminate():
    
    #/*---------------------------------------------------------------------*/

    for proc in cmd_future_ps_list():

        #proc_name = proc.name()

        #/* proc.cwd() may raise Permission Denined error */
        #try:
        #    proc_cwd = proc.cwd()
        #except Exception as e:
        #    proc_cwd = ''
        proc_pid = proc['pid']
        proc_cmd = proc['cmdline']

        have_rsnapshot = False
        have_rsnapshot_c_switch = False
        have_rsnapshot_config_file = False
        j = 0

        #/* look for rsnapshot executable */
        while j < len(proc_cmd):
            if proc_cmd[j].endswith('rsnapshot.bin') or proc_cmd[j].endswith('rsnapshot.exe') or proc_cmd[j].endswith('rsnapshot'):
                #print('meepmeep:', proc_cmd[j])
                have_rsnapshot = True
                break
            j = j + 1

        #/* look for -c switch */
        while j < len(proc_cmd):
            if proc_cmd[j] == '-c':
                #print('meepmeep: -c')
                have_rsnapshot_c_switch = True
                break
            j = j + 1





        #/* look for argument contains RSNAPSHOT_CONFIG_FILE */
        while j < len(proc_cmd):
        
            #/* config file may be relative, use realpath to get actual, absolute path */ 
            tmp = os.path.realpath(proc_cmd[j])
            
            if tmp == DEFAULT_RSNAPSHOT_CONFIG_FILE:
                #print('meepmeep: DEFAULT_RSNAPSHOT_CONFIG_FILE')
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
            print("INFO: found rsnapshot is running (pid={0}) !!! now terminating...".format(proc_pid))
            __terminate_process(proc_pid)


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_terminate, sys.argv[1:]))
