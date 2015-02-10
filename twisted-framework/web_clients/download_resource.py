import sys

from twisted.internet import reactor
from twisted.web.client import downloadPage


def printError(failure):
    print >>sys.stderr, failure


def stop():
    reactor.stop()


if len(sys.argv) != 3:
    print >>sys.stderr, 'Usage: python download_resource.py <URL> <output_file>'
    exit(1)

url = sys.argv[1]
output = sys.argv[2]
d = downloadPage(url, output)
d.addErrback(printError)
d.addBoth(stop)

reactor.run()
