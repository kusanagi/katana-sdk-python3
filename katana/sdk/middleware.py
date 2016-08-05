from .sdk import SDK

from katana.middleware.server import MiddlewareServer


class Middleware(SDK):
    """KATANA SDK middleware."""

    server_factory = MiddlewareServer

    def run_request(self, callback):
        self.run(callback)

    def run_response(self, callback):
        self.run(callback)
