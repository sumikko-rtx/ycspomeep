#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from check_if_root import check_if_root
from system_cmd import system_cmd
from cmd_future_uname_a import cmd_future_uname_a



#
# Wrapper python script for stopping a cron scheduler daemon
#
# https://www.cyberciti.biz/faq/howto-linux-unix-stop-restop-cron/
#
def cron_stop():
    
    #/* stoping cron requires root */
    check_if_root()
    
    #/*---------------------------------------------------------------------*/
    
    #/* the output of uname -a */
    distribution_name = cmd_future_uname_a().lower()
    #print('distribution_name:',distribution_name)

    #/* this will use to list possible cmd for stoping cron */
    stop_cron_cmds = []
    
    #/* ... as well as enabling cron on boot */
    disable_cron_cmds = []

    #/*---------------------------------------------------------------------*/
    
    #/* --- stop cron --- */

    #/* (for Debian, Ubuntu)
    # *
    # * (stop)               systemctl stop cron.service
    # *                   || service cron stop
    # *                   || /etc/init.d/cron stop
    # *
    # * (disable_on_boot)    systemctl disable cron.service
    # *                   || update-rc.d cron disable
    # */

    if 'ubuntu' in distribution_name \
            or 'debian' in distribution_name:

        stop_cron_cmds.extend([
            'systemctl', 'stop', 'cron.service', '||',
            'service', 'cron', 'stop', '||',
            '/etc/init.d/cron', 'stop',
        ])

        disable_cron_cmds = [
            'systemctl', 'disable', 'cron.service', '||',
            'update-rc.d', 'cron', 'disable'
        ]


    #/* (for RHEL, CentOs, Fedora)
    # *
    # * (stop)              systemctl stop crond.service
    # *                   || service crond stop
    # *                   || /etc/inid.d crond stop
    # *
    # * (disable_on_boot)    systemctl disable cron.service
    # *                   || chkconfig crond off
    # */
    elif 'rhel' in distribution_name \
            or 'centos' in distribution_name \
            or 'fedora' in distribution_name:

        stop_cron_cmds.extend([
            'systemctl', 'stop', 'crond.service', '||',
            'service', 'crond', 'stop', '||',
            '/etc/init.d/crond', 'stop',
        ])

        disable_cron_cmds = [
            'systemctl', 'disable', 'crond.service', '||',
            'chkconfig', 'crond', 'off'
        ]


    #/* on cygwin:
    # *
    # * (stop)               cygrunsrv -I cron -p /usr/sbin/cron -a -n
    # *                   && net stop cron
    # *
    # * (disable_on_boot)    sc config cron start= disabled
    # *
    # * both cygrunsrv and cron must be fully installed.
    # */
    elif 'cygwin' in distribution_name:

        cron_exec = os.path.join(os.sep, 'usr', 'sbin', 'cron')

        stop_cron_cmds.extend([
            'net', 'stop', 'cron', '&&',
            'cygrunsrv', '-E', 'cron', '&&',
            'cygrunsrv', '-R', 'cron'
        ])

        disable_cron_cmds = [
            'sc', 'config', 'cron', 'start=', 'disabled',
        ]

    #/*---------------------------------------------------------------------*/

    #/* stop cron goes here !!! */
    #/* note: disable first, then stop!!! */
    #print('stop_cron_cmds:', stop_cron_cmds)
    #print('disable_cron_cmds', disable_cron_cmds)
    system_cmd(*disable_cron_cmds)
    system_cmd(*stop_cron_cmds)










if __name__ == '__main__':
    print(simple_argparse(cron_stop, sys.argv[1:]))
