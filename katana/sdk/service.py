from ..service.server import ServiceServer

from .component import Component


class Service(Component):
    """KATANA SDK Service component."""

    server_factory = ServiceServer

    help = 'Service component action to process application logic'

    def run_action(self, callback):
        self.run(callback)
