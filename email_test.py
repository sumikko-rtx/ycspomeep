#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from email_report2 import email_report2



def email_test():

    email_report2(subject='a test messages from the backup server',
                  header_msg='If you are reading this message, congratulations!!! You have successfully configured the email notification on your backup server!!!',
                  )

    print('INFO: A test mail is sent. Please check your recipient\'s e-mail inbox.')

if __name__ == '__main__':
    print(simple_argparse(email_test, sys.argv[1:]))

