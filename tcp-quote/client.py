from twisted.internet import protocol, reactor


class QuoteProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.sendQuote()

    def sendQuote(self):
        self.transport.write(self.factory.quote)

    def dataReceived(self, data):
        print 'Received:', data
        self.transport.loseConnection()


class QuoteClientFactory(protocol.ClientFactory):

    def __init__(self, quote):
        self.quote = quote

    def buildProtocol(self, addr):
        return QuoteProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed:', reason.getErrorMessage()
        maybeStopReactor()

    def clientConnectionLost(self, connector, reason):
        print 'Connection lost', reason.getErrorMessage()
        maybeStopReactor()


def maybeStopReactor():
    global quote_counter
    quote_counter -= 1
    if not quote_counter:
        reactor.stop()


quotes = (
    'It is never too late to be what you might have been.',
    'If one way be better than another, that you may be sure is nature\'s way.',
    'There is nothing more deceptive than an obvious fact.',
)
quote_counter = len(quotes)


if __name__ == '__main__':
    for quote in quotes:
        reactor.connectTCP('localhost', 8000, QuoteClientFactory(quote))
    reactor.run()
