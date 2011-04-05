from tornado import template
from tornado.options import options, define, parse_command_line
from tornado.web import Application, RequestHandler, url

import logging
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web

define('port', type = int, default = 9009)
define('debug', type = bool, default = False)

class BaseHandler(RequestHandler):
  pass

class RootHandler(BaseHandler):
  @tornado.web.asynchronous
  def get(self):
    self.render('index.html')

def main():
  parse_command_line()
  template_path = os.path.join(os.path.dirname(__file__), 'templates')
  static_path = os.path.join(os.path.dirname(__file__), 'static')
  template_loader_factory = lambda: template.Loader(template_path)

  handlers = [
    url(r'/$', RootHandler)
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
