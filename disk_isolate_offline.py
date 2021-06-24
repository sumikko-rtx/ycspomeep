
import os
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from constants import ISOLATE_DISKS_ENABLE, ISOLATE_DISKS, ISOLATE_MDADM_ARRAYS
from disk_find_by_serial_numbers import disk_find_by_serial_numbers
from cmd_future_umount import cmd_future_umount
from cmd_future_mount import cmd_future_mount







#/* --- turn off the disk --- */
def __disk_offline(device_filename):

    #/* NOTE: the following code is only appliable for Linux!!! */

    #/* on linux, extract sdX (X = a, b, ...) only from device_filename */
    sdX = device_filename.replace("/dev/", "")

    #/* (optional) enter HDD to sleep mode: hdparm -Y /dev/sdX */
    #system_cmd(*['hdparm', '-Y', device_filename],
    #           raise_exception=False,
    #           )

    #/* (optional) flush flush any outstanding I/O: */
    system_cmd(*['blockdev', '--flushbufs', device_filename],
               raise_exception=False,
               )

    #/* echo offline > /sys/block/sdX/device/state */
    target_path = os.path.join(
        os.sep, 'sys', 'block', sdX, 'device', 'state')
    
    system_cmd(*['echo', 'offline'],
               output_file=target_path,
               )
    
    #/* echo 1 > /sys/block/sdX/device/delete */
    target_path = os.path.join(
        os.sep, 'sys', 'block', sdX, 'device', 'delete')
    
    system_cmd(*['echo', '1'],
               output_file=target_path,
               )




#/* --- handle for ISOLATE_DISKS --- */
def __handle_offline_ISOLATE_DISKS():
    
    #print('ISOLATE_DISKS:', ISOLATE_DISKS)
    
    for disk_sn, disk_partitions in dict(ISOLATE_DISKS).items():
    
        target_disks = disk_find_by_serial_numbers(disk_sn)
        if not target_disks:
            continue
        
        
        #/* get device filename */
        target_device_filename = target_disks[0]['device_filename']
        
        #/* list all partitions
        # * filter partitions by target_device_filename
        # */

        target_partitions = cmd_future_mount(list_mount_points=True)

        j = 0
        while j < len(target_partitions):
    
            #/* TODO windows may use like C:\ !!! */
            
            #/* Note: target_device_filename = /dev/sda
            # *       target_partitions[j].device = /dev/sda1
            # */
            if target_partitions[j]['device'].startswith(target_device_filename):
                j = j + 1

            else:
                target_partitions.pop(j)


        #/* unmount all target_partitions */
        
        #print('target_partitions:', target_partitions)
        
        for x in target_partitions:
            cmd_future_umount(x['mount_point'], remove_mount_points=True)


        #/* TODO turn off the disks */
        __disk_offline(device_filename=target_device_filename)







#
# Raid example:
#
# ISOLATE_MDADM_ARRAYS = {
#
#     '/dev/md0': { # << device filename for MDADM array(/dev/md(n))
#
#         'disk_serial_numbers': [   # << a list of drive serial numbers to re-assemble an array
#             '9HSSNTK8', 'L34MS67U'
#         ],
#
#         # --- start of disk partitions list ---
#
#         'mount_point': '',         # << the mouting point
#         'file_system_type': '',    # << file system type, matches mount(8)'s -t option
#         'mount_options': '',       # << mount option, matches mount(8)'s -o option
#
#         # --- end of disk partitions list ---
#     },
# }
#

#/* --- handle for ISOLATE_MDADM_ARRAYS --- */
def __handle_offline_ISOLATE_MDADM_ARRAYS():
    
    #print('ISOLATE_MDADM_ARRAYS:', ISOLATE_MDADM_ARRAYS)

    for md_device_filename, md_opts in dict(ISOLATE_MDADM_ARRAYS).items():

        disk_serial_numbers = md_opts.get('disk_serial_numbers', [])
        mount_point = md_opts.get('mount_point', '')
        #file_system_type = md_opts.get('file_system_type', '')
        #mount_options = md_opts.get('mount_options', '')

        #/* find disks need to be offline */
        target_disks = [x['device_filename'] for x in disk_find_by_serial_numbers(disk_serial_numbers)]

        #/* umount mdadm array first!!! */
        cmd_future_umount(mount_point, remove_mount_points=True)

        #/* stop mdadm array */
        #/* TODO is this sufficient to safely unmount mdadm array??? */
        mdadm_stop_cmd = ['mdadm', '--stop', md_device_filename]
        system_cmd(*mdadm_stop_cmd, raise_exception=False)

        #/* turn off the disks */
        for x in target_disks:
            __disk_offline(device_filename=x)
















#/* --- the main program --- */
def disk_isolate_offline():

    #/* skip if ISOLATE_DISKS_ENABLE set to false */
    if not ISOLATE_DISKS_ENABLE:
        return

    #/* handle different types of disk offline */
    __handle_offline_ISOLATE_DISKS()
    __handle_offline_ISOLATE_MDADM_ARRAYS()
    
    #/* your drive(s) is now turned off.
    # * At that point the OS does not see this drive!!!
    # */




if __name__ == "__main__":
    print(simple_argparse(disk_isolate_offline, sys.argv[1:]))
