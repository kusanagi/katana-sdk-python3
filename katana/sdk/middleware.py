from .sdk import SDK

from katana.middleware.server import MiddlewareServer


class Middleware(SDK):
    """KATANA SDK middleware."""

    def get_server(self, callback, cli_args):
        return MiddlewareServer(
            cli_args['address'],
            cli_args['endpoint'],
            callback,
            cli_args,
            debug=cli_args['debug']
            )

    def run_request(self, callback):
        self.run(callback)

    def run_response(self, callback):
        self.run(callback)
