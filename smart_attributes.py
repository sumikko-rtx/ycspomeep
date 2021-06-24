#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import re
from system_cmd import system_cmd

#
# run smartctl --attributes
#
# to list disk S.M.A.R.T. attribute information.
#
def smart_attributes(device_filename,
                      device_type,
                      ):
    '''
    @description:
    Print disk S.M.A.R.T. status information.

    This program does detect S.M.A.R.T. enabled drive only. Not suitable for
    CD/DVD ROM drives, or removable USB Flash Drives.

    To determine whether the disk is usable, use function check_disk_health.
    
    This function requires smartctl to run.
    SystemCmdException is raised if smartctl has encountered an error.
    
    @param device_filename@f: The drive device filename. (e.g. /dev/sda)
    @param device_type@d: The type of the device. (e.g. sat, ata...)

    @retval disk_smart_status_table: A table of disk smart status attributes.
    '''

    #/************************************************************************/

    #/* this will placed the result status (dict type ) */
    results = {}

    #/************************************************************************/

    #/* get device smart status */
    #/* smartctl --attributes --device <device_type> -- <device_filename> */
    unused, cmd_output, unused, unused = system_cmd(
        *[
            'smartctl', '--attributes',
            '--device', device_type,
            '--', device_filename,
        ]
    )

    #/* split lines in cmd_output */
    cmd_output = cmd_output.strip()
    cmd_output_lines = cmd_output.splitlines()

    #/* start parsing the smartctl output */
    parse_smart_data_ready = False
    for line in cmd_output_lines:

        #
        # Sample output
        # =============
        #
        # smartctl 7.0 2019-03-31 r4903 [x86_64-linux-5.2.14-200.fc30.x86_64] (local build)
        # Copyright (C) 2002-18, Bruce Allen, Christian Franke, www.smartmontools.org
        #
        # === START OF READ SMART DATA SECTION ===
        # SMART Attributes Data Structure revision number: 16
        # Vendor Specific SMART Attributes with Thresholds:
        #
        # (0) (1)                     (2)      (3)   (4)   (5)    (6)       (7)      (8)         (9)
        # ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
        #   3 Spin_Up_Time            0x0027   206   206   063    Pre-fail  Always       -       15760
        #   4 Start_Stop_Count        0x0032   252   252   000    Old_age   Always       -       2531
        #   5 Reallocated_Sector_Ct   0x0033   253   253   063    Pre-fail  Always       -       0
        #

        #/* locate the line 'ID# ATTRIBUTE_NAME FLAG VALUE WORST THRESH TYPE UPDATED WHEN_FAILED RAW_VALUE'
        # * should have 10 items
        # */
        items = line.split(None, 9)
        # print(items)
        
        #/* items must have exact 10 entries */
        if len(items) == 10 and \
                items[0] == 'ID#' and \
                items[1] == 'ATTRIBUTE_NAME' and \
                items[2] == 'FLAG' and \
                items[3] == 'VALUE' and \
                items[4] == 'WORST' and \
                items[5] == 'THRESH' and \
                items[6] == 'TYPE' and \
                items[7] == 'UPDATED' and \
                items[8] == 'WHEN_FAILED' and \
                items[9] == 'RAW_VALUE':
            parse_smart_data_ready = True
            continue

        #/* ready to parse smart attribute data */
        if len(items) == 10 and parse_smart_data_ready:
            
            #/* create empty row */
            tmprow = {}
            
            #/* get all data columns */
            id_ = int(items[0])

            tmprow['attribute_name'] = str(items[1])
            tmprow['flag'] = int(items[2],16) # /*<< represent as hex */
            tmprow['value'] = int(items[3])  # /*<< range between 0 and 255 */
            tmprow['worst'] = int(items[4])  # /*<< range between 0 and 255 */
            tmprow['thresh'] = int(items[5])  # /*<< range between 0 and 255 */
            tmprow['type_'] = str(items[6])  # /*<< pre-fail or old-age */
            tmprow['updated'] = str(items[7])  # /*<< Always or offline */
            tmprow['when_failed'] = str(items[8])
            
            tmprow['raw'] = str(items[9])



            #/* for attribute id 9: Power_On_Hours
            # *
            # * Power_On_Hours shall keep as low as possible.
            # */
            if id_ in [9]:

                #/* some Maxtor (now Seagate) HDD model have the raw value
                # * format like:
                # * 299h+53m
                # */
                g = re.search(r'^([0-9]+)h[+]([0-9]+)m$',
                              tmprow['raw'].lower())

                if g:
                    hours = float(g.group(1))
                    minutes = float(g.group(2))
                    tmprow['raw'] = hours + minutes / 60.0





            #/* for attribute id 194:
            # *
            # * some manufacturers may provide additional information
            # * such as max/min temperature into raw data
            # *
            # * extract first numeric data only
            # */
            if id_ in [194]:

                #/* note: the temperate from smartctl is expressed in deg C
                # * remove min max
                # */
                temp = tmprow['raw']
                g = re.search(r'^[0-9]+([.][0-9]+)?', temp)
                temp = g.group(0)
                temp = float(temp)
                tmprow['raw'] = temp

            #/* other attributes */
            else:
                pass

            #/* append */
            results[id_] = tmprow

    return results


if __name__ == '__main__':
    print(simple_argparse(smart_attributes, sys.argv[1:]))
