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
from tornado.options import options

from utils import _json, _dict, SDict, timesince

class BaseHandler(tornado.web.RequestHandler):
    USER_AUTH_SIGN = 'user_id'
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
        """
        self.__class__ is BaseHandler (True)
        """
        if self.__class__._first_running:
            logging.info('First Running')
            self.__class__._first_running = False

        self._set_prepares()

    def _set_prepares(self):
        """Rewrite to re-implement prepares
        """
        self._prepares = (
            'libs.prepares.debug',
            'libs.prepares.web',
        )
    
    @property
    def db(self):
        return self.application.db

    # TODO dbs, databases` mapping dict

    # TODO cache

    # TODO mq

    @property
    def _json(self):
        return _json

    @property
    def _dict(self):
        return _dict

    def api_write(self, chunk, json=False):
        """Used globally, not special in ApiHandler
        """
        if isinstance(chunk, dict) or isinstance(chunk, list):
            chunk = self._json(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = escape.utf8(chunk)
        print 'Response:'
        print '    ', chunk
        if json:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(chunk)

    def api_error(self, code, text=None):
        """Used globally, not special in ApiHandler
        """
        # TODO show message on logging
        self.set_status(code)
        msg = {'code': code, 'error': text}
        print 'API ERROR: ', msg
        self.write(msg)
        self.finish()

    def get_arg(self, name):
        arg = self.get_argument(name, None)
        if arg is None:
            return self.api_error(400, 'Missing argument %s' % name)
        return arg

    def get_arg_dict(self, *args):
        if not hasattr(self, '_arg_dict'):
            self._arg_dict = {}
            for i in args:
                self._arg_dict[i] = self.get_arg(i)
        return self._arg_dict


    # TODO get_user_locale

    def get_auth_value(self, name, value, max_age_days=7):
        """Changed. user new function: tornado.web.RequestHandler.create_signed_value
        """
        return tornado.web.decode_signed_value(self.application.settings['auth_secret'],
                                               name, value, max_age_days=max_age_days)

    def set_auth_value(self, name, value, expires_days=7):
        """Written as set_secure_cookie works
        """
        auth_token = tornado.web.create_signed_value(self.application.settings['auth_secret'],
                                               name, value)
        self.set_header(options.secure.auth_header, auth_token)
        return auth_token

    def get_user_auth(self, auth_token):
        """
        return None or the string value
        """
        value = self.get_auth_value(self.USER_AUTH_SIGN, auth_token)
        return value

    def set_user_auth(self, user, cookie=False):
        auth_token = self.set_auth_value(self.USER_AUTH_SIGN, str(user.id))
        self.set_header(options.secure.auth_header, auth_token)
        if cookie:
            self.set_cookie(options.secure.cookie_name, auth_token)
        return auth_token

    def prepare(self):
        """
        like a middleware between raw request and handling process,
        """
        for i in self._prepares:
            positions = i.split('.')
            _name = positions.pop(-1)
            _module = __import__('.'.join(positions), globals(), locals(), [_name, ])
            exec('fn = _module.%s' %_name)
            #fn = __import__(i)
            fn(self)
            if self._finished: return


class ApiHandler(BaseHandler):
    JSON_DATA_KEY = 'data'

    @property
    def request_json(self):
        if not hasattr(self, '_cached_request_json'):
            try:
                self._cached_request_json = self._dict(
                        self.get_argument(self.JSON_DATA_KEY))
            except:
                return self.api_error(400, 'caching request data error')
        return self._cached_request_json

class WebHandler(BaseHandler):
    def web_error(self, code, msg=None):
        pass

    def render_string(self, template_name, **kwargs):
        assert "base_context" not in kwargs, "context is a reserved keyword."
        kwargs["base_context"] = self._base_context
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    @property
    def next_url(self):
        next_url = self.get_argument("next", None)
        return next_url or '/'


def api_authenticated(method):
    """Copy from tornado.web.authenticated.

    no need to use in ApiAuthedHandler
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urllib.urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

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
