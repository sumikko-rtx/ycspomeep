#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from str_2_bool import str_2_bool
import hashlib
import os


def file_match_checksum(file_checksums=dict() ,
                        cwd='',
                        block_size=4096,
                        algorithm='sha512'):


    #/* this stores a list whether binary_mode is enabled or not */
    files_binary_mode_enabled = []

    #/* if file_checksums is str, convert text input to dict
    # */
    if isinstance(file_checksums,str):

        #/* When checking, the input
        # * should be a former output of this program.  The default mode is to print a
        # * line with checksum, a space, a character indicating input mode ('*' for binary,
        # * ' ' for text or where binary is insignificant), and name for each FILE.
        # */
        tmp = file_checksums.split(1)

        checksum = tmp[0]

        binary_mode = False
        if tmp[1][0] == '*':
            binary_mode = True

        file = tmp[1][1:]
        
        #/* output format should be same as file_gen_checksum
        # * i.e. (binary_mode, checksum)
        # */
        file_checksums[file] = (binary_mode, checksum)

    #/************************************************************************/

    for file, (binary_mode, checksum) in file_checksums:
        print(file, binary_mode, checksum)


        
  

if __name__ == '__main__':
    print(simple_argparse(file_match_checksum, sys.argv[1:]))
