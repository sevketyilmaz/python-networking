from twisted.application import internet, service
from chat import ChatFactory


application = service.Application('chat')
chatService = internet.TCPServer(8000, ChatFactory())
chatService.setServiceParent(application)
