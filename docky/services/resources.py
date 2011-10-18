#coding=utf8

from docky.libs.handlers import WebHandler

from models import *


class ProjectEntriesHdr(WebHandler):
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
        buf = Resource.query(method=data['method'],
                             url=data['url'])
        if buf:
            return self.api_error(401, 'y')

        _id = Resource.safeinsert(data)
        return self.write('ok')

class ProjectEntriesShowHdr(WebHandler):
    def get(self, doc_name=None, identifier=None):
        d = Project.query.filter_by(name=doc_name).one()
        print d, dir(d)
        e = d.get_entry(identifier)
        c = {
            'entry': e
        }
        return self.render('resource.html', **c)

class ProjectEntriesUpdateHdr(WebHandler):
    def post(self):
        pass

handlers = [
    (r'/projects/(?P<doc_name>\w+)/entries', ProjectEntriesHdr), # GET, POST, DELETE
    (r'/projects/(?P<doc_name>\w+)/entries/(?P<identifier>.*)', ProjectEntriesShowHdr), # GET
    (r'/projects/(?P<doc_name>\w+)/entries/(?P<identifier>.*)/update', ProjectEntriesUpdateHdr), # GET, POST
]
