
import os
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from file_list import file_list
from constants import ISOLATE_DISKS_ENABLE, ISOLATE_DISKS, ISOLATE_MDADM_ARRAYS
from disk_find_by_serial_numbers import disk_find_by_serial_numbers
from cmd_future_mount import cmd_future_mount





#/* --- turn on the disk --- */
def __disk_online():

    #/* NOTE: the following code is only appliable for Linux!!! */
    
    #
    # for scsi ports on system motherboard:
    #     echo "- - -" > /sys/class/scsi_host/hostX/scan'
    #

    local_scsi_ports = file_list(
        '/sys/class/scsi_host',
        list_symlinks=True,
    )

    for x in local_scsi_ports:

        target_path = os.path.join(x, 'scan')

        system_cmd(*['echo', '- - -'],
                   output_file=target_path,
                   )





#/* --- handle for ISOLATE_DISKS --- */
def __handle_online_ISOLATE_DISKS():

    for disk_sn, disk_partitions in dict(ISOLATE_DISKS).items():
    
        target_disks = disk_find_by_serial_numbers(disk_sn)
        if not target_disks:
            continue

        #/* get device filename */
        target_device_filename = target_disks[0]['device_filename']

        #/* mount partitions */
        for y, x in disk_partitions.items():

            #/* NOTE: must include /dev/sdX(Y), where Y = 1,2,3,.... */
            cmd_future_mount(
                device_filename='{0}{1}'.format(target_device_filename, y),
                file_system_type=x.get('file_system_type'),
                mount_point=x.get('mount_point'),
                mount_options=x.get('mount_options'),
            )








#/* --- handle for ISOLATE_MDADM_ARRAYS --- */
def __handle_online_ISOLATE_MDADM_ARRAYS():

    for md_device_filename, md_opts in dict(ISOLATE_MDADM_ARRAYS).items():

        disk_serial_numbers = md_opts.get('disk_serial_numbers', [])
        mount_point = md_opts.get('mount_point', '')
        file_system_type = md_opts.get('file_system_type', '')
        mount_options = md_opts.get('mount_options', '')

        #/* find disks need to be offline */
        target_disks = [x['device_filename']
                        for x in disk_find_by_serial_numbers(disk_serial_numbers)]

        #/* assemble mdadm array
        # * mdadm --assemble <md_device_filename> <disk1> <disk2> ...
        # */
        cmd = ['mdadm', '--assemble', md_device_filename]
        cmd.extend(target_disks)
        #print(cmd)
        system_cmd(*cmd, raise_exception=False)

        #/* use mdadm --detail <md_device_filename> to check the mdadm settings
        # *
        # * exit statuses
        # *
        # * 0 The array is functioning normally.
        # * 1 The array has at least one failed device.
        # * 2 The array has multiple failed devices such that it is unusable.
        # * 4 There was an error while trying to get information about the device
        # */
        cmd = ['mdadm', '--detail', md_device_filename]
        rc, unused, unused, unused = system_cmd(*cmd, raise_exception=True)

        if rc >= 2:
            raise Exception(
                'mdadm --detail returned exit status: {0}'.format(rc))

        #/* mount md_device_filename */
        cmd_future_mount(
            device_filename=md_device_filename,
            file_system_type=file_system_type,
            mount_point=mount_point,
            mount_options=mount_options,
        )






def disk_isolate_online():

    #/* skip if ISOLATE_DISKS_ENABLE set to false */
    if not ISOLATE_DISKS_ENABLE:
        return

    #/************************************************************************/

    #/* scan and turn on the disks */
    __disk_online()

    #/************************************************************************/

    #/* handle different types of disk offline */
    __handle_online_ISOLATE_DISKS()
    __handle_online_ISOLATE_MDADM_ARRAYS()

    #/************************************************************************/
    
    #/* turn off the disks */
    


if __name__ == "__main__":
    print(simple_argparse(disk_isolate_online, sys.argv[1:]))
