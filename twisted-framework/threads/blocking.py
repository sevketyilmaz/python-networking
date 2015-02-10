import time

from twisted.internet import reactor, threads
from twisted.internet.task import LoopingCall


def blockingCall(arg):
    time.sleep(1)
    return arg


def nonBlockingCall(arg):
    print arg


def printResult(result):
    print result


def finish():
    reactor.stop()


d = threads.deferToThread(blockingCall, 'Foo')
d.addCallback(printResult)


LoopingCall(nonBlockingCall, 'Bar').start(.30)

reactor.callLater(2, finish)
reactor.run()
