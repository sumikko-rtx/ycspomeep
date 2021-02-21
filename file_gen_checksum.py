#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from str_2_bool import str_2_bool
import hashlib
import os


def file_gen_checksum(*files,
                      relative_to='',
                      binary_mode=True,
                      block_size=4096,
                      output_as_text=False,
                      algorithm='sha512'):

    #/* output_as_dict = True, return the result as dict
    # * otherwise output the sha*sum like format
    # */
    output_as_text = str_2_bool(output_as_text)

    #/* True to open file in binary mode */
    binary_mode = str_2_bool(binary_mode)

    file_checksums = dict()

    #/************************************************************************/

    #/* select for the checksum algorithms */
    algorithms_available = hashlib.algorithms_available

    if not (algorithm in algorithms_available):
        raise Exception(
            '{0}: unrecognized hashing algorithm'.format(algorithm))

    #/************************************************************************/

    #/* generate each file checksum using the selected hashing algorithm */
    for x in files:

        hash_class = getattr(hashlib, algorithm)
        hash_obj = hash_class()

        try:

            #/* append relative_to if any */
            if relative_to:
                fullpath_ = os.path.realpath(os.path.join(relative_to, x))

            else:
                fullpath_ = os.path.realpath(x)

            relpath_ = os.path.relpath(fullpath_, os.path.dirname(fullpath_))

            #/* select for file mode */
            mode = 'rb' if binary_mode else 'r'

            with open(fullpath_, mode) as f:

                while True:

                    f_chunk = f.read(block_size)

                    if not f_chunk:
                        break

                    hash_obj.update(f_chunk)

                #/* output format should be (binary_mode, checksum) */
                file_checksums[relpath_] = (
                    binary_mode, str(hash_obj.hexdigest()))

        except Exception as e:
            print('WARNING: cannot read file {0}: {1}'.format(x, e))

    #/************************************************************************/

    #/* convert to text output
    # */
    if output_as_text:

        tmp = file_checksums
        file_checksums = []

        #/* When checking, the input
        # * should be a former output of this program.  The default mode is to print a
        # * line with checksum, a space, a character indicating input mode ('*' for binary,
        # * ' ' for text or where binary is insignificant), and name for each FILE.
        # */
        for file, checksum in tmp.items():
            file_checksums.append('{0} {1}{2}'.format(
                checksum,
                '*' if binary_mode else '',
                file))

        file_checksums = '\n'.join(file_checksums)

    return file_checksums


if __name__ == '__main__':
    print(simple_argparse(file_gen_checksum, sys.argv[1:]))
