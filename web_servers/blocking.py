import time

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site


class BusyPage(Resource):
    isLeaf = True

    def render_GET(self, request):
        time.sleep(3)
        return 'Finished at {}'.format(time.asctime())


factory = Site(BusyPage())
reactor.listenTCP(8000, factory)
reactor.run()
