#!/usr/bin/python2.7
import os

import tornado.ioloop
import tornado.web
import tornado.httpserver

from tornado.options import options

from libs.utils import load_project, parse_command_line, autoadd_handlers

class Application(tornado.web.Application):
    def __init__(self):
        from docky.urls import handlers

        settings = dict(
            debug = options.default.debug,

            cookie_secret = options.secure.auth_secret,
            auth_secret = options.secure.auth_secret,

            template_path = options.web.template_path,
            #static_path = options.web.static_path,

            autoescape = None,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        # TODO approach db & cache system.

        #from models import db, mongodb

        Application.db = None

def run():
    http_server = tornado.httpserver.HTTPServer(Application())

    http_server.listen(options.get('port') or options.default.port)
    tornado.ioloop.IOLoop.instance().start()

if '__main__' == __name__:
    load_project()

    parse_command_line()

    run()
