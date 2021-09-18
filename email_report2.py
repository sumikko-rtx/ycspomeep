#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from email_report import email_report

# for html_ecape function
from html import escape as html_escape # << python 3.2
from constants import CURRENT_VERSION



def email_report2(subject='important messages from the backup server',
                  header_msg='Critical or warning alerts were detected on your backup server. These issues may negatively affect your service. Please resolve them as soon as possible.',
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
            _body.append('<p>{0}</p>'.format(html_escape(header_msg)))

        #/* begin of message list */
        if success_msgs or info_msgs or warning_msgs or error_msgs:
            _body.append('<ul>')

        for x in success_msgs:
            _body.append('✅ {0}<br/>'.format(html_escape(x)))
            print('SUCCESS: {0}'.format(x))

        for x in info_msgs:
            _body.append('ℹ️ {0}<br/>'.format(html_escape(x)))
            print('INFO: {0}'.format(x))

        for x in warning_msgs:
            _body.append('⚠️ {0}<br/>'.format(html_escape(x)))
            print('WARNING: {0}'.format(x))

        for x in error_msgs:
            _body.append('❌ {0}<br/>'.format(html_escape(x)))
            print('ERROR: {0}'.format(x))

        #/* end of message list */
        if success_msgs or info_msgs or warning_msgs or error_msgs:
            _body.append('</ul>')

        #/* footer_msg */
        if footer_msg:
            _body.append('<p>{0}</p>'.format(html_escape(footer_msg)))

        #/* add version info at the end of this mail message */
        _body.append('<p>This mail was sent by ycspomeep version {0}.</p>'.format(html_escape(CURRENT_VERSION)))

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

