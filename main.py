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


async def shutdown():
    logging.info('Stopping server')
    http_server.stop()
    await gen.sleep(1)
    IOLoop.current().stop()


def exit_handler(sig, frame):
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback_from_signal(shutdown)


def start_server():
    urls = [
        (r'/', MainHandler),
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

    app = start_server()
    http_server = HTTPServer(app)
    port = int(os.getenv('PORT', 8888))
    http_server.listen(port)
    logging.info('Starting server')
    IOLoop.current().start()
