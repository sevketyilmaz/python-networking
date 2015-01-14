from twisted.internet import reactor
from twisted.web import http


class RequestHandler(http.Request):
    resources = {
        '/': '<h1>Home page</h1>',
        '/about': '<h1>About stuff</h1>',
    }

    def process(self):
        self.setHeader('Content-Type', 'text/html')

        if self.path in self.resources:
            self.write(self.resources[self.path])
        else:
            self.setResponseCode(http.NOT_FOUND)
            self.write('<h1>Not found, sorry!</h1>')
        self.finish()


class CustomHTTP(http.HTTPChannel):
    requestFactory = RequestHandler


class CustomHTTPFactory(http.HTTPFactory):

    def buildProtocol(self, addr):
        return CustomHTTP()


reactor.listenTCP(8000, CustomHTTPFactory())
reactor.run()
