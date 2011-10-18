from tornado.options import options

from libs.utils import autoadd_handlers

handlers = autoadd_handlers(options.project.service)
#handlers = []

from home import handlers as home_handlers
handlers.extend(home_handlers)
