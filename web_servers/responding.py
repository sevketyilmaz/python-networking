from twisted.protocols.basic import LineReceiver
from twisted.internet import protocol, reactor


class HTTPEchoProtocol(LineReceiver):

    def __init__(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)
        if not line:
            self.sendResponse()

    def sendResponse(self):
        self.sendLine('HTTP/1.1 200 OK')
        self.sendLine('')
        body = 'You said:\r\n\r\n' + '\r\n'.join(self.lines)
        self.transport.write(body)
        self.transport.loseConnection()


class HTTPEchoFactory(protocol.ServerFactory):

    def buildProtocol(self, addr):
        return HTTPEchoProtocol()


reactor.listenTCP(8000, HTTPEchoFactory())
reactor.run()
