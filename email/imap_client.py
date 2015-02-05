import sys

from twisted.internet import protocol, reactor
from twisted.mail import imap4
from twisted.python import log


USERNAME = 'you@localhost'
PASSWORD = 'pass'


class IMAP4LocalClient(imap4.IMAP4Client):

    def connectionMade(self):
        self.login(USERNAME, PASSWORD).addCallbacks(self._getMessages, self._ebLogin)

    def connectionLost(self, reason):
        reactor.stop()

    def _ebLogin(self, result):
        log.msg(result)
        self.transport.loseConnection()

    def _getMessages(self, result):
        return self.list('', '*').addCallback(self._cbPickMailbox)

    def _cbPickMailbox(self, result):
        try:
            mbox = [m for m in result if 'Inbox' in m[2]][0][2]
        except IndexError:
            log.err('No emails to show!')
            return
        return self.select(mbox).addCallback(self._cbExamineMailBox)

    def _cbExamineMailBox(self, result):
        return self.fetchMessage('1:*', uid=False).addCallback(self._cbFetchMessages)

    def _cbFetchMessages(self, result):
        for seq, message in result.iteritems():
            log.msg(seq, message['RFC822'])
        return self.logout()


class IMAP4ClientFactory(protocol.ClientFactory):

    protocol = IMAP4LocalClient

    def clientConnectionFailed(self, connector, reason):
        log.msg(reason)
        reactor.stop()

try:
    USERNAME = sys.argv[1] or USERNAME
    PASSWORD = sys.argv[2] or PASSWORD
except IndexError:
    pass


log.startLogging(sys.stdout)
reactor.connectTCP('localhost', 1430, IMAP4ClientFactory())
reactor.run()
