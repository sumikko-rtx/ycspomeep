#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from cmd_rm_r import cmd_rm_r
import time
import os





#
# Unmount the given mount_points
#
def cmd_future_umount(*mount_points, remove_mount_points=False):

    #print('mount_points: ',mount_points)

    for x in mount_points:

        #/* use mountpoint to determine mount_point is mounted */
        if not os.path.ismount(x):
            raise Exception('{0}: not a mounting point'.format(x))


        #/* Wait until backup disk is not busy */
        #/* https://askubuntu.com/questions/1083624/how-to-make-umount-wait-until-a-device-is-not-busy */
        while True:

            #/* NOTE: that there is no "n" between the “u” and the "m"!!!
            # *       the command is "umount" and not "unmount."!!!
            # */

            umount_cmd = ['umount', x]

            #/* in case rc != 0, drive is still busy!!! */
            rc, usused, unused, unused = system_cmd(
                *umount_cmd,
                raise_exception=False,
            )

            if rc == 0:
                break

            #/* delay 10 seconds, to reduce CPU Time... */
            time.sleep(10)


        #/* backup disk is now unmounted. */
        #/* if remove_mount_points = True, remove mounting point after unmount drives */
        if remove_mount_points:
            cmd_rm_r(x, force=True)


if __name__ == '__main__':
    print(simple_argparse(cmd_future_umount, sys.argv[1:]))
