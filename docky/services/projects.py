from docky.libs.handlers import WebHandler

from models import *

class ProjectsHdr(WebHandler):
    def get(self):
        c = {
            'projects': [],
        }
        data = [i._data for i in Project.objects]

        self.api_write(self._json(Project.objects), json=True)

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
        data = Project.objects(name=name).first()

        self.api_write(self._json(data), json=True)

class ProjectsUpdateHdr(WebHandler):
    def post(self, name=None):
        p = Project.objects(name=name).first()
        if not p:
            return self.api_error(404, 'Not Found')
        udict = self.get_arg_dict('name', 'description')
        p.update(**udict)
        # NOTE could not understand why id will be changed after calling .update
        # as to .save, there's no such problem

handlers = [
    (r'/projects', ProjectsHdr), # GET, POST, DELETE
    (r'/projects/name:(?P<name>[\w\s]+)', ProjectsShowHdr), # GET
    (r'/projects/name:(?P<name>[\w\s]+)/update', ProjectsUpdateHdr), # GET, POST

]
