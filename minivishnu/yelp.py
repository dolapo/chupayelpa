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
    results = []
    self._make_request(user_id, results, callback)

  def _make_request(self, user_id, results, callback, page = 0):
    logging.debug('making request, page = %d, current num results = %s', page, len(results))
    args = {'userid': user_id}
    if page > 0:
      args['start'] = page * 50

    self.request('/user_details_bookmarks',
                 functools.partial(self._on_bookmarks, user_id, results, callback, page),
                 **args)

  def _on_bookmarks(self, user_id, results, callback, page, response):
    if response.error:
      if len(results) == 0:
        logging.debug('Error response %s from yelp: %s', response.error, response.body)
        callback(None, error = (response.error, response.body))
      else:
        logging.debug('error response %s from yelp, but we\'re done', response.error)
        callback(results)
      return

    # OH EM GEE
    match = YelpBookmarksClient.BIZ_LIST_RE.search(response.body)
    if match == None:
      if len(results) == 0:
        logging.debug('No match, maybe user isn\'t public?')
        callback(None, error = (999, 'no bizlist, user might not be public?'))
      else:
        logging.debug('No match, maybe all done?')
        callback(results)
      return

    biz_list = match.group(1)
    decoded = None
    try:
      decoded = json_decode(biz_list)
    except Exception as e:
      logging.error('unable to decode json: %s', e)
      callback(None, error = (999, 'unable to decode json'))
      return

    results = results + decoded
    if len(decoded) == 50:
      logging.debug('found 50, trying next page')
      # try page next
      self._make_request(user_id, results, callback, page = page + 1)
      return
    else:
      logging.debug('found fewer than 50. done?')
      callback(results)

if __name__ == '__main__':
  parse_command_line()
  user_ids = ['wZ46o0rz0IbF8dYenyQVbw', # dolapo
              'W46UkrAvPokkWfXno1cD6g'  # some girl
             ]

  class Barrier:
    def __init__(self, total):
      self.num_calls = 0
      self.total = total

  def _test_callback(barrier, user_id, bookmarks, error = None):
    if error:
      logging.warning('unable to get bookmarks for %s: %s' % (user_id, error))
    else:
      logging.warning('bookmarks for %s: %s' % (user_id, len(bookmarks)))
    barrier.num_calls += 1
    if barrier.num_calls == barrier.total:
      tornado.ioloop.IOLoop.instance().stop()

  # a lil test driver
  client = YelpBookmarksClient()
  barrier = Barrier(len(user_ids))
  for i, user_id in enumerate(user_ids):
    client.get_bookmarks(user_id,
                         functools.partial(_test_callback, barrier, user_id))
  tornado.ioloop.IOLoop.instance().start()
