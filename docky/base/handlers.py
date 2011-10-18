
class ApiAuthedHandler(ApiHandler):
    """
    require both IMEI identify and auth
    NOTE: add new attribute `user` to the handler
    """
    def _prepare_auth(self):
        value = self.request.headers.get(options.secure.auth_header)
        if value:
            user_id = self.get_auth_value('user_id', value)
            if user_id:
                user = User.query.get(user_id)
                if user:
                    self.user = user
                    # after user has been authed,
                    # try to get his mobile by imei,
                    # if mobile not exist, create it.
                    self.user.using(self._mobile.imei)
                    return

        return self.api_error(401, 'Authentication Failed')

class WebAuthedHandler(WebHandler):

    def authed_render(self, tmpl_name, context, cookie_value=None):
        if not cookie_value:
            self.set_cookie('sessionid', self._auth_token)
        return self.render(tmpl_name, **context)

    def authed_redirect(self, url, cookie_value=None):
        if not cookie_value:
            self.set_cookie('sessionid', self._auth_token)
        return self.redirect(url)

    def _prepare_auth(self):
        """
        first sequence, verify `sessionid` in url
        second is cookie auth
        """
        value = self.get_argument(options.secure.cookie_name, None) or \
                self.get_cookie(options.secure.cookie_name, None)
        if value:
            user_id = self.get_auth_value('user_id', value)
            if user_id:
                user = User.query.get(user_id)
                if user:
                    self.user = user
                    # signed attribute _auth_token
                    self._auth_token = value
                    return

        self.write('403 Authentication Failed')
        return self.finish()
