from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from tornado.options import parse_command_line

import functools
import logging
import tornado.ioloop
import re
import urllib

class YelpWebClient:
  def request(self, path, callback, **args):
    all_args = {}
    all_args.update(args)
    url = 'http://www.yelp.com%s' % path

    if all_args:
      url = '%s?%s' % (url, urllib.urlencode(all_args))

    http = AsyncHTTPClient()
    logging.debug('making request to %s', url)
    http.fetch(url, callback = callback)

class YelpBookmarksClient(YelpWebClient):
  '''hacky schiiittt to get at user bookmarks. they must be public'''
  BIZ_LIST_RE = re.compile('''Yelp\.biz_list = *(\[.*?\]);\s*$''', re.M | re.S)

  def get_bookmarks(self, user_id, callback):
    '''callback is invoked with None or json bookmarks (and an error kwarg)'''
    # beware, THAR BE HACKS
    # yelp doesn't expose their bookmarks via the api, but we know it's available
    # via json in the html
    self.request('/user_details_bookmarks',
                 functools.partial(self._on_bookmarks, user_id, callback),
                 userid = user_id)

  def _on_bookmarks(self, user_id, callback, response):
    if response.error:
      logging.debug('Error response %s from yelp: %s', response.error, response.body)
      callback(None, error = (response.error, response.body))
      return

    # OH EM GEE
    match = YelpBookmarksClient.BIZ_LIST_RE.search(response.body)
    if match == None:
      logging.debug('No match, maybe user isn\'t public?')
      callback(None, error = (999, 'no bizlist, user might not be public?'))
      return

    biz_list = match.group(1)
    decoded = None
    try:
      decoded = json_decode(biz_list)
    except Exception as e:
      logging.error('unable to decode json: %s', e)
      callback(None, error = (999, 'unable to decode json'))
      return

    callback(decoded)



if __name__ == '__main__':
  parse_command_line()
  def _test_callback(barrier, user_id, bookmarks, error = None):
    if error:
      logging.warning('unable to get bookmarks for %s: %s' % (user_id, error))
    else:
      logging.warning('bookmarks for %s: %s' % (user_id, bookmarks))
    if barrier == 0:
      tornado.ioloop.IOLoop.instance().stop()

  user_ids = ['wZ46o0rz0IbF8dYenyQVbw', # dolapo
              'W46UkrAvPokkWfXno1cD6g'  # some girl
             ]
  # a lil test driver
  client = YelpBookmarksClient()
  for i, user_id in enumerate(user_ids):
    client.get_bookmarks(user_id,
                         functools.partial(_test_callback, len(user_ids) - 1 - i, user_id))
  tornado.ioloop.IOLoop.instance().start()
