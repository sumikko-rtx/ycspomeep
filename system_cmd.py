#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import subprocess
import time
import chardet
from str_2_bool import str_2_bool


class SystemCmdException(Exception):
    pass




def __str_decode_autodetect(input_string, encoding):

    target_encoding = encoding

    if not target_encoding:
        target_encoding = chardet.detect(input_string)['encoding']

    output_string = input_string.decode(target_encoding)
    
    #print('target_encoding:',target_encoding)
    #print('output_string:',output_string)
    return output_string




def system_cmd(*cmd,
               cwd=os.getcwd(),
               envs={},
               input_encoding='utf-8',
               output_encoding=None,
               input_string='',

               input_file='',
               output_file='',
               error_file='',

               output_quiet=True,
               error_quiet=True,

               output_append=False,
               error_append=False,

               output_strip_whitespace=True,
               error_strip_whitespace=True,

               enable_cond_op=True,
               raise_exception=True,
               ):
    '''
    @description:
    Run system commands.',

    The command <cmd> is executed in C locale. Command alias not supported.

    @param cmd@c: The system command to run, plus arguments. Support && and || operaters.
    @param cwd@w: The working directory of the running <cmd>.
    @param env@v: Sets for environment variable, in a form VAR=VALUE (can be used many times).
    @param input_encoding@e: Select for character encoding for readig from stdin.
    @param output_encoding@e: Select for character encoding for writing to stdout or stderr.
    @param special_fx_kwargs: Additional options to be passed on to the function sumikko_func_begin.
    @param output_file: File for storing stdout output.
    @param error_file: File for storing stderr output.
    @param output_quiet: if set to true, do not print stdout content to stdout.
    @param error_quiet: if set to true, do not print stdout content to stderr.
    
    @param enable_cond_op: If set to True, enable conditional operator && and || ; Otherwise treat && and || as command arguments.
    
    @param raise_exception: If set to True, raise SystemCmdException with strerr message set.
    
    0: Exit status of <cmd>.
    1: stdout output of <cmd>.
    2: stderr output of <cmd>.
    3: Total execution time of running <cmd>.
    '''
    
    output_quiet = str_2_bool(output_quiet)
    error_quiet = str_2_bool(error_quiet)
    output_append = str_2_bool(output_append)
    error_append = str_2_bool(error_append)
    output_strip_whitespace = str_2_bool(output_strip_whitespace)
    error_strip_whitespace = str_2_bool(error_strip_whitespace)
    enable_cond_op = str_2_bool(enable_cond_op)
    raise_exception = str_2_bool(raise_exception)

    cmd_final=list(cmd)
    #print('cmd_final:',cmd_final)


    #/* update_from_git form system's envs */
    envs.update(os.environ)


    #/* use C locale */
    envs['LANG'] = 'C'

    #/************************************************************************/

    #/* separate cmd_final by && or || */
    cmd_final.insert(0, '&&')
    cmd_final.append('&&')
    
    combination_cmds = []
    currnet_op = '&&'
    current_cmd = []
    
    for x in cmd_final:

        if x in ['&&', '||']:

            if len(current_cmd) > 0:
                
                #/* make a copy of current_cmd*/
                tmp = []
                tmp.extend(current_cmd)
                combination_cmds.append([currnet_op, tmp])

            currnet_op = x
            current_cmd.clear()

        else:

            current_cmd.append(x)

    #for _op,_cmd in combination_cmds:
    #   print(_op,_cmd)

    #/************************************************************************/

    #/* handle for input file and  input string */
    try:

        if input_file:
            with open(input_file, 'rb') as f:
                input_data = f.read()
        else:
            raise Exception()

    except Exception as e:
        input_data = input_string.encode(input_encoding)

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
        pass
        #raise SystemCmdException(
        #    'Cannot determine path variable from unknown OS.')


    #/************************************************************************/

    #/* this sets _cmd[0], the program name */
    prog_name = ''

    #/* true if prog_name found; False otherwise */
    prog_found = True

    #/* this variables to be returned...*/
    return_code = 0
    
    #/* these store stdout and stderr */
    outputs = []
    errors = []
    
    #/* records total execution time */
    elapsed_n_seconds = 0.0




    #/* run each cmd combination */
    for j, (_op, _cmd) in enumerate(combination_cmds):

        #/* --- select for operator _op --- */
        
        #/* only handle _op on combination_cmds[1] or after!!! */
        if enable_cond_op and j > 0:
            
            #/* handle || operator */
            if _op == '||' and return_code == 0:
                continue

            #/* handle && operator */
            if _op == '&&' and return_code != 0:
                continue

        #print('running:',_cmd)


        #/* --- Identify the actual executable path of _cmd[0] --- */
        prog_name = _cmd[0]
        prog_found = False

        for x in possible_search_paths:
            prog_path = os.path.join(x, _cmd[0])

            #/* filepath have executable permission... */
            if os.path.isfile(prog_path) \
                    and os.access(prog_path, os.X_OK):

                prog_found = True
                _cmd[0] = prog_path
                break

        if not prog_found:
            tmp_error = 'command not found: {0}'.format(_cmd[0])
            return_code = 1
            continue


    
        #/* --- run command by opening a pipe --- */
    
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
    
        #/* TODO how to feed input_string/input_file into string */
        p = subprocess.Popen(
            _cmd,
            stdin=subprocess.PIPE,
            stdout=f_output,
            stderr=f_error,
            env=envs,
            cwd=cwd
        )
    
        #/* record start time tick */
        t1 = time.time()

        #/* TODO what happen if CTRL+C is pressed??? */
        #/* run command actually take place */
        tmp_output, tmp_error = p.communicate(input=input_data)
    
        #/* record end time tick */
        t2 = time.time()
    
        #/* get stdout from running commnad */
        if tmp_output:
            tmp_output = __str_decode_autodetect(tmp_output, output_encoding)
        else:
            tmp_output = ''
    
        #/* get stderr from running commnad */
        if tmp_error:
            tmp_error = __str_decode_autodetect(tmp_error, output_encoding)
        else:
            tmp_error = ''
    
        #/* strip leading/trailing whitespace(s) from stdout */
        if output_strip_whitespace:
            tmp_output = tmp_output.strip()
            
        #/* strip leading/trailing whitespace(s) from stderr*/
        if error_strip_whitespace:
            tmp_error = tmp_error.strip()
    
        #/* accumulate the current execution time of this _cmd */
        elapsed_n_seconds = elapsed_n_seconds + (t2 - t1)
    
        #/* the program return code */
        return_code = p.returncode
        
        #/* append stdout and stderr */
        outputs.append(tmp_output)
        errors.append(tmp_error)
        

    #/************************************************************************/

    #/* handle raise_exception if command error */
    if raise_exception and return_code != 0:

        #/* error is empty, try output */
        if not tmp_error:
            tmp_error = tmp_output

        raise SystemCmdException(
            'command {0} return exit status {1}: {2}'.format(prog_name, return_code, tmp_error))
        
    #/************************************************************************/

    return return_code, ''.join(outputs), ''.join(errors), elapsed_n_seconds  # CCCsumikko_func_end


if __name__ == '__main__':
    print(simple_argparse(system_cmd, sys.argv[1:]))

