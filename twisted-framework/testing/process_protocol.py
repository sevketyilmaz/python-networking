import sys

from twisted.internet import protocol
from twisted.python import log


class EchoProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, reactor):
        self.reactor = reactor

    def connectionMade(self):
        log.msg('connectionMade called')
        self.reactor.callLater(10, self.terminateProcess)

    def terminateProcess(self):
        self.transport.signalProcess('TERM')

    def outReceived(self, data):
        log.msg('outReceived called with {0} bytes of data: {1}'.format(len(data), data))

    def errReceived(self, data):
        log.err('errReceived calleld with {0} bytes of data: {1}'.format(len(data), data))

    def inConnectionLost(self):
        log.msg('inConnectionLost called, stdin closed.')

    def outConnectionLost(self):
        log.msg('outConnectionLost called, stdout closed.')

    def errConnectionLost(self):
        log.msg('errConnectionLost called, stderr closed.')

    def processExited(self, reason):
        log.msg('processExited called with status', reason.value.exitCode)

    def processEnded(self, reason):
        log.msg('processEnded called with status', reason.value.exitCode)
        log.msg('All File descriptors closed and the process has been reaped')
        self.reactor.stop()

log.startLogging(sys.stdout)
