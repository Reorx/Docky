import urllib
import urllib2

from Cookie import BaseCookie

from json import _json, _dic

class RPCResponseError(Exception):
    def __str__(self):
        return 'Fail to get response from rpc.py'

class ServerProxy(object):
    BASIC_HEADER = {'User-Agent': 'NodeMix-Benchmark/1.0'}
    LOGIN_URL = '/api/user/login'
    SESSION_COOKIE_NAME = 'sessionid' # TODO sesson mechanism

    def __init__(self, domain, port=None,
        auth_token=None, imei=None):
        if '/' == domain[-1:]:
            raise ValueError
        self._domain = domain # suffix without '/'
        if port:
            self._port_s = ':' + str(port)
        else:
            self._port_s = ''
        if auth_token:
            self._authed = False
            self._auth_token = auth_token
        else:
            self._authed = False
        self._imei = imei

    def _fetch(self, req):
        req.add_header('PNMM-IMEI', self._imei)
        if self._authed:
            req.add_header('Cookie', '%s=%s' % (self.SESSION_COOKIE_NAME, self._auth_token))

        resp = urllib2.urlopen(req) # debug has been turned to Django, no need here

        if 200 != resp.code:
            print 'rpc response: ', resp.code, resp.msg
            raise RPCResponseError

        return resp

    def login(self, email, password):
        if self._authed:
            return self._auth_token

        data = {'email': email, 'password': password}
        data_s = 'json=' + _json(data)
        call_url = 'http://%s%s%s' % (self._domain, self._port_s, self.LOGIN_URL)
        req = urllib2.Request(url=call_url, data=data_s, headers=self.BASIC_HEADER)
        resp = self._fetch(req)

        try:
            cookie = BaseCookie(resp.headers['set-cookie'])
        except KeyError:
            cookie = BaseCookie(resp.headers['Set-Cookie'])

        self._auth_token = cookie[self.SESSION_COOKIE_NAME].value
        self._authed = True
        self.user = _dic(resp.read())

        print 'self._auth_token: ', self._auth_token
        return self._auth_token

    def logout(self):
        pass

    def get(self, url, query=None):
        """
        url: '/', '/foo/bar/'
        query: dict
        """
        #if '/' != url[-1:] or '/' != url[:1]:
            #raise ValueError
        if query:
            if not isinstance(query, dict):
                raise ValueError
            query_s = '?' + urllib.urlencode(query)
        else:
            query_s = ''

        call_url = 'http://%s%s%s%s' % (self._domain, self._port_s, url, query_s)
        req = urllib2.Request(url=call_url, headers=self.BASIC_HEADER)
        resp = self._fetch(req)

        return resp

    def post(self, url, data=None, raw=False):
        """
        data: dict
        """
        #if '/' != url[-1:] or '/' != url[:1]:
            #raise ValueError
        if data:
            data_s = urllib.urlencode(data)
        else:
            data_s = None

        call_url = 'http://%s%s%s' % (self._domain, self._port_s, url)
        print call_url

        req = urllib2.Request(url=call_url, data=data_s, headers=self.BASIC_HEADER)
        resp = self._fetch(req)

        return resp
