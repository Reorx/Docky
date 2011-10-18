import datetime

from tornado.options import options

from utils import SDict

def debug(hdr, full=False):
    """
    in sequence 1
    """
    print 'Request'
    print '    header:'
    if full:
        for k, v in hdr.request.headers.iteritems():
            print '        %s%s%s' % (k, (22-len(k))*' ', v[:100])
    else:
        k = options.secure.mobile_header; v = hdr.request.headers.get(k, '')
        print '        %s%s%s' % (k, (22-len(k))*' ', v[:100])
        k = options.secure.auth_header; v = hdr.request.headers.get(k, '')
        print '        %s%s%s' % (k, (22-len(k))*' ', v[:100])
    print '    body:'
    for k, v in hdr.request.arguments.iteritems():
        print '        %s%s%s' % (k, (22-len(k))*' ', v[0][:3000])

def params(hdr):
    """Define tuple::`param_requirements` at the top of handler class
    """
    requirements = [] # actually is tuple
    def check_params():
        for i in requirements:
            if not i in hdr.request.arguments:
                return hdr.api_error(403, 'Param Lost')

    if hasattr(hdr, 'GET_PARAMS') and hdr.request.method == 'GET':
        requirements = hdr.GET_PARAMS
        check_params()
    elif hasattr(hdr, 'POST_PARAMS') and hdr.request.method == 'POST':
        requirements = hdr.POST_PARAMS
        check_params()
    elif hasattr(hdr, 'PUT_PARAMS') and hdr.request.method == 'PUT':
        requirements = hdr.PUT_PARAMS
        check_params()
    elif hasattr(hdr, 'DELETE_PARAMS') and hdr.request.method == 'DELETE':
        requirements = hdr.DELETE_PARAMS
        check_params()
    else:
        pass

def web(hdr):
    hdr._base_context = SDict()
    hdr._base_context.now = datetime.datetime.now()
    hdr._base_context.now_formated = lambda x: hdr._base_context.now.strftime(x)
    hdr._base_context.user = None

def user_agent(hdr):
    pass

def auth(hdr):
    """Overwrite this function to involving authtication
    """
    pass
