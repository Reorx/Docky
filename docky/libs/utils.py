import os
import sys
import datetime

import simplejson as pyjson

from tornado.options import parse_command_line

class SDict(dict):
    """
    flexiblely set & get key-value
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError

from bson.objectid import ObjectId
from mongoengine import Document
from mongoengine.queryset import QuerySet
class CustomJSONEncoder(pyjson.JSONEncoder):
    """
    copy from django.core.serializers.json
    """
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def resolve_iterable(self, o):
        print 'resolving ', o, o.__class__
        return o

    def default(self, o):
        if isinstance(o, QuerySet):
            print 'is QuerySet'
            return [i for i in o]
        
        elif issubclass(o.__class__, Document):
            print 'is Document'
            d = {}
            for i in o: d[i] = getattr(o, i)
            return d

        elif isinstance(o, ObjectId):
            return o.__str__()

        elif isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        else:
            return super(CustomJSONEncoder, self).default(o)

def _dict(json):
    return pyjson.loads(json, encoding='utf-8')

def _json(dic):
    return pyjson.dumps(dic, ensure_ascii=False, cls=CustomJSONEncoder)

def timesince(time):
    if not isinstance(time, datetime.datetime):
        return None
    now = datetime.datetime.utcnow()
    delta = now - time
    if not delta.days:
        if delta.seconds / 3600:
            return '{0} hours ago'.format(delta.seconds / 3600)
        return '{0} minutes ago'.format(delta.seconds / 60)
    if delta.days / 365:
        return '{0} years ago'.format(delta.days / 365)
    if delta.days / 30:
        return '{0} months ago'.format(delta.days / 30)
    return '{0} days ago'.format(delta.days)

#####################
#   project tools   #
#####################

from tornado.options import options

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.split(CURRENT_PATH)[0]
PARENT_PATH, PROJECT_NAME = os.path.split(PROJECT_PATH)


def autoload_submodules(dirpath):
    """Load submodules by dirpath
    NOTE. ignore packages
    """
    import pkgutil
    importer = pkgutil.get_importer(dirpath)
    return (importer.find_module(name).load_module(name)\
            for name, is_pkg in importer.iter_modules())

def autoadd_handlers(dirname):
    handlers = []
    dirpath = os.path.join(PROJECT_PATH, dirname)
    for i in autoload_submodules(dirpath):
        handlers.extend(i.handlers)
    return handlers

def simplep(s, color):
    colortag = '%s'
    if 'red' == color:
        colortag = '\033[1;31m%s\033[1;m'
    elif 'green' == color:
        colortag = '\033[1;32m%s\033[1;m'
    elif 'blue' == color:
        colortag = '\033[1;34m%s\033[1;m'
    else:
        pass
    print colortag % s

def parse_cfg_file(cfgname=None):
    """Use (?) standard .cfg syntax configuraion
    file name default to be `settings.cfg`
    """
    import ConfigParser
    from tornado.options import define as define_option

    if cfgname is None: cfgname = 'settings.cfg'

    path = os.path.join(PROJECT_PATH, cfgname)
    if not os.path.isfile(path):
        raise IOError('settings.cfg file does not exist, check if it has been copied from .dev or .product')
    with open(path, 'r') as f:
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(f)
    for i in cfg.sections():
        o = SDict()
        for k, v in cfg.items(i):
            # convert v type by its figure
            if 'True' == v: v = True
            elif 'False' == v: v = False
            elif 'None' == v: v = None
            else:
                INTCHAR = '0123456789'
                is_int = True
                for char in v:
                    if not char in INTCHAR: is_int = False
                if is_int:
                    v = int(v)
                    if v > 65535: v = str(v)

            o[k] = v
        if i in options:
            options[i].set(o)
        else:
            define_option(i, o)

def load_project():
    """
    facilities:
        1. make project package as importable (parent dir in sys.path)
        2. load settings.cfg into options
    """
    try:
        #import nodemix
        __import__(PROJECT_NAME)
    except ImportError:
        sys.path.append(PARENT_PATH)
        #import nodemix
        __import__(PROJECT_NAME)
    sys.path.append(os.path.join(PROJECT_PATH))
    sys.path.append(os.path.join(PROJECT_PATH, 'third'))

    # load cfg file
    parse_cfg_file()

def resolve_input():
    """
    called after most things in models have been imported
    """
    try:
        arg1 = sys.argv[1]
    except:
        simplep('Please Input First Arg', 'red')
        sys.exit()

    if 'syncdb' == arg1:
        simplep('creating database table structure..', 'blue')
        db.Model.metadata.create_all(db.engine)
        simplep('done', 'blue')
    elif 'reset' == arg1:
        try:
            arg2 = sys.argv[2]
        except:
            simplep('Please Input Secode Arg', 'red')
            sys.exit()
        if 'all' == arg2:
            db.Model.metadata.drop_all(db.engine)
            db.Model.metadata.create_all(db.engine)
        else:
            try:
                # TODO import hook..
                #_module = __import__('models.'+arg2, globals(), locals())
                _module = globals()[arg2]
            except KeyError as e:
                simplep(e.message + ' Not Exist', 'red')
                sys.exit()
            simplep('drop & recreate table', 'blue')
            _module.__table__.drop(bind=db.engine)
            _module.__table__.create(bind=db.engine)
            simplep('done', 'blue')
    elif 'backupdb' == arg1:
        arg2 = sys.argv[2]
        #os.chdir(arg3)
        fopt = options.sqlalchemy
        fopt['output'] = arg2
        cmd_elements = ('mysqldump -C -f --host={host} --user={username} --password={password}' +\
                ' --result-file={output} {database}').format(**fopt)
        print cmd_elements
        os.system(cmd_elements)
        import gzip
        print fopt.output+'.gz'
        with open(fopt.output, 'r') as f:
            gz = gzip.open(fopt.output+'.gz', 'w')
            gz.writelines(f)
            gz.close()
        pass
    else:
        simplep('I Don`t Konw This Instruction', 'red')

def generate_cookie_secret():
    import uuid
    import base64
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

if '__main__' == __name__:
    load_project()

    from models import *
    resolve_input()
