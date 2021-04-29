
import os
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from file_list import file_list
from constants import ISOLATE_DISKS_ENABLE, ISOLATE_DISKS
from disk_find_by_serial_numbers import disk_find_by_serial_numbers
from cmd_mount import cmd_mount






#/* linux code to online the disks */
def __linux_disk_online():

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

        system_cmd(cmd=['echo', '- - -'],
                   output_file=target_path,
                   )





def disk_isolate_online():

    #/* skip if ISOLATE_DISKS_ENABLE set to false */
    if not ISOLATE_DISKS_ENABLE:
        return

    #/************************************************************************/

    #/* scan and turn on the disks */
    __linux_disk_online()

    #/************************************************************************/

    #/* --- handle for ISOLATE_DISKS --- */
    
    for disk_sn, disk_partitions in dict(ISOLATE_DISKS).items():
    
        target_disks = disk_find_by_serial_numbers(disk_sn)
        if not target_disks:
            continue

        #/* get device filename */
        target_device_filename = target_disks[0]['device_filename']

        #/* mount partitions */
        for y, x in disk_partitions.items():

            #/* NOTE: must include /dev/sdX(Y), where Y = 1,2,3,.... */
            cmd_mount(
                device_filename='{0}{1}'.format(target_device_filename, y),
                file_system_type=x.get('file_system_type'),
                mount_point=x.get('mount_point'),
                mount_options=x.get('mount_options'),
            )






if __name__ == "__main__":
    print(simple_argparse(disk_isolate_online, sys.argv[1:]))
