#!/usr/bin/python2.7
import os

import tornado.options
import tornado.ioloop
import tornado.web
import tornado.httpserver

import config

def load_package():
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    try:
        import docky
    except ImportError:
        import sys
        sys.path.append(os.path.join(ROOT_PATH, '..'))
        import docky

class Application(tornado.web.Application):
    def __init__(self):
        from urls import handlers

        settings = dict(
            debug = config.debug,
            autoescape = None,
            cookie_secret = config.auth_secret,
            auth_secret = config.auth_secret,
            template_path = config.template_path,
            static_path = config.static_path,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        # TODO approach db & cache system.

        from models import db, mongodb

        Application.db = db.session
        Application.mongodb = mongodb.session

def run():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())

    # multi-process control way
    #http_server.bind(config.port)
    #http_server.start(config.processes)

    http_server.listen(config.port)
    tornado.ioloop.IOLoop.instance().start()

if '__main__' == __name__:
    load_package()
    run()
