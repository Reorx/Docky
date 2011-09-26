from docky.core.handlers import WebHandler, WebAuthHandler

from models import Doc, DocEntry

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

class DocsShowHandler(WebHandler):
    def get(self, doc_name=None):
        c = {}
        c['doc'] = Doc.query.filter_by(name=doc_name).one()
        c['doc']['entries'] = DocEntry.query(doc=doc_name)
        #c['doc']['resources'] = 
        self.render('docs_show.html', **c)

class DocsEntriesHandler(WebHandler):
    def get(self):
        pass

    def post(self):
        pass

class DocsEntriesShowHandler(WebHandler):
    def get(self, doc_name=None, identifier=None):
        pass

class EntriesHandler(WebHandler):
    """Must be checked at backend
    """
    def post(self):
        try:
            data = self._dict(self.get_argument('data'))
        except:
            print 'illegal'
            return self.api_error(400, 'w')
        # check attributes
        print 'data', data
        for i in data.keys():
            if not i in ('doc', 'resource', 'url', 'method', 'description',
                    'authentication_required', 'parameters', 'example'):
                print 'not all: ', i
                return self.api_error(400, 'x')
        # check dumplication
        buf = DocEntry.query(method=data['method'],
                             url=data['url'])
        if buf:
            return self.api_error(401, 'y')

        _id = DocEntry.safeinsert(data)
        return self.write('ok')

class EntriesShowHandler(WebHandler):
    def get(self, identifier):
        try:
            buf = identifier.split('|')
            e_method = buf[0]
            e_url = buf[1]
        except:
            return self.api_error(400, 'b r')
        try:
            e = DocEntry.query(method=e_method,
                               url=e_url)[0]
        except:
            return self.api_error(404, 'n f')
        c = {
            'entry': e
        }
        return self.render('entry.html', **c)

handlers = [
    (r'/docs', DocsHandler),
    (r'/docs/(?P<doc_name>\w+)', DocsShowHandler),
    (r'/docs/(?P<doc_name>\w+)/entries', DocsEntriesHandler),
    (r'/docs/(?P<doc_name>\w+)/entries/(?P<identifier>.*)', DocsEntriesShowHandler),
]
