from twisted.test import proto_helpers
from twisted.trial import unittest

from echo import EchoFactory


class EchoServerTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = EchoFactory()

    def test_echo(self):
        proto = self.factory.buildProtocol(('localhost', 0))
        transport = proto_helpers.StringTransport()

        proto.makeConnection(transport)

        line = 'test\r\n'
        proto.dataReceived(line)
        self.assertEqual(transport.value(), line)
