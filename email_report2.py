#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from email_report import email_report


def email_report2(subject='important messages from the backup server',
                  header_msg='Critical or warning alerts were detected on your the backup server. These issue may negatively affect your service. Please resolve them as soon as possible.',
                  success_msgs=[],
                  info_msgs=[],
                  warning_msgs=[],
                  error_msgs=[],
                  footer_msg='',
                  attach_files=[],
                  pidname='',
                  wait_interval_seconds=0,
                  ):

        #/* construct an email message */
        _body = []

        #/* header_msg */
        if header_msg:
            _body.append('<p>{0}</p>'.format(header_msg))

        #/* begin of message list */
        if success_msgs or info_msgs or warning_msgs or error_msgs:
            _body.append('<ul>')

        for x in success_msgs:
            _body.append('✅ {0}<br/>'.format(x))
            print('SUCCESS: {0}'.format(x))

        for x in info_msgs:
            _body.append('ℹ️ {0}<br/>'.format(x))
            print('INFO: {0}'.format(x))

        for x in warning_msgs:
            _body.append('⚠️ {0}<br/>'.format(x))
            print('WARNING: {0}'.format(x))

        for x in error_msgs:
            _body.append('❌ {0}<br/>'.format(x))
            print('ERROR: {0}'.format(x))

        #/* end of message list */
        if success_msgs or info_msgs or warning_msgs or error_msgs:
            _body.append('</ul>')

        #/* footer_msg */
        if footer_msg:
            _body.append('<p>{0}</p>'.format(footer_msg))

        #/* send email message*/
        email_report(
            subject=subject,
            message=''.join(_body),
            use_html_markup=True,
            attach_files=attach_files,
            encoding='utf-8',
            pidname=pidname,
            wait_interval_seconds=wait_interval_seconds,
        )


if __name__ == '__main__':
    print(simple_argparse(email_report2, sys.argv[1:]))

