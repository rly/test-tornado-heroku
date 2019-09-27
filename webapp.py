import logging
import signal
import os
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.httpserver import HTTPServer
from tornado import gen

from tornado.log import enable_pretty_logging


class MainHandler(RequestHandler):
    def get(self):
        self.write('Hello, world')


class CommandHookHandler(RequestHandler):
    def post(self):
        headers = self.request.headers
        event = headers.get('X-GitHub-Event', None)

        if event == 'ping':
            self.write('pong')
        else:
            print('Unhandled event "{}".'.format(event))
            self.set_status(404)
            self.write_error(404)


async def shutdown():
    logging.info('Stopping server')
    http_server.stop()
    await gen.sleep(1)
    IOLoop.current().stop()


def exit_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback_from_signal(shutdown)


def create_webapp():
    urls = [
        (r'/', MainHandler),
        (r'/nwb-extensions-command/hook', CommandHookHandler)
    ]
    return Application(urls)


handler = logging.FileHandler('tornado.log')
app_log = logging.getLogger('tornado.application')
app_log.setLevel(logging.INFO)
enable_pretty_logging()
app_log.addHandler(handler)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    app = create_webapp()
    http_server = HTTPServer(app, xheaders=True)
    port = int(os.getenv('PORT', 8888))

    # https://devcenter.heroku.com/articles/optimizing-dyno-usage#python
    n_processes = int(os.environ.get("WEB_CONCURRENCY", 1))

    if n_processes != 1:
        logging.info('Multiple processes available. Binding to port %d' % port)
        # http://www.tornadoweb.org/en/stable/guide/running.html#processes-and-ports
        http_server.bind(port)
        http_server.start(n_processes)
    else:
        logging.info('Listening to port %d' % port)
        http_server.listen(port)

    logging.info('Starting server')
    IOLoop.current().start()
