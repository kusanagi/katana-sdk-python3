from .sdk import SDK

from katana.service.server import ServiceServer


class Service(SDK):
    """KATANA SDK service."""

    server_factory = ServiceServer

    help = 'Service component action to process application logic'

    def run_action(self, callback):
        self.run(callback)
