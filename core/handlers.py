#coding=utf8

"""
core concepts:
    * client
        name collection, could be mobile or browser

    * browser
        one in client

    * mobile
        one in client

    * web
        request send by a browser called web request

    * api
        request send by a mobile called api request
"""

import re
import os
import time
import base64
import logging
import datetime
import urllib
import urlparse
import functools

import tornado.web
import tornado.locale

from tornado.web import HTTPError
from tornado.web import authenticated as web_authenticated
from tornado import escape
from tornado.util import b

from nodemix.models import User
from nodemix.core.utils import _json, _dict, SDict, timesince

import config

class BaseHandler(tornado.web.RequestHandler):
    """
    Request
        header:
        body:

    Response
        status code: 200(成功), 400(参数异常), 403(不成功), 404(web,未找到), 500(服务器异常)
        header:
        body:
    """
    _first_running = True
    def initialize(self):
        if BaseHandler._first_running:
            logging.info('First Running')
            BaseHandler._first_running = False
    
    @property
    def db(self):
        return self.application.db

    @property
    def mongodb(self):
        return self.application.mongodb

    # TODO cache

    @property
    def _json(self):
        return _json

    @property
    def _dict(self):
        return _dict

    def get_user_locale(self):
        if self.current_user:
            return tornado.locale.get(self.current_user.locale)
        return None

    def _prepare_debug(self):
        """
        in sequence 1
        """
        print 'Request'
        print '    header:'
        for k, v in self.request.headers.iteritems():
            print '        %s%s%s' % (k, (22-len(k))*' ', v[:100])
        print '    body:'
        for k, v in self.request.arguments.iteritems():
            print '        %s%s%s' % (k, (22-len(k))*' ', v[0][:100])

    def _prepare_auth(self):
        """
        in sequence 3
        """
        pass

    def _prepare_params(self):
        """Define tuple::`param_requirements` at the top of handler class
        """
        requirements = [] # actually is tuple
        def check_params():
            for i in requirements:
                if not i in self.request.arguments:
                    return self.api_error(403, 'Param Lost')

        if hasattr(self, 'GET_PARAMS') and self.request.method == 'GET':
            requirements = self.GET_PARAMS
            check_params()
        elif hasattr(self, 'POST_PARAMS') and self.request.method == 'POST':
            requirements = self.POST_PARAMS
            check_params()
        elif hasattr(self, 'PUT_PARAMS') and self.request.method == 'PUT':
            requirements = self.PUT_PARAMS
            check_params()
        elif hasattr(self, 'DELETE_PARAMS') and self.request.method == 'DELETE':
            requirements = self.DELETE_PARAMS
            check_params()
        else:
            pass

    def _prepare_web(self):
        pass

    def _prepare_others(self):
        pass

    def prepare(self):
        """
        watch out _prepare* functions' sequence 
        NOTE: WITHOUT JUDGING self._finished THERE WILL BE BIG PROBLEMS
        """
        self._prepare_debug()
        if self._finished: return

        self._prepare_auth()
        if self._finished: return

        self._prepare_params()
        if self._finished: return

        self._prepare_web()
        if self._finished: return

        self._prepare_others()
        if self._finished: return

class WebHandler(BaseHandler):
    def web_error(self, code, msg=None):
        pass

    def _prepare_web(self):
        self._base_context = SDict()
        self._base_context.now = datetime.datetime.now()
        self._base_context.now_formated = lambda x: self._base_context.now.strftime(x)
        self._base_context.user = None

    def render_string(self, template_name, **kwargs):
        assert "base_context" not in kwargs, "context is a reserved keyword."
        kwargs["base_context"] = self._base_context
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    @property
    def next_url(self):
        next_url = self.get_argument("next", None)
        return next_url or '/'

class WebAuthHandler(WebHandler):
    def _prepare_auth(self):
        user_id = self.get_secure_cookie(config.web_auth_key)
        if user_id:
            user = User.query.get(user_id)
            if user:
                self.user = user
                return

        return self.web_error(403, 'Authentication Failed')

class check_request:
    def __init__(self, *args):
        self.fields = args

    def __call__(self, fn, *args, **kwargs):
        def _wrapper(hdr, *args, **kwargs):
            params = hdr.request.arguments
            for i in self.fields:
                if not i in params:
                    #raise KeyError('lose param')
                    return hdr.send_error(status_code=400)

            return fn(hdr, *args, **kwargs)
        return _wrapper
