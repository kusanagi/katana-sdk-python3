from .sdk import SDK

from katana.middleware.server import MiddlewareServer


class Middleware(SDK):
    """KATANA SDK middleware."""

    def get_server(self, callback, args):
        return MiddlewareServer(
            args['name'],
            args['address'],
            args['version'],
            args['platform_version'],
            args['endpoint'],
            callback,
            debug=args.get('debug', False),
            )

    def run_request(self, callback):
        self.run(callback)

    def run_response(self, callback):
        self.run(callback)
