import os
import sys
from simple_argparse import simple_argparse


#
# checking if the user of a script has root-like privileges?
#
def check_if_root(raise_exception=True):

    #/* https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows */

    user_is_root = True

    #/* uid = 0: it is a root user */
    try:
        user_is_root = bool(os.getuid() == 0)

    #/* for windows, use shell32.dll api: IsUserAnAdmin */
    except AttributeError:
        import ctypes
        user_is_root = bool(ctypes.windll.shell32.IsUserAnAdmin() != 0)

    if not user_is_root:

        if raise_exception:
            raise Exception("This program requires root privileges!!!")

    return user_is_root


if __name__ == "__main__":
    print(simple_argparse(check_if_root, sys.argv[1:]))
