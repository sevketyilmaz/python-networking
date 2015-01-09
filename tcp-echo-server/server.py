from twisted.internet import protocol, reactor


class EchoProtocol(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return EchoProtocol()


if __name__ == '__main__':
    reactor.listenTCP(8000, EchoFactory())
    reactor.run()
