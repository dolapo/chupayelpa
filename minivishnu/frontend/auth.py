from tornado.auth import OAuth2Mixin
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient

import json
import logging
import urllib

from tornado.options import options, define

class FoursquareMixin(OAuth2Mixin):
  _OAUTH_AUTHORIZE_URL = 'https://foursquare.com/oauth2/authenticate?'
  _OAUTH_ACCESS_TOKEN_URL = 'https://foursquare.com/oauth2/access_token?'
  def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                             code, callback):
    url = self._oauth_request_token_url(redirect_uri = redirect_uri,
                                        code = code,
                                        client_id = client_id,
                                        client_secret = client_secret,
                                        extra_params = {'grant_type': 'authorization_code'})
    logging.debug('making oauth access token request to %s' % url)
    http = AsyncHTTPClient()
    http.fetch(url, self.async_callback(self._on_access_token, callback))

  def _on_access_token(self, callback, response):
    logging.debug('response from foursquare: %s' % response)
    if response.error:
      logging.warning('foursquare auth error: %s' % str(response))
      callback(None)
    else:
      access_token = json.loads(response.body)['access_token']
      logging.debug('haz access token %s, getting user info', access_token)
      self.foursquare_request(
        '/users/self',
        self.async_callback(self._on_get_user_info, access_token, callback),
        access_token)

  def _on_get_user_info(self, access_token, callback, response):
    if response is None:
      logging.warning('awww, couldn\'t get user info')
      callback(None)
    else:
      logging.debug('response retreived: %s' % response)
      user = response['response']['user']
      user['access_token'] = access_token
      callback(user)

  def foursquare_request(self, path, callback, access_token, post_args = None, **args):
    '''use post_args to make this a post, otherwise use args'''
    all_args = {'oauth_token': access_token}

    all_args.update(args)
    url = 'https://api.foursquare.com/v2%s?%s' % (path, urllib.urlencode(all_args))

    callback = self.async_callback(self._on_foursquare_request, callback)
    http = AsyncHTTPClient()
    if post_args is not None:
      http.fetch(url, method = 'POST', body = urllib.urlencode(post_args),
                 callback = callback, connect_timeout = 30.0, request_timeout = 30.0)
    else:
      http.fetch(url, callback = callback)

  def _on_foursquare_request(self, callback, response):
    if response.error:
      logging.warning('Error response %s from foursquare on %s: %s',
                      response.error, response.request.url, response.body)
      callback(None)
    else:
      callback(json_decode(response.body))
