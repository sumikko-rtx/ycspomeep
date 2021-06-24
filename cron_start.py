#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from check_if_root import check_if_root
from system_cmd import system_cmd
from cmd_future_uname_a import cmd_future_uname_a




#
# Wrapper python script for starting a cron scheduler daemon
#
# https://www.cyberciti.biz/faq/howto-linux-unix-start-restart-cron/
#
def cron_start():
    
    #/* starting cron requires root */
    check_if_root()
    
    #/*---------------------------------------------------------------------*/
    
    #/* the output of uname -a */
    distribution_name = cmd_future_uname_a().lower()
    #print('distribution_name:',distribution_name)

    #/* this will use to list possible cmd for starting cron */
    start_cron_cmds = []

    #/* ... as well as enabling cron on boot */
    enable_cron_cmds = []

    #/*---------------------------------------------------------------------*/
    
    #/* --- start cron --- */

    #/* (for Debian, Ubuntu)
    # *
    # * (start)             systemctl start cron.service
    # *                  || service cron start
    # *                  || /etc/init.d/cron start
    # *
    # * (enable_on_boot)    systemctl enable cron.service
    # *                  || update-rc.d cron defaults
    # */

    if 'ubuntu' in distribution_name \
            or 'debian' in distribution_name:

        start_cron_cmds.extend([
            'systemctl', 'start', 'cron.service', '||',
            'service', 'cron', 'start', '||',
            '/etc/init.d/cron', 'start',
        ])

        enable_cron_cmds = [
            'systemctl', 'enable', 'cron.service', '||',
            'update-rc.d', 'cron', 'defaults'
        ]


    #/* (for RHEL, CentOs, Fedora)
    # *
    # * (start)             systemctl start crond.service
    # *                  || service crond start
    # *                  || /etc/inid.d crond start
    # *
    # * (enable_on_boot)    systemctl enable crond.service
    # *                  || chkconfig crond on
    # */
    elif 'rhel' in distribution_name \
            or 'centos' in distribution_name \
            or 'fedora' in distribution_name:

        start_cron_cmds.extend([
            'systemctl', 'start', 'crond.service', '||',
            'service', 'crond', 'start', '||',
            '/etc/init.d/crond', 'start',
        ])

        enable_cron_cmds = [
            'systemctl', 'enable', 'crond.service', '||',
            'chkconfig', 'crond', 'on'
        ]


    #/* on cygwin:
    # *
    # * (start)             cygrunsrv -I cron -p /usr/sbin/cron -a -n
    # *                  && net start cron
    # *
    # * (enable_on_boot)    sc config cron start= auto
    # *
    # * both cygrunsrv and cron must be fully installed.
    # */ 
    elif 'cygwin' in distribution_name:

        cron_exec = os.path.join(os.sep, 'usr', 'sbin', 'cron')

        start_cron_cmds.extend([
            'cygrunsrv', '-I', 'cron', '-p', cron_exec, '-a', '-n', '&&',
            'net', 'start', 'cron',
        ])

        enable_cron_cmds = [
            'sc', 'config', 'cron', 'start=', 'auto',
        ]

    #/*---------------------------------------------------------------------*/

    #/* start cron goes here !!! */
    #print('start_cron_cmds:', start_cron_cmds)
    #print('enable_cron_cmds', enable_cron_cmds)
    system_cmd(*start_cron_cmds)
    system_cmd(*enable_cron_cmds)









if __name__ == '__main__':
    print(simple_argparse(cron_start, sys.argv[1:]))
