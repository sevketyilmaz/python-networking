from twisted.internet.defer import Deferred


def callback1(result):
    print 'Callback 1:', result
    return result


def callback2(result):
    print 'Callback 2:', result


def callback3(result):
    # result is None, cause callback2 returned None
    raise Exception('Callback 3:', result)


def errback1(failure):
    print 'Errback 1:', failure
    return failure


def errback2(failure):
    raise Exception('Errback 2:', failure)


def errback3(failure):
    print 'Errback 3 took care of', failure
    return 'Everything is fine'


if __name__ == '__main__':
    situation = input('situation:')
    if situation == 1:
        d = Deferred()
        # Should just print stuff
        d.addCallback(callback1)
        d.addCallback(callback2)
        d.callback('first situation')
    elif situation == 2:
        # Should go to the empty errback chain and get terminated,
        # cause there's nothing to handle the Exception
        d = Deferred()
        d.addCallback(callback1)
        d.addCallback(callback2)
        d.addCallback(callback3)
        d.callback('second situation')
    elif situation == 3:
        # Should handle the exception raised by callback3, since errback3 is 4th in the errchain.
        # The callback/errback chain is like:
        # C | PASS
        # C | PASS
        # C EXCEPTION | PASS
        # PASS | ERR
        d = Deferred()
        d.addCallback(callback1)
        d.addCallback(callback2)
        d.addCallback(callback3)
        d.addErrback(errback3)
        d.callback('third situation')
    elif situation == 4:
        # Terminates cause errback1 returns the Exception (wrapped as a Failure),
        # but there are no more errbacks in the errchain to handle it.
        d = Deferred()
        d.addErrback(errback1)
        d.errback(ValueError('fourth situation'))
    elif situation == 5:
        # Errchain is cleared up and Failure is handled by errback3
        d = Deferred()
        d.addErrback(errback1)
        d.addErrback(errback3)
        d.errback(ValueError('fifth situation'))
    elif situation == 6:
        # Terminates since there's nothing to handle the exception raised by errback2
        d = Deferred()
        d.addErrback(errback2)
        d.errback(ValueError('sixth situation'))
    elif situation == 7:
        # Terminates, because callback3 raises an Exception that can't be handled.
        # callback3 and errback3 are both at level 3, but to handle the Failure,
        # we need an errback at level 4.
        d = Deferred()
        d.addCallback(callback1)
        d.addCallback(callback2)
        d.addCallbacks(callback3, errback3)
        d.callback('seventh situation')
    elif situation == 8:
        # callback3 raises an exception and sends it to errback3.
        # errback3 handles it and sends it to the next level where
        # callback1 lies.
        # Important to note is that callback2 is skipped!
        d = Deferred()
        d.addCallback(callback3)
        d.addCallbacks(callback2, errback3)
        d.addCallbacks(callback1, errback2)
        d.callback('eight situation')
