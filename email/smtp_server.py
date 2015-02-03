from email.header import Header
import sys

from twisted.internet import defer, reactor
from twisted.mail import smtp
from twisted.python import log
from zope.interface import implements


class StdOutMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, protocol):
        self.protocol = protocol

    def receivedHeader(self, helo, origin, recipients):
        client_hostname, _ = helo
        current_hostname = self.protocol.transport.getHost().host  # train-wreck
        header_value = 'from {client} by {current} with ESMTP ;  {date}'.format(
            client=client_hostname,
            current=current_hostname,
            date=smtp.rfc822date())
        output = Header(header_value)
        return 'Received: {0}'.format(output)

    def validateFrom(self, helo, origin):
        '''Accept any sender'''
        return origin

    def validateTo(self, user):
        '''Accept recipients @localhost'''
        if user.dest.domain == 'localhost':
            return StdOutMessage
        else:
            log.msg('Received mail for invalid recipient', user)
            raise smtp.SMTPBadRcpt(user)


class StdOutMessage:
    implements(smtp.IMessage)

    def __init__(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        log.msg('New message received')
        log.msg('\n'.join(self.lines))
        self.lines = None
        return defer.succeed(None)


class StdOutSMTPFactory(smtp.SMTPFactory):

    def buildProtocol(self, addr):
        proto = smtp.SMTP()
        proto.delivery = StdOutMessageDelivery(proto)
        return proto


log.startLogging(sys.stdout)

reactor.listenTCP(2500, StdOutSMTPFactory())
reactor.run()
