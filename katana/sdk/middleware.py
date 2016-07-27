from .sdk import SDK

from katana.middleware.server import MiddlewareServer


class Middleware(SDK):
    """Kusanagi SDK middleware."""

    def get_server(self, callback):
        args = self.get_arguments()
        # TODO: Define a base, middleware request and also response server
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
        # TODO: Implement middleware run request using commands
        self._run(callback)

    def run_response(self, callback):
        # TODO: Implement middleware run response using commands
        self._run(callback)
