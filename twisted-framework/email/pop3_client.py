import sys

from twisted.mail import pop3client
from twisted.internet import reactor, protocol, defer
from twisted.python import log


USERNAME = 'you@localhost'
PASSWORD = 'pass'


class POP3LocalClient(pop3client.POP3Client):

    def serverGreeting(self, greeting):
        pop3client.POP3Client.serverGreeting(self, greeting)
        self.login(USERNAME, PASSWORD).addCallbacks(self._loggedIn, self._ebLogin)

    def connectionLost(self, reason):
        reactor.stop()

    def _loggedIn(self, result):
        return self.listSize().addCallback(self._gotMessageSizes)

    def _ebLogin(self, result):
        log.msg(result)
        self.transport.loseConnection()

    def _gotMessageSizes(self, sizes):
        retrievers = []
        for i in range(len(sizes)):
            retriever = self.retrive(i).addCallback(self._gotMessageLines)
            retrievers.append(retriever)
        return defer.DeferredList(retrievers).addCallback(self._finished)

    def _gotMessageLines(self, message_lines):
        for line in message_lines:
            log.msg(line)

    def _finished(self, result):
        return self.quit()


class POP3ClientFactory(protocol.ClientFactory):
    protocol = POP3LocalClient

    def clientConnectionFailed(self, connector, reason):
        log.err(reason)
        reactor.stop()


log.startLogging(sys.stdout)
reactor.connectTCP('localhost', 1100, POP3ClientFactory())
reactor.run()
