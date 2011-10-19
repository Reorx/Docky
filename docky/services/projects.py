from docky.libs.handlers import WebHandler

from models import *

#class ProjectsHandler()
def asure_project(hdr, name):
    p = Project.objects(name=name).first()
    if not p:
        hdr.api_error(404, 'Not Found')
        return
    return p

class ProjectsHdr(WebHandler):
    def get(self):
        _i = lambda x: {'id': x.id, 'name': x.name}
        data = [_i(i) for i in Project.objects]

        self.api_write(data)

        #a = Project.objects[0]
        #for i in a:
            #print i
        #self.render('projects.html', **c)
        #self.api_write(data)

    def post(self):
        p = Project(name=self.get_arg('name'),
                  description=self.get_arg('description'))

        exs = Project.objects(name=p.name)
        if exs:
            return self.api_error(400, 'name conflict')
        p.save()
        return self.redirect('/projects')

class ProjectsShowHdr(WebHandler):
    def get(self, name=None):
        p = asure_project(self, name)
        if not p: return

        self.api_write(self._json(p), json=True)

class ProjectsUpdateHdr(WebHandler):
    def post(self, name=None):
        p = asure_project(self, name)
        if not p: return

        udict = self.get_arg_dict('name', 'description')
        p.update(**udict)
        # NOTE could not understand why id will be changed after calling .update
        # as to .save, there's no such problem

class ProjectsSectionHdr(WebHandler):
    def post(self, name=None):
        p = asure_project(self, name)
        if not p: return

        section = Section(**self.get_arg_dict('name', 'description'))
        section.save()
        p.sections.append(section)
        result = p.save()

class ProjectsResourcesHdr(WebHandler):
    def get(self, name=None):
        p = asure_project(self, name)
        if not p: return

        data = []
        for i in p.sections:
            s = {
                'name': i.name,
                'sequence': 0, # TODO
                'resources': i.resources,
            }
            data.append(s)

        return self.api_write(data)

handlers = [
    (r'/projects', ProjectsHdr), # GET, POST, DELETE
    (r'/projects/name:(?P<name>[\w\s]+)', ProjectsShowHdr), # GET
    (r'/projects/name:(?P<name>[\w\s]+)/update', ProjectsUpdateHdr), # GET, POST

    (r'/projects/name:(?P<name>[\w\s]+)/sections', ProjectsSectionHdr), # GET, POST
    (r'/projects/name:(?P<name>[\w\s]+)/rs', ProjectsResourcesHdr), # GET, POST

]
