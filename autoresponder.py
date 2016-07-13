import email
import email.parser
import email.utils
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import MySQLdb
import re
import datetime
import logging

# Defaults settings
DEFAULTS = {
    'db': 'postfix',
    'dbuser': 'postfix',
    'dbpassword': 'CHANGEME',
    'loglevel': 'DEBUG',
    'logfile': '/var/log/responder.log'
}

allowed_log_levels = {'INFO': logging.INFO, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING, 'DEBUG': logging.DEBUG}


def main():
        try:
            logging.basicConfig(filename=DEFAULTS['logfile'], level=allowed_log_levels[DEFAULTS['loglevel']])
            logging.debug('BEGIN')
            parser = email.parser.HeaderParser()
            headers = parser.parse(sys.stdin)
            from_addr = email.utils.parseaddr(headers.get('From'))
            to_addr = email.utils.parseaddr(headers.get('To'))
            xloop = email.utils.parseaddr(headers.get('X-loop'))
            logging.debug(headers.items())

            logging.debug('X-loop: {} {}'.format(xloop, to_addr))
            if xloop[1] == to_addr[1]:
                logging.debug('X-loop detected:')
                logging.debug('END')
                sys.exit(0)
            if 'MAILER-DAEMON' in from_addr[1]:
                logging.debug('MAILER-DAEMON detected')
                logging.debug('END')
                sys.exit(0)

            try:
                db = MySQLdb.connect(host="localhost", user=DEFAULTS['dbuser'], passwd=DEFAULTS['dbpassword'],
                                     db=DEFAULTS['db'], use_unicode=True, charset="utf8")
            except Exception as e:
                logging.exception('END')
                sys.exit(0)
            c = db.cursor()
            query = 'SELECT message FROM postfix_autoresponder WHERE email="{}" AND `from`<=NOW() AND `to`>=NOW()'.format(
                to_addr[1])
            c.execute(query)
            logging.debug(query)
            row = c.fetchone()
            if row is None:
                logging.debug('END')
                sys.exit(0)

            msg = MIMEMultipart('alternative')
            msg['From'] = to_addr[1]
            msg['To'] = from_addr[1]
            msg['Subject'] = 'Re: {}'.format(headers.get('Subject', ''))
            msg['X-loop'] = to_addr[1]
            msg['Auto-Submitted'] = 'auto-replied'
            logging.debug(msg.items())

            text = re.sub("<.*?>", "", row[0])
            html = row[0]
            part1 = MIMEText(text, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')

            msg.attach(part1)
            msg.attach(part2)

            s = smtplib.SMTP('localhost')
            s.sendmail(to_addr[1], from_addr[1], msg.as_string())
            s.quit()
            logging.debug('SENT to {}'.format(from_addr[1]))
            logging.debug('END')
            sys.exit(0)
        except Exception as e:
            logging.debug(e)
            sys.exit(0)


if __name__ == '__main__':
    main()
