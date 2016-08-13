from ..middleware.server import MiddlewareServer

from .component import Component


class Middleware(Component):
    """KATANA SDK Middleware component."""

    server_factory = MiddlewareServer

    help = 'Middleware component to process HTTP requests and responses'

    def run_request(self, callback):
        self.run(callback)

    def run_response(self, callback):
        self.run(callback)
