
#/* True to enable backup disk isolaton; False otherwise
# */
ISOLATE_DISKS_ENABLE = False

#/* Specify list of disks, including mounting points, to be isolated
# *
# * Please use mount, smartmontools or gnome-disk-utility to find the
# * corresponding serial numbers, mount settings, and so on.
# *
# * If ISOLATE_DISKS or ISOLATE_MDADM_ARRAYS leaves empty, no disk isolation performs!!!
# */

#
# Single disk example:
#
# ISOLATE_DISKS = {
#
#     'X8HMMTZV': { # << drive serial number to be isolated
#
#         # --- start of disk partitions list ---
#
#         1: { # << the (n)th partition, corresponding /dev/sdX(n)
#             'mount_point': '',         # << the mouting point
#             'file_system_type': '',    # << file system type, matches mount(8)'s -t option
#             'mount_options': '',       # << mount option, matches mount(8)'s -o option
#         },
#
#         # --- end of disk partitions list ---
#     },
# }
#

ISOLATE_DISKS = {
}

#
# Raid example:
#
# ISOLATE_MDADM_ARRAYS = {
#
#     '/dev/md0': { # << device filename for MDADM array (e.g.: /dev/md0)
#
#         'disk_serial_numbers': [   # << a list of drive serial numbers to re-assemble an array
#             '9HSSNTK8', 'L34MS67U'
#         ],
#
#         # --- start of disk partitions list ---
#
#         'mount_point': '',         # << the mouting point
#         'file_system_type': '',    # << file system type, matches mount(8)'s -t option
#         'mount_options': '',       # << mount option, matches mount(8)'s -o option
#
#         # --- end of disk partitions list ---
#     },
# }
#
ISOLATE_MDADM_ARRAYS = {
}
