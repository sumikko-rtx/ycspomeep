#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from disk_check_smart_attributes import disk_check_smart_attributes
from constants import NOTIFY_DISK_MAX_POWER_ON_HOURS


#
# Check for disk power on hours
#
def disk_check_power_on_hours(preload_disks=[], negate=False):

    #/* load smart attribute data first... */
    disk_check_smart_attributes(preload_disks)

    #/*---------------------------------------------------------------------*/

    problem_disks = []

    #/* looking through each disks */
    for j, disk in enumerate(preload_disks):

        disk_smart_attributes = disk['smart_attributes']

        #/* smart attribute id for Power_On_Hours: 9
        # */
        if 9 in disk_smart_attributes.keys():

            disk_power_on_hours = float(disk_smart_attributes[9]['raw'])

            if float(NOTIFY_DISK_MAX_POWER_ON_HOURS) <= 0:
                continue

            #/* test... */
            condition = (disk_power_on_hours >= float(
                NOTIFY_DISK_MAX_POWER_ON_HOURS))

            if negate:
                condition = (not condition)

            if condition:
                #/* (smart_attributes_ok, disk_power_on_hours) */
                problem_disks.append((j, True, disk_power_on_hours,))

    return problem_disks


if __name__ == '__main__':
    print(simple_argparse(disk_check_power_on_hours, sys.argv[1:]))
