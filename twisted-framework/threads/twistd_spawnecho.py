import sys

from twisted.internet import protocol, reactor
from twisted.python import log


class EchoProcessProtocol(protocol.ProcessProtocol):

    def connectionMade(self):
        log.msg('connectionMade called')
        reactor.callLater(10, self.terminateProcess)

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
        reactor.stop()


log.startLogging(sys.stdout)
pp = EchoProcessProtocol()
commandAndArgs = ['twistd', '-ny', 'echo_server.tac']
reactor.spawnProcess(pp, commandAndArgs[0], args=commandAndArgs)
reactor.run()
