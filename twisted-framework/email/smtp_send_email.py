import sys

from email.mime.text import MIMEText

from twisted.internet import reactor
from twisted.mail.smtp import sendmail
from twisted.python import log


log.startLogging(sys.stdout)

host = 'localhost'
sender = 'secretguy@example.com'
recipients = ['you@localhost']

msg = MIMEText('Violets are blue,\nCan you read this message?\nOr SMTP is failing you?')
msg['Subject'] = 'Roses are red'
msg['From'] = '"Secret Guy" <{0}>'.format(sender)
msg['To'] = ','.join(recipients)


deferred = sendmail(host, sender, recipients, msg.as_string(), port=2500)
deferred.addBoth(lambda result: reactor.stop())
reactor.run()
