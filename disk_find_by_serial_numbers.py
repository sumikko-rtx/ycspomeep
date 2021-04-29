
import os
import sys
from simple_argparse import simple_argparse
from smart_scan_open import smart_scan_open


#/* find attached disks by serial_numbers */
def disk_find_by_serial_numbers(serial_numbers):

    found_disks = []

    #/* list attacted disk info */
    attached_disks = smart_scan_open()

    for x in attached_disks:
        if x['serial_number'] in serial_numbers:
            found_disks.append(x)

    return found_disks


if __name__ == "__main__":
    print(simple_argparse(disk_find_by_serial_numbers, sys.argv[1:]))
