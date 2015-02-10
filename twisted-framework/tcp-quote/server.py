from twisted.internet import protocol, reactor


class QuoteProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.numConnections += 1

    def dataReceived(self, data):
        print 'Current number of connections:', self.factory.numConnections
        print 'Received:', data
        quote = self.getQuote()
        self.transport.write(quote)
        print 'Sending:', quote
        self.updateQuote(data)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1

    def getQuote(self):
        return self.factory.quote

    def updateQuote(self, quote):
        self.factory.quote = quote


class QuoteFactory(protocol.Factory):
    numConnections = 0

    def __init__(self, quote=None):
        self.quote = quote or 'If you have a problem, call it a feature.'

    def buildProtocol(self, addr):
        return QuoteProtocol(self)


if __name__ == '__main__':
    reactor.listenTCP(8000, QuoteFactory())
    reactor.run()
