#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from smart_scan_open import smart_scan_open
from smart_attributes import smart_attributes


def disk_check_smart_attributes(preload_disks=[], negate=False):

    #/* if disk info not get, run smart_scan_open first  */
    if not preload_disks:
        
        #/* Note: smart_scan_open may raise SystemCmdException */
        try:
            tmp = smart_scan_open()
            preload_disks.extend(tmp)
            
        except Exception:
            pass

    #/*---------------------------------------------------------------------*/

    problem_disks = []

    #/* looking through each disks */
    for j, disk in enumerate(preload_disks):

        disk_device_filename = disk['device_filename']
        disk_device_type = disk['device_type']

        #/* Note: smart_attributes may raise SystemCmdException */
        try:

            #/* get disk smart status (this runs run smartctl) */
            disk_smart_attributes = smart_attributes(
                device_filename=disk_device_filename,
                device_type=disk_device_type,
            )

            #/* save smart attribute for later use */
            disk['smart_attributes'] = disk_smart_attributes

            #/* smart attribute id for Reallocated_Sector_Count: 5
            # * smart attribute id for Reallocation_Event_Count: 196
            # * smart attribute id for Current_Pending_Sector_Count: 197
            # * smart attribute id for Uncorrectable_Sector_Count: 198
            # */
            for attr_id, attr_data in disk_smart_attributes.items():

                attr_name = attr_data['attribute_name']
                attr_value = int(attr_data['value'])
                attr_thresh = int(attr_data['thresh'])
                attr_worst = int(attr_data['worst'])
                attr_raw = int(attr_data['raw'])

                #/* normal < threshold: hdd/ssd have problems */
                #/* test */
                condition = (attr_value < attr_thresh)

                if negate:
                    condition = (not condition)

                if condition:
                    #/* (j, smart_attributes_ok, attr_id, attr_name, attr_value, attr_thresh, attr_worst, attr_raw) */
                    problem_disks.append(
                        (j,  True, attr_id, attr_name, attr_value, attr_thresh, attr_worst, attr_raw,))

        #/* in case of smart_attributes get an error... */
        except Exception:
            problem_disks.append((j, False,))

    return problem_disks


if __name__ == '__main__':
    print(simple_argparse(disk_check_smart_attributes, sys.argv[1:]))
