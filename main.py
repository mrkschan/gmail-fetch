from datetime import datetime
import getpass
import os
import sys
import time

import gmail  # github.com/charlierguo/gmail

try:
    import argparse
except:
    # argparse is only available in Python 2.7+
    print >> sys.stderr, 'pip install -U argparse'
    sys.exit(1)


DATE_FORMAT = '%d-%b-%Y'
DATE_FORMAT_TEXT = DATE_FORMAT.replace('%', '')


def main():
    '''Fetch emails from Gmail and store them in local filesystem'''
    argparser = argparse.ArgumentParser(description=main.__doc__)
    argparser.add_argument('username', type=str, help='Gmail account')
    argparser.add_argument('-p', type=str, dest='password',
                           help='Gmail account password')
    argparser.add_argument('--label', type=str,
                           help='Filter email by label')
    argparser.add_argument('--content', type=str,
                           help='Filter email by content specified')
    argparser.add_argument('--before', type=str,
                           help=('Filter email received before the date (%s) '
                                 'in PDT') % DATE_FORMAT_TEXT)
    argparser.add_argument('--after', type=str,
                           help=('Filter email received after the date (%s) '
                                 'in PDT') % DATE_FORMAT_TEXT)
    argparser.add_argument('--on', type=str,
                           help=('Filter email received on the date (%s) '
                                 'in PDT') % DATE_FORMAT_TEXT)
    argparser.add_argument('-d', '--dir', type=str, default='.',
                           help='Output directory')
    argparser.add_argument('--trash', action='store_true',
                           help='Trash the email after it is fetched')
    argparser.add_argument('--pause', type=int, default=0,
                           help=('Pause between fetching each message '
                                 'for throttling, in second(s)'))
    args = argparser.parse_args()

    username = args.username
    try:
        password = args.password or getpass.getpass()
    except KeyboardInterrupt:
        sys.exit(1)

    mbox = gmail.login(username, password)

    if args.label:
        mbox = mbox.label(args.label)
        if not mbox:
            print >> sys.stderr, 'Specified label is not available.'
            sys.exit(1)

    mail_kwargs = {}
    if args.before:
        mail_kwargs['before'] = datetime.strptime(args.before, DATE_FORMAT)
    if args.after:
        mail_kwargs['after'] = datetime.strptime(args.after, DATE_FORMAT)
    if args.on:
        mail_kwargs['on'] = datetime.strptime(args.on, DATE_FORMAT)

    for email in mbox.mail(**mail_kwargs):
        email.fetch()
        if args.content and args.content not in email.body:
            continue

        subject = email.subject.replace('/', '_') \
                               .replace('\r', '_') \
                               .replace('\n', '_')
        sent_at = email.sent_at.strftime('%Y-%m-%d %H%M')
        sender = email.fr

        seq = 0
        filename = '%s - %s - %s.eml' % (subject, sender, sent_at)
        while os.path.exists(os.path.join(args.dir, filename)):
            seq += 1
            filename = '%s - %s - %s.eml.%d' % (subject, sender, sent_at, seq)

        with open(os.path.join(args.dir, filename), 'w') as f:
            print >> f, email.message

        if args.trash:
            email.delete()

        del email.message
        del email.body

        if args.pause:
            time.sleep(args.pause)


if __name__ == '__main__':
    main()
