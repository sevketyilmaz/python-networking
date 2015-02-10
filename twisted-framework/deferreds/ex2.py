from twisted.internet.defer import Deferred


def errback(result):
    print result


d = Deferred()
d.addErrback(errback)
d.errback(ValueError('boom'))
