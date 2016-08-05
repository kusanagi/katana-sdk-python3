from .sdk import SDK

from katana.service.server import ServiceServer


class Service(SDK):
    """KATANA SDK service."""

    server_factory = ServiceServer

    def run_action(self, callback):
        self.run(callback)
