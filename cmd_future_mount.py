#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_mkdir import cmd_mkdir
from system_cmd import system_cmd
import re



def cmd_future_mount(list_mount_points=False,
              device_filename='',
              mount_point='',
              file_system_type='',
              mount_options=''):

    #/* list mounting points */
    if list_mount_points:

        #/* output format:
        # * 
        # * <device> on <mount_point> type <fstype> (<mount_options>)
        # *
        # * output example:
        # *
        # * /var/lib/snapd/snaps/gnome-3-34-1804_72.snap on /snap/gnome-3-34-1804/72 type squashfs (ro,nodev,relatime,x-gdu.hide)
        # */
    
        rc, output, unused, unused = system_cmd(
            *['mount'],
        )

        output_lines = output.splitlines()
        
        mount_points = []
        
        for line in output_lines:

            g = re.search(r'([^\s]+)\s+on\s+([^\s]+)\s+type\s+([^\s]+)\s+([(][^()]+[)])', line)
            
            if not g:
                continue

            mount_points.append({
                'device': g.group(1),
                'mount_point': g.group(2),
                'fstype': g.group(3),
                'mount_options': g.group(4),
            })

        return mount_points

    #/*---------------------------------------------------------------------*/
    
    #/* mount a drive */        
    else:

        if not device_filename:
            raise Exception('no device_filename given')
            
        if not mount_point:
            raise Exception('no mount_point given')    


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
        cmd_mkdir(mount_point, parents=True)


        #/* we have to check if mount_point is mount on this system
        # * mountpoint is provided from util-linux package
        # */

        #/* https://serverfault.com/questions/50585/whats-the-best-way-to-check-if-a-volume-is-mounted-in-a-bash-script */
        #/* https://stackoverflow.com/questions/4212522/shell-script-to-know-whether-a-filesystem-is-already-mounted */
        rc, unused, unused, unused = system_cmd(
            *['mountpoint', '-q', mount_point],
            raise_exception=False,
        )

        
        #/* 0: mount_point is mounted; non-zero otherwise */
        if rc != 0:
            system_cmd(
                *mount_cmd,
            )
            
            
                


if __name__ == '__main__':
    print(simple_argparse(cmd_future_mount, sys.argv[1:]))
