#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from check_if_root import check_if_root
from cmd_future_uname_a import cmd_future_uname_a
from cmd_future_reboot import cmd_future_reboot
import os
from rsnapshot_check_running_progress import rsnapshot_check_running_progress
import time







def update_from_pkgmgr(check_upgradable=False, reboot=False):
    
    #/* must be root */
    check_if_root()

    #/* get distribution name */
    distribution_name = cmd_future_uname_a().lower()
    
    #/* this will form a package update cmdline */
    cmd = []
    
    #/* True to neet reboot: */
    need_reboot = False

    #/* return code from pkgmgr */
    pkgmgr_rc = 0

    #/*---------------------------------------------------------------------*/
    
    #/* update software database */
    if True:
        
        cmd.clear()
    
        if False:
            pass
    
        #elif 'suse' in distribution_name:
        #    cmd.extend(['zypper', 'ref'])
    
        elif 'debian' in distribution_name \
                or 'ubuntu' in distribution_name:
            cmd.extend(['apt', 'update'])
    
        elif 'rhel' in distribution_name \
                or 'centos' in distribution_name \
                or 'fedora' in distribution_name:
            cmd.extend(['dnf', 'check-update', '||', 'yum', 'check-update'])
    
        elif 'cygwin' in distribution_name:
            pass
        
        print('INFO: trying {0}'.format(cmd))
        system_cmd(*cmd, raise_exception=False)
        print('INFO: software database updated')





    #/*---------------------------------------------------------------------*/
    
    #/* show updatable packages (check_upgradable=True) */
    if check_upgradable:

        cmd.clear()
        
        if False:
            pass
    
        #elif 'suse' in distribution_name:
        #    cmd.extend(['zypper', 'lu'])

        elif 'debian' in distribution_name \
                or 'ubuntu' in distribution_name:
            cmd.extend(['apt', 'list', 'upgradable'])
    
        elif 'rhel' in distribution_name \
                or 'centos' in distribution_name \
                or 'fedora' in distribution_name:
            cmd.extend(['dnf', 'check-update', '||', 'yum', 'check-update'])
    
        elif 'cygwin' in distribution_name:
            pass

        print('INFO: trying {0}'.format(cmd))
        unused, output, unused, unused = system_cmd(*cmd, raise_exception=False)
        print(output)

        #/* exit... */
        return

    #/*---------------------------------------------------------------------*/

    #/* install all upgrades (check_upgradable=False, check_reboot=False) */
    if True:

        #/* important:!!!  all backup must be complete before updating system... */
        print('INFO: wait until all backup job(s) is/are completed...')
        
        while True:
            
            have_rsnapshot_running, unused, unused, unused, unused, unused, unused, unused = rsnapshot_check_running_progress()
            
            if not have_rsnapshot_running:
                break

            #/* to reduce cpu time... */
            time.sleep(1)




        #/* system update goes here... */
        cmd.clear()
        
        if False:
            pass
        
        #elif 'suse' in distribution_name:
        #    cmd.extend(['zypper', '-n', 'up'])

        elif 'debian' in distribution_name \
                or 'ubuntu' in distribution_name:
            cmd.extend(['apt', '-y', 'upgrade'])

        elif 'rhel' in distribution_name \
                or 'centos' in distribution_name \
                or 'fedora' in distribution_name:
            cmd.extend(['dnf', '-y', 'update', '||', 'yum',  '-y', 'update'])
    
        elif 'cygwin' in distribution_name:
            
            #/* cygwin (64-bit) */
            cmd.extend(['/setup-x86_64', '--no-desktop', '--no-shortcuts', '--no-startmenu', '--quiet-mode'])
            
            #/* cygwin (32-bit) */
            cmd.extend(['||', '/setup-x86', '--no-desktop',
                        '--no-shortcuts', '--no-startmenu', '--quiet-mode'])

        print('INFO: trying {0}'.format(cmd))
        
        pkgmgr_rc, output, unused, unused = system_cmd(
            *cmd, raise_exception=False)
        
        if pkgmgr_rc == 0:
            print('INFO: package(s) are successfully updated!!!')


    #/*---------------------------------------------------------------------*/
    
    #/* check if reboot required after update */
    #/* https://megamorf.gitlab.io/2019/06/10/check-if-reboot-is-required-after-installing-linux-updates/ */
    
    if True:
        
        if False:
            pass
    
        #elif 'suse' in distribution_name:
        #    # /etc/zypp/needreboot
        #    pass

        elif 'debian' in distribution_name \
                or 'ubuntu' in distribution_name:

            #/* The system needs a reboot if the file /var/run/reboot-required
            # * exists and can be checked as follows:
            # */
            target_file = os.path.join(
                os.sep, 'var', 'run', 'reboot-required'
            )

            if os.path.isfile(target_file):
                need_reboot = True
    
        elif 'rhel' in distribution_name \
                or 'centos' in distribution_name \
                or 'fedora' in distribution_name:

            #/* need-restarting is provided from dnf-utils or yum-utils package */
            rc, unused, unused, unused = system_cmd(
                *['needs-restarting', '-r'], raise_exception=False)

            #/* needs-restarting -r returns 0 if reboot is not needed, and 1 if it is. */
            if rc == 0:
                need_reboot = False

            elif rc == 1:
                need_reboot = True

    
        elif 'cygwin' in distribution_name:
            #/* TODO currently there is no check reboot script or program for cygwin */
            pass

        
        
        
        if need_reboot:
            print('INFO: your system needs to be restarted to finish installing updates!!!')
        else:
            print('INFO: your system no needs to be restarted!!!')
            
    #/*---------------------------------------------------------------------*/

    #/* reboot if restart required */
    if pkgmgr_rc == 0 and reboot and need_reboot:
        cmd_future_reboot()

    
    
    


if __name__ == '__main__':
    print(simple_argparse(update_from_pkgmgr, sys.argv[1:]))

