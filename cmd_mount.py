#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_mkdir_p import cmd_mkdir_p
from system_cmd import system_cmd

#
# Mount the drive
#


def cmd_mount(device_filename,
              mount_point,
              file_system_type='',
              mount_options=''):

        #/* construct mount commands */
        mount_cmd = ['mount']

        if file_system_type:
            mount_cmd.extend(['-t', file_system_type])

        if mount_options:
            mount_cmd.extend(['-o', mount_options])

        mount_cmd.extend([device_filename, mount_point])


        #/* The first step before mounting */
        if not mount_point:
            raise Exception('{0}: no mounting point'.format(
                device_filename
            ))


        #/* create a mounting point */
        cmd_mkdir_p(mount_point)


        #/* we have to check if mount_point is mount on this system
        # * mountpoint is provided from util-linux package
        # */

        #/* https://serverfault.com/questions/50585/whats-the-best-way-to-check-if-a-volume-is-mounted-in-a-bash-script */
        #/* https://stackoverflow.com/questions/4212522/shell-script-to-know-whether-a-filesystem-is-already-mounted */
        rc, unused, unused, unused = system_cmd(
            cmd=['mountpoint', '-q', mount_point],
            raise_exception=False,
        )

        
        #/* 0: mount_point is mounted; non-zero otherwise */
        if rc != 0:
            system_cmd(
                cmd=mount_cmd,
            )
            
            
                


if __name__ == '__main__':
    print(simple_argparse(cmd_mount, sys.argv[1:]))
