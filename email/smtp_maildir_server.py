from email.header import Header
import os
import sys

from twisted.internet import reactor
from twisted.mail import smtp, maildir
from twisted.python import log
from zope.interface import implements


class LocalMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, protocol, base_dir):
        self.protocol = protocol
        self.baseDir = base_dir

    def receivedHeader(self, helo, origin, recipients):
        client_hostname, client_ip = helo
        current_hostname = self.protocol.transport.getHost().host  # train-wreck
        header_value = 'from {client} by {current} with ESMTP ; {date}'.format(
                        client=client_hostname,
                        current=current_hostname,
                        date=smtp.rfc822date())
        output = Header(header_value)
        return 'Received {0}'.format(output)

    def validateFrom(self, helo, origin):
        '''Accept any sender'''
        return origin

    def __get_address_dir(self, address):
        return os.path.join(self.baseDir, str(address))

    def validateTo(self, user):
        if user.dest.domain == 'localhost':
            address_dir = self.__get_address_dir(user.dest)
            return lambda: MailDirMessage(address_dir)

        log.msg('Received mail for invalid recipient {0}'.format(user))
        raise smtp.SMTPBadRcpt(user)


class MailDirMessage:
    implements(smtp.IMessage)

    def __init__(self, user_dir):
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        inbox_dir = os.path.join(user_dir, 'Inbox')
        self.mailbox = maildir.MaildirMailbox(inbox_dir)
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        log.msg('New message received')
        data = '\n'.join(self.lines)
        return self.mailbox.appendMessage(data)

    def connectionLost(self):
        log.msg('Conection lost!')
        del self.lines


class LocalSMTPFactory(smtp.SMTPFactory):

    def __init__(self, base_dir):
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        self.baseDir = base_dir

    def buildProtocol(self, addr):
        proto = smtp.ESMTP()
        proto.delivery = LocalMessageDelivery(proto, self.baseDir)
        return proto


log.startLogging(sys.stdout)

reactor.listenTCP(2500, LocalSMTPFactory('/tmp/mail'))
reactor.run()
