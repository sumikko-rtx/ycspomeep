#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import subprocess
import time


class SystemCmdException(Exception):
    pass


def system_cmd(cmd,
               sep=',',
               cwd=os.getcwd(),
               envs={},
               encoding='utf-8',
               input_string='',

               input_file='',
               output_file='',
               error_file='',

               output_quiet=True,
               error_quiet=True,

               output_append=False,
               error_append=False,

               raise_exception=True,
               ):
    '''
    @description:
    Run system commands.',

    The command <cmd> is executed in C locale. Command alias not supported.

    @param cmd@c: The system command to run, plus arguments.
    @param cwd@w: The working directory of the running <cmd>.
    @param env@v: Sets for environment variable, in a form VAR=VALUE (can be used many times).
    @param encoding@e: Select for character encoding for reading/writing stdin, stdout or stderr.
    @param special_fx_kwargs: Additional options to be passed on to the function sumikko_func_begin.
    @param output_file: File for storing stdout output.
    @param error_file: File for storing stderr output.
    @param output_quiet: if set to true, do not print stdout content to stdout.
    @param error_quiet: if set to true, do not print stdout content to stderr.
    @param raise_exception: If set to True, raise Exception with strerr message set.
    
    0: Exit status of <cmd>.
    1: stdout output of <cmd>.
    2: stderr output of <cmd>.
    3: Total execution time of running <cmd>.
    '''

    #/* split cmd argument, if any */
    if isinstance(cmd, str):
        cmd = cmd.split(sep)
    cmd = list(cmd)

    #/* update form system's envs */
    envs.update(os.environ)

    #/* use C locale */
    envs['LANG'] = 'C'

    #/************************************************************************/

    #/* handle for input file and  input string */
    try:

        if input_file:
            with open(input_file, 'rb') as f:
                input_data = f.read()
        else:
            raise Exception()

    except Exception as e:
        input_data = input_string.encode(encoding)

    #/************************************************************************/

    #/* default executable search paths in most *nix systems */

    possible_search_paths = [
        '',  # << shell builtin???
        os.path.join(os.sep, 'sbin'),
        os.path.join(os.sep, 'bin'),
        os.path.join(os.sep, 'usr', 'sbin'),
        os.path.join(os.sep, 'usr', 'bin'),
        os.path.join(os.sep, 'usr', 'local', 'sbin'),
        os.path.join(os.sep, 'usr', 'local', 'bin'),
    ]

    #/* Add $PATH to possible_paths */
    #/* *nix platform, separated by colon */
    if 'PATH' in envs:
        possible_search_paths.extend(
            envs['PATH'].split(':'))

    #/* windows platform, separated by semi-colon */
    elif 'path' in envs:
        possible_search_paths.extend(
            envs['path'].split(';'))

    else:
        raise SystemCmdException(
            'Cannot determine path variable from unknown OS.')

    #/* Identify the actual executable path of cmd[0] */
    for x in possible_search_paths:
        program_path = os.path.join(x, cmd[0])

        #/* filepath have executable permission... */
        if os.path.isfile(program_path) and \
                os.access(program_path, os.X_OK):
            cmd[0] = program_path
            break

    #/************************************************************************/

    #/* this variables to be returned...*/
    return_code = 0
    output = ''
    error = ''
    elapsed_n_seconds = 0.0

    #/* run command by opening a pipe... */
    try:

        #/* open output_file if any */
        f_output = sys.stdout

        if output_quiet:
            f_output = subprocess.PIPE

        if output_file:
            f_output = open(output_file, 'wb')

        #/* open error_file if any */
        f_error = sys.stderr

        if error_quiet:
            f_error = subprocess.PIPE

        if error_file:
            f_error = open(error_file, 'wb')

        #with open("stdout.txt","wb") as out, open("stderr.txt","wb") as err:
        #    subprocess.Popen("ls",stdout=out,stderr=err)

        #/* TODO how to feed input_string/input_file into string */
        p = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=f_output,
            stderr=f_error,
            env=envs,
            cwd=cwd
        )

        #/* record start time tick */
        t1 = time.time()

        #/* run command actually take place */
        output, error = p.communicate(input=input_data)

        #/* record end time tick */
        t2 = time.time()

        #/* get stdout from running commnad */
        if output:
            output = output.decode(encoding)
        else:
            output = ''

        #/* get stderr from running commnad */
        if error:
            error = error.decode(encoding)
        else:
            error = ''

        #/* print how long does it take to run this command */
        elapsed_n_seconds = t2 - t1

        #/* the program return code */
        return_code = p.returncode

    #/* CTRL+C is pressed...*/
    #except KeyboardInterrupt:
    #    raise KeyboardInterrupt

    except Exception as e:

        #/* in case of program not found error... */
        return_code = 1
        error = 'Cannot run command {0}: {1}'.format(cmd[0], str(e))

    #/************************************************************************/

    #/* raise exception if raise_exception is set and return code != 0*/
    if raise_exception and return_code != 0:

        #/* error is empty, try output */
        if not error:
            error = output

        raise SystemCmdException(
            'command {0} return exit status {1}: {2}'.format(cmd[0], return_code, error))

    return return_code, output, error, elapsed_n_seconds  # CCCsumikko_func_end


if __name__ == '__main__':
    print(simple_argparse(system_cmd, sys.argv[1:]))

