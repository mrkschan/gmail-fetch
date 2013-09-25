import getpass
import os
import sys

import gmail  # github.com/charlierguo/gmail

try:
    import argparse
except:
    # argparse is only available in Python 2.7+
    print >> sys.stderr, 'pip install -U argparse'
    sys.exit(1)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('username', type=str, help='Gmail account')
    argparser.add_argument('-p', type=str, dest='password',
                           help='Gmail account password')
    argparser.add_argument('-l', '--label', type=str,
                           help='Filter email by label')
    argparser.add_argument('-c', '--content', type=str,
                           help='Filter email by content specified')
    argparser.add_argument('-d', '--dir', type=str, default='.',
                           help='Output directory')
    args = argparser.parse_args()

    username = args.username
    password = args.password or getpass.getpass()

    mbox = gmail.login(username, password)

    if args.label:
        mbox = mbox.label(args.label)
        if not mbox:
            print >> sys.stderr, 'Specified label is not available.'
            sys.exit(1)

    for email in mbox.mail():
        email.fetch()
        if args.content and args.content not in email.body:
            continue

        subject = email.subject.replace('/', '_')
        sent_at = email.sent_at.strftime('%Y-%m-%d %H%M')
        sender = email.fr

        seq = 0
        filename = '%s - %s - %s.eml' % (subject, sender, sent_at)
        while os.path.exists(os.path.join(args.dir, filename)):
            seq += 1
            filename = '%s - %s - %s.eml.%d' % (subject, sender, sent_at, seq)

        with open(os.path.join(args.dir, filename), 'w') as f:
            print >> f, email.message


if __name__ == '__main__':
    main()
