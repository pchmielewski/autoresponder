import email
import email.parser
import email.utils
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import MySQLdb
import re
import logging

# Defaults settings
DEFAULTS = {
    'db': 'postfix',
    'dbuser': 'postfix',
    'dbpassword': 'CHANGEME',
    'loglevel': 'DEBUG',
    'logfile': '/var/log/autoresponder.log'
}

allowed_log_levels = {'INFO': logging.INFO, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING, 'DEBUG': logging.DEBUG}

def main():
    try:
        FORMAT = "%(asctime)-15s [%(levelname)-10s][%(process)s] %(message)s"
        logging.basicConfig(filename=DEFAULTS['logfile'], level=allowed_log_levels[DEFAULTS['loglevel']], format=FORMAT)
        logging.debug('Start processing...')
        parser = email.parser.HeaderParser()
        headers = parser.parse(sys.stdin)
        from_addr = email.utils.parseaddr(headers.get('From'))
        to_addr = email.utils.parseaddr(headers.get('To'))
        xloop = email.utils.parseaddr(headers.get('X-loop'))
        logging.debug(headers.items())
        if xloop[1] == to_addr[1]:
            logging.debug('X-loop detected. Exiting')
            sys.exit(0)
        if 'MAILER-DAEMON'.lower() in from_addr[1].lower():
            logging.debug('MAILER-DAEMON detected. Exiting.')
            sys.exit(0)
        if ('Auto-submitted' or 'auto-replied' or 'auto-notified') in headers:
            logging.debug('Autoreply detected. Exiting.')
            sys.exit(0)

        try:
            db = MySQLdb.connect(host="localhost", user=DEFAULTS['dbuser'], passwd=DEFAULTS['dbpassword'],
                                 db=DEFAULTS['db'], use_unicode=True, charset="utf8")
        except Exception as e:
            logging.exception('MySQL connection failure. Exiting.')
            sys.exit(0)
        c = db.cursor()
        query = 'SELECT message FROM postfix_autoresponder WHERE email="{}" AND `from`<=NOW() AND `to`>=NOW()'.format(
            to_addr[1])
        c.execute(query)
        logging.debug(query)
        row = c.fetchone()
        if row is None:
            logging.debug('Autoresponder not found. Exiting.')
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
        logging.debug('Exiting.')
        sys.exit(0)
    except Exception as e:
        logging.exception('main() failure')
        sys.exit(0)


if __name__ == '__main__':
    main()
