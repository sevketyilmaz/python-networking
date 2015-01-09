from twisted.internet import protocol, reactor


class EchoClient(protocol.Protocol):

    def connectionMade(self):
        self.transport.write('Connected!')

    def dataReceived(self, data):
        print 'Server responded: {0}'.format(data)
        self.transport.loseConnection()


class EchoClientFactory(protocol.ClientFactory):

    def buildProtocol(self, addr):
        return EchoClient()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed'
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'Connection lost'
        reactor.stop()


if __name__ == '__main__':
    reactor.connectTCP('localhost', 8000, EchoClientFactory())
    reactor.run()
