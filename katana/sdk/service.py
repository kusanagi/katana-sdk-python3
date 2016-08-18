import click

from ..service.server import ServiceServer
from ..utils import ipc

from .component import Component


class Service(Component):
    """KATANA SDK Service component."""

    server_factory = ServiceServer

    help = 'Service component action to process application logic'

    @property
    def action_name(self):
        return self._args['action']

    def get_argument_options(self):
        args = super().get_argument_options()
        args.append(click.option(
            '-a', '--action',
            required=True,
            help='Service action name',
            ))
        return args

    def get_default_socket_name(self):
        name = ipc('service', self.name, self.action_name)
        return name.replace('ipc://', '')

    def run_action(self, callback):
        self.run(callback)
