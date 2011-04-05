from minivishnu.frontend.auth import FoursquareMixin
from minivishnu.yelp import YelpBookmarksClient
from tornado import template
from tornado.escape import json_encode, json_decode, url_escape
from tornado.options import options, define, parse_command_line
from tornado.web import Application, RequestHandler, url
from tornado.httpclient import AsyncHTTPClient

import functools
import json
import logging
import memcache
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web
import urllib

define('port', type = int, default = 9009)
define('debug', type = bool, default = False)


# Required
define('base_url', type = str, default = None)
define('foursquare_client_id', type = str, default = None)
define('foursquare_client_secret', type = str, default = None)
define('memcache_host', type = str, default = None)

class BaseHandler(RequestHandler):
  def __init__(self, application, request):
    super(BaseHandler, self).__init__(application, request)
    self.memcache_client = application.settings['memcache_client']

  def get_current_user(self):
    user_cookie = self.get_secure_cookie('user')
    if user_cookie:
      return json_decode(user_cookie)
    else:
      None

  def memcache_key_bookmarks(self, yelpId):
    return str('mv/chupayelpa/yelpbookmarks/%s/v2' % yelpId)

  def memcache_key_yelpid(self, userId):
    return str('mv/chupayelpa/user/%s/yelpId/v0' % userId)

class RootHandler(BaseHandler, FoursquareMixin):
  @tornado.web.asynchronous
  def get(self):
    yelpId = None
    yelpBookmarks = None
    user = self.get_current_user()
    if user:
      yelpId = self.memcache_client.get(self.memcache_key_yelpid(user['id']))
      logging.debug('yelp id in cache: %s' % yelpId)
      yelpBookmarks = self.memcache_client.get(
        self.memcache_key_bookmarks(yelpId))
      if yelpBookmarks:
        yelpBookmarks = json_decode(yelpBookmarks)
      else:
        logging.warning('bookmarks not in cache, reseting id')
        yelpId = None

    self.render('index.html',
                user = user,
                yelpError = self.get_argument('yelp_error', None),
                yelpId = yelpId,
                yelpBookmarks = yelpBookmarks)

class LogoutHandler(BaseHandler):
  def get(self):
    user = self.get_current_user()
    if user:
      yelpId = self.memcache_client.get(self.memcache_key_yelpid(user['id']))
      if yelpId:
        self.memcache_client.delete_multi([self.memcache_key_yelpid(user['id']),
                                           self.memcache_key_bookmarks(yelpId)])
      self.clear_all_cookies()
    self.redirect('/')


class SubmitYelpHandler(BaseHandler):
  # This is kind of nasty but i don't want to deal with ajax just yet.
  @tornado.web.asynchronous
  def post(self):
    yelpId = self.get_argument('yelpid', None)
    if not yelpId:
      self.redirect('/')
      return
    yelpClient = YelpBookmarksClient()
    yelpClient.get_bookmarks(yelpId,
                             functools.partial(self._on_yelp_response, yelpId))

  def _on_yelp_response(self, yelpId, bookmarks, error = None):
    if error:
      logging.warning('aww, yelp error')
      self.redirect('/?yelp_error=%s' % str(error))
    else:
      logging.debug('yelp looks good, saving info')
      user = self.get_current_user()
      # TODO(dolapo): may need to zip this
      self.memcache_client.set(self.memcache_key_bookmarks(yelpId),
                               json_encode(bookmarks), 0)
      self.memcache_client.set(self.memcache_key_yelpid(user['id']), yelpId, 0)
      self.redirect('/')

class MatchVenuesHandler(BaseHandler, FoursquareMixin):
  @tornado.web.asynchronous
  def get(self):
    user = self.get_current_user()
    bookmarks = self.get_argument('bookmarks', None)
    if not user or not bookmarks:
      self.send_error(400)
      return

    bookmarks = json_decode(bookmarks)

    def make_req(bookmark):
      req_args = {
        'll': '%.8f,%.8f' % (bookmark['latitude'], bookmark['longitude']),
        'llAcc': '1000',
        'intent': 'match',
        'query': url_escape(bookmark['name']),
        # boo
        #'url': 'http://yelp.com/biz/%s' % bookmark['id']
        'providerId': 'yelp'
      }
      return '/venues/search?%s' % urllib.urlencode(req_args)

    self.foursquare_request(
      '/multi',
      functools.partial(self._on_multi, bookmarks),
      user['access_token'],
      requests = ','.join([make_req(b) for b in bookmarks]))

  def _on_multi(self, bookmarks, lresponse):
    results = {}
    for (bookmark, outerresponse) in zip(bookmarks, lresponse['response']['responses']):
      response = outerresponse['response']
      # TODO(dolapo): may not exist
      if (response.get('groups') == None):
        logging.error('OH OH, what is: %s' % lresponse)
      groups = response.get('groups', [])
      for group in groups:
        results[bookmark['id']] = group['items']
    self.finish({'results': results})

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
  client = AsyncHTTPClient(max_clients = 100)
  template_path = os.path.join(os.path.dirname(__file__), 'templates')
  static_path = os.path.join(os.path.dirname(__file__), 'static')
  template_loader_factory = lambda: template.Loader(template_path)

  handlers = [
    url(r'/$', RootHandler),
    url(r'/logout$', LogoutHandler),
    url(r'/submityelp$', SubmitYelpHandler),
    url(r'/matchvenues$', MatchVenuesHandler),
    url(r'%s$' % OAuthLoginHandler.URI, OAuthLoginHandler)
  ]

  app = Application(
    handlers,
    debug = options.debug,
    xsrf_cookies = False, # TODO
    cookie_secret = 'deadb33fd00dc9234adeda42777',
    template_path = template_path,
    static_path = static_path,
    memcache_client = memcache.Client([options.memcache_host], debug = 0),
    httpclient = client
  )

  logging.info('starting on port %d' % options.port)
  server = tornado.httpserver.HTTPServer(app)
  server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  main()
