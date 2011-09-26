#coding=utf8

from docky.core.handlers import WebHandler, WebAuthHandler

from models import Doc, DocResource, DocEntry

class DocsHdr(WebHandler):
    def get(self):
        c = {}
        c['docs'] = Doc.query.all()
        self.render('docs.html', **c)

    def post(self):
        doc = Doc(name=self.get_argument('name'),
                  description=self.get_argument('description'))
        doc.save()
        return self.redirect('/docs')

class DocsShowHdr(WebHandler):
    def get(self, doc_name=None):
        c = {}
        d = Doc.query.filter_by(name=doc_name).one()
        c['doc'] = d
        #print dir(d)
        c['doc_entries'] = d.get_entries()
        c['doc_resources'] = d.get_resources()
        self.render('docs_show.html', **c)

class DocsUpdateHdr(WebHandler):
    def get(self):
        pass

class DocsEntriesHdr(WebHandler):
    def get(self):
        pass

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

class DocsEntriesShowHdr(WebHandler):
    def get(self, doc_name=None, identifier=None):
        d = Doc.query.filter_by(name=doc_name).one()
        print d, dir(d)
        e = d.get_entry(identifier)
        c = {
            'entry': e
        }
        return self.render('entries_show.html', **c)

class DocsEntriesUpdateHdr(WebHandler):
    def post(self):
        pass

handlers = [
    (r'/docs', DocsHdr), # GET, POST, DELETE
    (r'/docs/(?P<doc_name>\w+)', DocsShowHdr), # GET
    (r'/docs/(?P<doc_name>\w+)/update', DocsUpdateHdr), # GET, POST

    (r'/docs/(?P<doc_name>\w+)/entries', DocsEntriesHdr), # GET, POST, DELETE
    (r'/docs/(?P<doc_name>\w+)/entries/(?P<identifier>.*)', DocsEntriesShowHdr), # GET
    (r'/docs/(?P<doc_name>\w+)/entries/(?P<identifier>.*)/update', DocsEntriesUpdateHdr), # GET, POST
]
