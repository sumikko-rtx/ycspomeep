#!/usr/bin/env python3
import math


def simple_argparse(func, args):

    #/* this will store args to be passed to func_*/
    func_args = list()
    func_kwargs = dict()

    #/* True to continue parse argument, False otherwise*/
    argparse_enable = True

    j = 0
    n_args = len(args)
    while j < n_args:

        #/* argparse_enable=False, append to func_args directly */
        if not argparse_enable:
            func_args.append(args[j])

        else:

            #/* looks for args[j] start with -- */
            if args[j].startswith('--'):

                #/* just --, stop parsing argument futher */
                if args[j] == '--':
                    argparse_enable = False

                else:

                    #/* get function argument name k: remove -- from args[j] */
                    k = args[j][2:]
                    k = k.replace('-', '_')

                    #/* get function argument name k: from args[j+1] */
                    #/* we need to additional check so that no index error is thrown */
                    j = j + 1
                    if j >= n_args:
                        v = None
                    else:
                        v = args[j]

                    #/* parse is finished, add to func_kwargs */
                    func_kwargs[k] = v

            #/* otherwise append to func_args directly */
            else:
                func_args.append(args[j])

        #/* next argument args[j] */
        j = j + 1

    #/* finally call the given func */
    retval = func(*func_args, **func_kwargs)

    #/* return non-none value from func */
    if not retval is None:
        return retval
    
    return ''
    

if __name__ == '__main__':

    #/* example: solve for real values of x : xa^2* + bs + c = 0 */
    def quadratic_roots(a, b, c):

        #/* input may be string */
        a = float(a)
        b = float(b)
        c = float(c)

        P = -b
        Q = b * b - a * c * 4
        R = a * 2

        if Q < 0:
            raise Exception('no real roots')

        X1 = (P + math.sqrt(Q)) / R
        X2 = (P - math.sqrt(Q)) / R
        return X1, X2

    print(simple_argparse(quadratic_roots, ['--a', 1, '--b', 1, '--c', 1]))
