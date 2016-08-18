from ..middleware.server import MiddlewareServer
from ..utils import ipc

from .component import Component


class Middleware(Component):
    """KATANA SDK Middleware component."""

    server_factory = MiddlewareServer

    help = 'Middleware component to process HTTP requests and responses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__middleware_type = None

    def get_default_socket_name(self):
        name = ipc('middleware', self.name, self.__middleware_type)
        return name.replace('ipc://', '')

    def run_request(self, callback):
        self.__middleware_type = 'request'
        self.run(callback)

    def run_response(self, callback):
        self.__middleware_type = 'response'
        self.run(callback)
