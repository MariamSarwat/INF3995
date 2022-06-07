import json
import logging

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from src.routes import Route


def catch_exception(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        # pylint: disable=broad-except
        except Exception as E:
            logging.exception(E)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
    return wrapper

class HttpRequestHandler(BaseHTTPRequestHandler):

    # pylint: disable=signature-differs
    def log_request(self, *args):
        pass

    # pylint: disable=signature-differs
    def log_message(self, *args):
        pass

    # pylint: disable=signature-differs
    def log_error(self, *args):
        pass

    # pylint: disable=arguments-differ
    def send_error(self, code, message=None):
        self.send_response(code, message=message)
        self.end_headers()

    def log_client(self, method):
        logging.info("New %s request from %s:%s. Path:%s ",
                     method,
                     self.client_address[0], self.client_address[1],
                     self.path)

    @catch_exception
    def do_GET(self):

        route_match = Route.get_GET_route(self.path)

        if route_match:

            kwargs, todo = route_match

            if todo not in Route.divert_log_set:
                self.log_client("GET")

            if not Route.has_auth(self.headers["Authorization"], todo):
                logging.warning("authorization failed")
                self.send_error(HTTPStatus.UNAUTHORIZED)
                return

            response = { "body": {} }
            code     = todo(response,**kwargs)

            self.send_response(int(code))
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response["body"]), 'utf-8'))
        else:
            self.log_client("GET")
            self.send_error(HTTPStatus.NOT_FOUND)
            logging.error("path '%s' not found", self.path)

    @catch_exception
    def do_POST(self):
        route_match = Route.get_POST_route(self.path)

        logging.info("New POST request from %s:%s. Path:%s ",
                     self.client_address[0], self.client_address[1], self.path)

        if route_match:

            data_len = int(self.headers.get('Content-Length', 0))
            data_string = self.rfile.read(data_len)

            logging.info("Body:%s", data_string.decode('utf-8'))

            if not data_string:
                data = {}
            else:
                try:
                    data = json.loads(data_string)
                except json.decoder.JSONDecodeError:
                    self.send_error(HTTPStatus.BAD_REQUEST, message="Bad JSON")
                    return

            todo     = route_match
            response = {"body":{}}
            code     = todo(response,data)

            if code == HTTPStatus.OK:
                self.send_response(int(code))
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(response["body"]), 'utf-8'))
            else:
                self.send_error(code)

        else :
            logging.warning("path '%s' not found", self.path)
            self.send_error(HTTPStatus.NOT_FOUND)
            return

def run_server(server_class=HTTPServer,
               handler_class=HttpRequestHandler,
               port=80, module=''):

    addr   = ('', port)
    httpd = server_class(addr, handler_class)

    logging.info('Starting server for %s on port %d...', module, port)

    httpd.serve_forever()
