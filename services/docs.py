from docky.core.handlers import WebHandler, WebAuthHandler

from models import Doc

class DocsHandler(WebHandler):
    def get(self):
        c = {}
        c['docs'] = Doc.query.all()
        self.render('docs.html', **c)

    def post(self):
        doc = Doc(name=self.get_argument('name'),
                  description=self.get_argument('description'))
        doc.save()
        return self.redirect('/docs')

handlers = [
    (r'/docs', DocsHandler),
]
