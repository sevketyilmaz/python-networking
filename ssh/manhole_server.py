from twisted.conch import manhole, manhole_ssh
from twisted.cred import portal, checkers
from twisted.internet import reactor
from twisted.web import server, resource


class LinksPage(resource.Resource):
    isLeaf = True

    def __init__(self, links):
        resource.Resource.__init__(self)
        self.links = links

    def render(self, request):
        links_list_items = ['<li><a href="{0}">{1}</a></li>'.format(link, title) for link, title in self.links.iteritems()]
        return '<ul>{0}</ul>'.format(''.join(links_list_items))


def get_manhole_factory(namespace, **passwords):
    realm = manhole_ssh.TerminalRealm()

    def get_manhole(_):
        return manhole.Manhole(namespace)

    realm.chainedProtocolFactory.protocolFactory = get_manhole
    p = portal.Portal(realm)
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords)
    p.registerChecker(checker)
    return manhole_ssh.ConchFactory(p)


if __name__ == '__main__':
    links = {'blog': 'blog.syndbg.com',
             'github': 'github.com/syndbg',
             'python': 'python.org'}
    page = LinksPage(links)
    site = server.Site(page)
    reactor.listenTCP(8000, site)

    factory = get_manhole_factory(globals(), admin='aaa')
    reactor.listenTCP(2222, factory)
    reactor.run()
