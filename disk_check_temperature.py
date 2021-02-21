#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from disk_check_smart_attributes import disk_check_smart_attributes
from configs.email_settings import NOTIFY_DISK_MAX_TEMP, NOTIFY_DISK_MIN_TEMP


#
# Check for disk temperature
#
def disk_check_temperature(preload_disks=[], negate=False):

    #/* load smart attribute data first... */
    disk_check_smart_attributes(preload_disks)

    #/*---------------------------------------------------------------------*/

    problem_disks = []

    #/* looking through each disks */
    for j, disk in enumerate(preload_disks):

        disk_smart_attributes = disk['smart_attributes']

        #/* smart attribute id for Temperature_Celsius: 194
        # */
        if 194 in disk_smart_attributes.keys():

            disk_temp = float(disk_smart_attributes[194]['raw'])

            #/* test... */
            condition = (
                disk_temp < float(NOTIFY_DISK_MIN_TEMP) or disk_temp > float(NOTIFY_DISK_MAX_TEMP))

            if negate:
                condition = (not condition)

            if condition:
                #/* (j, smart_attributes_ok, disk_temp) */
                problem_disks.append((j, True, disk_temp,))

    return problem_disks


if __name__ == '__main__':
    print(simple_argparse(disk_check_temperature, sys.argv[1:]))
