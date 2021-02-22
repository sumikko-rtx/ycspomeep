#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from disk_check_smart_attributes import disk_check_smart_attributes
from configs.email_settings import NOTIFY_DISK_MAX_BAD_SECTORS


#
# Check for disk any (possible) bad sectors
# Note: run disk_self_test before calling disk_check_temperature
#       since the are some offline smart attribute need to be update_from_git
#
def disk_check_bad_sectors(preload_disks=[], negate=False):

    #/* load smart attribute data first... */
    disk_check_smart_attributes(preload_disks)

    #/*---------------------------------------------------------------------*/

    problem_disks = []

    #/* looking through each disks */
    for j, disk in enumerate(preload_disks):

        possible_bad_sectors = 0

        disk_smart_attributes = disk['smart_attributes']

        if NOTIFY_DISK_MAX_BAD_SECTORS <= 0:
            continue

        #/* count up any possible bad sectors */
        for x in [5, 196, 197, 198]:
            if x in disk_smart_attributes.keys():
                possible_bad_sectors = possible_bad_sectors + \
                    int(disk_smart_attributes[x]['raw'])

        #/* test... */
        condition = (NOTIFY_DISK_MAX_BAD_SECTORS > 0 and
                     possible_bad_sectors >= NOTIFY_DISK_MAX_BAD_SECTORS)

        if negate:
            condition = (not condition)

        if condition:
            #/* (j, smart_attributes_ok, possible_bad_sectors) */
            problem_disks.append((j, True, possible_bad_sectors,))

    return problem_disks


if __name__ == '__main__':
    print(simple_argparse(disk_check_bad_sectors, sys.argv[1:]))
