from minivishnu.frontend.auth import FoursquareMixin
from tornado import template
from tornado.escape import json_encode, json_decode
from tornado.options import options, define, parse_command_line
from tornado.web import Application, RequestHandler, url

import json
import logging
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web

define('port', type = int, default = 9009)
define('debug', type = bool, default = False)


# Required
define('base_url', type = str, default = None)
define('foursquare_client_id', type = str, default = None)
define('foursquare_client_secret', type = str, default = None)


class BaseHandler(RequestHandler):
  def get_current_user(self):
    user_cookie = self.get_secure_cookie('user')
    if user_cookie:
      return json_decode(user_cookie)
    else:
      None

class RootHandler(BaseHandler, FoursquareMixin):
  @tornado.web.asynchronous
  def get(self):
    self.render('index.html',
                user = self.get_current_user())

class OAuthLoginHandler(BaseHandler, FoursquareMixin):
  URI = '/auth/foursquare'

  @tornado.web.asynchronous
  def get(self):
    if self.get_argument('code', False):
      self.get_authenticated_user(
        redirect_uri = options.base_url + OAuthLoginHandler.URI,
        client_id = options.foursquare_client_id,
        client_secret = options.foursquare_client_secret,
        code = self.get_argument('code'),
        callback = self.async_callback(self._on_auth))
    else:
      self.authorize_redirect(redirect_uri = options.base_url + OAuthLoginHandler.URI,
                              client_id = options.foursquare_client_id,
                              extra_params = {'response_type': 'code'})

  def _on_auth(self, user):
    logging.debug('oauth callback, user: %s' % user)
    if not user:
      self.render('error.html',
                  error = 'oauth_token provided, but unable to authenticate')
    else:
      self.set_secure_cookie('user', json_encode(user))
      self.redirect('/')

def main():
  parse_command_line()
  template_path = os.path.join(os.path.dirname(__file__), 'templates')
  static_path = os.path.join(os.path.dirname(__file__), 'static')
  template_loader_factory = lambda: template.Loader(template_path)

  handlers = [
    url(r'/$', RootHandler),
    url(r'%s$' % OAuthLoginHandler.URI, OAuthLoginHandler)
  ]

  app = Application(
    handlers,
    debug = options.debug,
    xsrf_cookies = True,
    cookie_secret = 'deadb33fd00dc9234adeda42777',
    template_path = template_path,
    static_path = static_path
  )

  logging.info('starting on port %d' % options.port)
  server = tornado.httpserver.HTTPServer(app)
  server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  main()
