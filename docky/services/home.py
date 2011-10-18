from libs.handlers import WebHandler

class HomeHandler(WebHandler):
    def get(self):
        self.render('home.html')

handlers = [
    (r'/', HomeHandler),
]
