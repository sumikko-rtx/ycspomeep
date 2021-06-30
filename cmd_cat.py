#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os


#
# Run command:
#
# cat <input_filename1> <input_filename2> ... > <output_filename> (truncate=True)
# cat <input_filename1> <input_filename2> ... >> <output_filename> (truncate=False)
#
# if output_file is None, just print the concatenated output
#

def __read_input_file(input_filename):

    #/* resolve link: input_file */
    input_file = os.path.realpath(input_filename)

    #/* prepare input file content */
    input_file_content = bytes()

    try:
        with open(input_file, 'rb') as fin:
            input_file_content = fin.read()

    #/* ignore file error... */
    except Exception as e:
        pass

    return input_file_content


def cmd_cat(output_filename, *input_filenames, truncate=False):

    #/* resolve link: output_file */
    output_file = None
    if output_filename:
        output_file = os.path.realpath(output_filename)

    #/* select file operation mode, from description above */
    mode = 'ab'
    if truncate:
        mode = 'wb'
    #print('mode:',mode)

    #/* avaliable if output_file=None */
    #/* bytes is immutable. Use bytearray. */
    concatenated_output = bytearray()

    #/* output to file... */
    if output_file:
        with open(output_file, mode) as fout:
            for x in input_filenames:
                fout.write(__read_input_file(x))

    #/* print the concatenated output... */
    else:
        for x in input_filenames:
            #/* use += to append bytes objects */
            concatenated_output += __read_input_file(x)

    return concatenated_output


if __name__ == '__main__':
    print(simple_argparse(cmd_cat, sys.argv[1:]))

