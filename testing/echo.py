from twisted.internet import protocol, reactor


class Echo(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return Echo()


if __name__ == '__main__':
    # Mandatory if testing.
    # Otherwise it'll idle and listen while tests never complete
    reactor.listenTCP(8000, EchoFactory())
    reactor.run()
