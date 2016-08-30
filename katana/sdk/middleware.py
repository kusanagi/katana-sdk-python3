from ..middleware.server import MiddlewareServer

from .component import Component
from .runner import ComponentRunner


class Middleware(Component):
    """KATANA SDK Middleware component."""

    def __init__(self):
        super().__init__()
        self._runner = ComponentRunner(
            MiddlewareServer,
            'Middleware component to process HTTP requests and responses',
            )

    def run_request(self, callback):
        self.run(callback)

    def run_response(self, callback):
        self.run(callback)
