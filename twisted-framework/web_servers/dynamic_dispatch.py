from calendar import calendar
from datetime import datetime

from twisted.internet import reactor
from twisted.web import resource
from twisted.web.util import redirectTo
from twisted.web.server import Site


class YearPage(resource.Resource):

    def __init__(self, year):
        resource.Resource.__init__(self)
        self.year = year

    def render_GET(self, request):
        return '<html><body><pre>{0}</pre></body></html>'.format(calendar(self.year))


class CalendarHome(resource.Resource):

    def getChild(self, name, request):
        if name == '':
            return self
        elif name.isdigit():
            return YearPage(int(name))
        else:
            return resource.NoResource()

    def render_GET(self, request):
        # return '<html><body>Welcome to the calendar server!</body></html>'
        return redirectTo(datetime.utcnow().year, request)


root = CalendarHome()
factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
