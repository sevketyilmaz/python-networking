from twisted.internet import protocol, reactor
from twisted.python import log


class EchoProtocol(protocol.Protocol):

    def dataReceived(self, data):
        log.msg(data)
        self.transport.write(data)


class EchoFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return EchoProtocol()


log_file = open('echo.log', 'w')
log.startLogging(log_file)
reactor.listenTCP(8000, EchoFactory())
reactor.run()
