from twisted.test import proto_helpers
from twisted.trial import unittest

from chat_server import ChatFactory


class ChatServerTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = ChatFactory()
        self.proto = self.factory.buildProtocol(('localhost', 0))
        self.transport = proto_helpers.StringTransport()
        self.proto.makeConnection(self.transport)

    def test_connect(self):
        self.assertEqual('What\'s your name?\r\n', self.transport.value())

    def test_register(self):
        self.transport.clear()  # clear what's your name message.
        self.assertEqual('REGISTER', self.proto.state)
        self.proto.lineReceived('foobar')
        self.assertEqual('Welcome foobar.\r\n', self.transport.value())
        self.assertIn('foobar', self.proto.factory.users)
        self.assertEqual('CHAT', self.proto.state)

    def test_register_existing_user(self):
        self.proto.lineReceived('foobar')
        self.assertIn('foobar', self.proto.factory.users)
        self.assertEqual('CHAT', self.proto.state)

        other_proto = self.factory.buildProtocol(('localhost', 0))
        other_transport = proto_helpers.StringTransport()
        other_proto.makeConnection(other_transport)

        other_transport.clear()  # clear what's your name message.
        other_proto.lineReceived('foobar')
        self.assertEqual('Name taken.\r\n', other_transport.value())

    def test_register_broadcast_when_other_user_joins(self):
        self.proto.lineReceived('foobar')

        other_proto = self.factory.buildProtocol(('localhost', 0))
        other_transport = proto_helpers.StringTransport()
        other_proto.makeConnection(other_transport)

        self.transport.clear()  # clear welcome message
        other_transport.clear()  # clear what's your name message.
        other_proto.lineReceived('barfoo')

        self.assertEqual('Welcome barfoo.\r\n', other_transport.value())
        self.assertEqual('barfoo has joined the channel.\r\n', self.transport.value())

    def test_chat(self):
        self.proto.lineReceived('foobar')

        other_proto = self.factory.buildProtocol(('localhost', 0))
        other_transport = proto_helpers.StringTransport()
        other_proto.makeConnection(other_transport)
        other_proto.lineReceived('barfoo')

        self.transport.clear()
        other_proto.lineReceived('echo echo echo')
        self.assertEqual('<barfoo> echo echo echo\r\n', self.transport.value())

    def test_disconnect(self):
        self.proto.lineReceived('foobar')

        other_proto = self.factory.buildProtocol(('localhost', 0))
        other_transport = proto_helpers.StringTransport()
        other_proto.makeConnection(other_transport)
        other_proto.lineReceived('barfoo')

        self.transport.clear()
        other_transport.loseConnection()
        other_proto.connectionLost()
        self.assertNotIn('barfoo', self.proto.factory.users)
        self.assertEqual('barfoo has left the channel.\r\n', self.transport.value())
