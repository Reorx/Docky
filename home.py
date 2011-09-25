from core.handlers import WebHandler, WebAuthHandler

class HomeHandler(WebHandler):
    def get(self):
        self.render('home.html')

handlers = [
    (r'/', HomeHandler),
]
