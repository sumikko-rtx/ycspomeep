#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import re

from system_cmd import system_cmd
from cmd_future_mount import cmd_future_mount
from str_2_bool import str_2_bool



#
# run smartctl --scan-open
#
# to list disk(s) attached on this server.
#
def smart_scan_open(include_system_disks=False):

    #/* this will placed the result status (dict type ) */
    results = []

    #/************************************************************************/

    #/* use smartctl --scan-open to scan disks
    # * this return a list of corresponding disk options pass to smartctl
    # */

    cmd = ['smartctl', '--scan-open',]

    unused, cmd_A_output, unused, unused = system_cmd(*cmd)

    include_system_disks = str_2_bool(include_system_disks)
    cmd_A_output = cmd_A_output.strip()
    cmd_A_output_lines = cmd_A_output.splitlines()

    #/************************************************************************/

    #/* sample output:
    # *
    # * /dev/sda -d sat # /dev/sda [SAT], ATA device
    # * /dev/sdb -d sat # /dev/sdb [SAT], ATA device
    # */

    #/* parse the output lines */
    for line_A in cmd_A_output_lines:

        #/* the row data will be store */
        tmprow = {}

        #/* text after # is comment. remove it */
        line_A = re.sub(r'#.*$', '', line_A)

        #/* remove leading and trailing whitespace if any */
        #/* replace repeated whitespace by single space */
        line_A = line_A.strip()
        line_A = re.sub(r'\s+', ' ', line_A)

        #/* split line by whitespaces */
        smartctl_options = [x.strip() for x in line_A.split()]

        #/* prevent smartctl_options INdexError */
        if not smartctl_options:
            continue

        #/* store device_filename and device_type */
        device_filename = smartctl_options[0]
        tmprow['device_filename'] = device_filename
        device_type = smartctl_options[2]
        tmprow['device_type'] = device_type

        #/* next, run smartctl --info <smartctl_options> */
        cmd = ['smartctl', '--info', *smartctl_options,]
        unused, cmd_B_output, unused, unused = system_cmd(*cmd)

        cmd_B_output = cmd_B_output.strip()
        cmd_B_output_lines = cmd_B_output.splitlines()

        #
        # sample output #1
        # ================
        #
        # Model Family:     Hitachi/HGST Travelstar Z5K500
        # Device Model:     HGST HTS545050A7E680
        # Serial Number:    RBF5WADC0LJ4VR
        # LU WWN Device Id: 5 000cca 8acc86b54
        # Firmware Version: GR2OA230
        # User Capacity:    500,107,862,016 bytes [500 GB]
        # Sector Sizes:     512 bytes logical, 4096 bytes physical
        # Rotation Rate:    5400 rpm
        # Form Factor:      2.5 inches
        # Device is:        In smartctl database [for details use: -P show]
        # ATA Version is:   ATA8-ACS T13/1699-D revision 6
        # SATA Version is:  SATA 2.6, 6.0 Gb/s (current: 6.0 Gb/s)
        # Local Time is:    Mon Sep 16 04:38:01 2019 EDT
        # SMART support is: Available - device has SMART capability.
        # SMART support is: Enabled
        #

        #
        # sample output #2
        # ================
        #
        # Model Family:     Western Digital Scorpio Blue Serial ATA
        # Device Model:     WDC WD1600BEVT-22ZCT0
        # Serial Number:    WD-WXE908UY4397
        # LU WWN Device Id: 5 0014ee 05646dc6b
        # Firmware Version: 11.01A11
        # User Capacity:    160,041,885,696 bytes [160 GB]
        # Sector Size:      512 bytes logical/physical
        # Rotation Rate:    5400 rpm
        # Device is:        In smartctl database [for details use: -P show]
        # ATA Version is:   ATA8-ACS (minor revision not indicated)
        # SATA Version is:  SATA 2.5, 3.0 Gb/s
        # Local Time is:    Fri Sep 27 14:14:14 2019 CST
        # SMART support is: Available - device has SMART capability.
        # SMART support is: Enabled
        #
        for line_B in cmd_B_output_lines:

            #/* split colon(:) once */
            tmp = line_B.split(':', 1)

            #/* to avoid index error... */
            if len(tmp) < 2:
                continue

            k = tmp[0].strip()
            v = tmp[1].strip()

            #/* ??? */
            k = re.sub(r'[^A-Za-z0-9]', '_', k)
            k = k.lower()

            #/* except device_type. why??? */
            if k in ['device_type']:
                pass
            else:
                tmprow[k] = v


        #/* For key sector_size, possible output
        # *
        # * (1)
        # * Sector Sizes:     512 bytes logical, 4096 bytes physical
        # *                   ^^^                ^^^^
        # * (2)
        # * Sector Sizes:     512 bytes logical/physical
        # *                   ^^^                ^^^^
        # */
        sector_sizes = tmprow.get(
            'sector_sizes',  tmprow.get('sector_sizes', ''))
        
        sector_sizes = sector_sizes.lower()
        
        g1 = re.search(
            r'([0-9]+)\s+bytes\s+logical,\s+([0-9]+)\s+bytes\s+physical$', sector_sizes)
        g2 = re.search(
            r'([0-9]+)\s+bytes\s+logical/physical', sector_sizes)
        
        if g1:
            tmprow['physical_sector_size'] = int(g1.group(1))
            tmprow['logical_sector_size'] = int(g1.group(2))

        #/* Parse the line like:
        # * Sector Sizes:     512 bytes logical/physical
        # *                   ^^^                ^^^^
        # */
        elif g2:
            tmprow['physical_sector_size'] = int(g2.group(1))
            tmprow['logical_sector_size'] = int(g2.group(1))

        #/* otherwise, set both zeros */
        else:
            tmprow['physical_sector_size'] = 0
            tmprow['logical_sector_size'] = 0

        #/* for user capacity, extract bytes only */
        user_capacity = tmprow['user_capacity']
        user_capacity = user_capacity.lower()
        user_capacity = re.sub(',', '', user_capacity)
        user_capacity = re.sub('\s*bytes.*$', '', user_capacity)
        tmprow['user_capacity'] = int(user_capacity)



        #/* additional check: check if using system disk */
        is_system_disk = False
        mount_points = cmd_future_mount(list_mount_points=True)

        for x in mount_points:
            
            #/* TODO unix only, how about windows */
            if x['device'].startswith(device_filename) and x['mount_point'] == '/':
                is_system_disk = True
                break

        #print('device_filename:',device_filename, type(device_filename))
        #print('is_system_disk:',is_system_disk, type(is_system_disk))
        #print('include_system_disks:',include_system_disks, type(include_system_disks))

        #/* append */
        if is_system_disk and (not include_system_disks):
            continue

        results.append(tmprow)

    return results


if __name__ == '__main__':
    print(simple_argparse(smart_scan_open, sys.argv[1:]))
