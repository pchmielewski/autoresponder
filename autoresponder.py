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

user = 'postfix'
password = 'xxx'
db = 'postfix'
		
def log(msg):
        with open('/var/log/responder.log', 'a+') as f:
           f.write('{} {}\n'.format(str(datetime.datetime.today()), msg))


try:
        log('BEGIN')
        msg = ''
        parser = email.parser.HeaderParser()
        headers = parser.parse(sys.stdin)
        from_addr = email.utils.parseaddr(headers.get('From'))
        to_addr = email.utils.parseaddr(headers.get('To'))
        xloop =  email.utils.parseaddr(headers.get('X-loop'))
        log(headers.items())

        log('X-loop: {} {}'.format(xloop, to_addr))
        if xloop[1] == to_addr[1]:
                log('X-loop detected:')
                log('END')
                sys.exit(0)
        if 'MAILER-DAEMON' in from_addr[1]:
                log('MAILER-DAEMON detected')
                log('END')
                sys.exit(0)

        try:
                db = MySQLdb.connect(host="localhost",user=user, passwd=password,db=db, use_unicode=True, charset="utf8")
        except Exception as e:
                log(e)
                log('END')
                sys.exit(0)
        c = db.cursor()
        query='SELECT message FROM postfix_autoresponder WHERE email="{}" AND `from`<=NOW() AND `to`>=NOW()'.format(to_addr[1])
        c.execute(query)
        log(query)
        row = c.fetchone()
        if row is None:
                log('END')
                sys.exit(0)

        msg = MIMEMultipart('alternative')
        msg['From'] = to_addr[1]
        msg['To'] = from_addr[1]
        msg['Subject'] = 'Re: {}'.format(headers.get('Subject', ''))
        msg['X-loop'] = to_addr[1]
        msg['Auto-Submitted'] = 'auto-replied'
        log(msg.items())

        text = re.sub("<.*?>", "", row[0])
        html = row[0]
        part1 = MIMEText(text, 'plain', 'utf-8')
        part2 = MIMEText(html, 'html', 'utf-8')

        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP('localhost')
        s.sendmail(to_addr[1], from_addr[1], msg.as_string())
        s.quit()
        log('SENT to {}'.format(from_addr[1]))
        log('END')
        sys.exit(0)
except Exception as e:
        log(e)
        sys.exit(0)
