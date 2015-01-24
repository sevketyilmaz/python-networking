from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.trial import unittest


class DeferredTestCase(unittest.TestCase):

    def slow_function(self):
        d = Deferred()
        reactor.callLater(1, d.callback, ('foo'))
        return d

    def test_slow_function(self):
        def cb(result):
            self.assertEqual(result, 'foo')

        d = self.slow_function()
        d.addCallback(cb)
        return d  # mandatory when testing deferreds
