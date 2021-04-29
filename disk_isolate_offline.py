
import os
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from constants import ISOLATE_DISKS_ENABLE, ISOLATE_DISKS
from disk_find_by_serial_numbers import disk_find_by_serial_numbers
import psutil
from cmd_umount import cmd_umount






#/* linux code to offline the disks */
def __linux_disk_offline(device_filename):

    #/* on linux, extract sdX (X = a, b, ...) only from device_filename */
    sdX = device_filename.replace("/dev/", "")

    #/* (optional) enter HDD to sleep mode: hdparm -Y /dev/sdX */
    #system_cmd(cmd=['hdparm', '-Y', device_filename],
    #           raise_exception=False,
    #           )

    #/* (optional) flush flush any outstanding I/O: */
    system_cmd(cmd=['blockdev', '--flushbufs', device_filename],
               raise_exception=False,
               )

    #/* echo offline > /sys/block/sdX/device/state */
    target_path = os.path.join(
        os.sep, 'sys', 'block', sdX, 'device', 'state')
    
    system_cmd(cmd=['echo', 'offline'],
               output_file=target_path,
               )
    
    #/* echo 1 > /sys/block/sdX/device/delete */
    target_path = os.path.join(
        os.sep, 'sys', 'block', sdX, 'device', 'delete')
    
    system_cmd(cmd=['echo', '1'],
               output_file=target_path,
               )






def disk_isolate_offline():

    #/* skip if ISOLATE_DISKS_ENABLE set to false */
    if not ISOLATE_DISKS_ENABLE:
        return

    #/************************************************************************/

    #/* --- handle for ISOLATE_DISKS --- */
    
    #print('ISOLATE_DISKS:', ISOLATE_DISKS)
    
    for disk_sn, disk_partitions in dict(ISOLATE_DISKS).items():
    
        target_disks = disk_find_by_serial_numbers(disk_sn)
        if not target_disks:
            continue
        
        
        #/* get device filename */
        target_device_filename = target_disks[0]['device_filename']
        
        #/* TODO found wrong here: forced umount due to target_device_filename=[]!!! */
        #/* list all partitions
        # * filter partitions by target_device_filename
        # */
        target_partitions = list(psutil.disk_partitions())
        
        j = 0
        while j < len(target_partitions):
    
            #/* TODO windows may use like C:\ !!! */
            
            #/* Note: target_device_filename = /dev/sda
            # *       target_partitions[j].device = /dev/sda1
            # */
            if target_partitions[j].device.startswith(target_device_filename):
                j = j + 1

            else:
                target_partitions.pop(j)


        #/* unmount all target_partitions */
        
        #print('target_partitions:', target_partitions)
        
        for x in target_partitions:
            cmd_umount(x.mountpoint, remove_mount_points=True)


        #/* TODO turn off the disks */
        __linux_disk_offline(device_filename=target_device_filename)

    #/************************************************************************/
    
    
    #/* your drive(s) is now turned off.
    # * At that point the OS does not see this drive!!!
    # */



if __name__ == "__main__":
    print(simple_argparse(disk_isolate_offline, sys.argv[1:]))
