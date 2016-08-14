import asyncio
import inspect
import logging
import os

import click
import zmq.asyncio

from ..errors import KatanaError
from ..logging import setup_katana_logging
from ..utils import EXIT_ERROR
from ..utils import EXIT_OK
from ..utils import install_uvevent_loop

LOG = logging.getLogger(__name__)


def key_value_strings_callback(ctx, param, values):
    """Option callback to validate a list of key/value arguments.

    Converts 'NAME=VALUE' cli parameters to a dictionary.

    :rtype: dict

    """

    params = {}
    if not values:
        return params

    for value in values:
        parts = value.split('=')
        if len(parts) != 2:
            raise click.BadParameter('Invalid parameter format')

        param_name, param_value = parts
        params[param_name] = param_value

    return params


class Component(object):
    """Base KATANA SDK component class."""

    def __init__(self):
        """Constructor."""

        self._args = {}
        self.callback = None

    @property
    def server_factory(self):
        """Component server class or factory.

        When factory is a callable it must return a
        `katana.sdk.server.Server` instance.

        :rtype: `katana.sdk.server.Server` or callable.

        """

        raise NotImplementedError()

    @property
    def args(self):
        """Command line arguments.

        Command line arguments are initialized during `run` with the values
        used to run the component.

        :rtype: dict

        """

        return self._args

    @property
    def socket_name(self):
        """IPC socket name.

        :rtype: str or None

        """

        return self._args.get('socket') or self.get_default_socket_name()

    @property
    def name(self):
        """Component name.

        :rtype: str

        """

        return self._args['name']

    @property
    def debug(self):
        """Check if debug is enabled for current component.

        :rtype: bool

        """

        return self._args.get('debug', False)

    @property
    def help(self):
        """Get a description to be displayed as CLI help text

        :rtype: str

        """

        raise NotImplementedError()

    def get_default_socket_name(self):
        """Get a default socket name to use when socket name is missing.

        :rtype: str

        """

        raise NotImplementedError()

    def set_callback(self, callback):
        """Assign a callback to the SDK.

        :param callback: A callback with the bootstrap code.
        :type callback: callable.

        """

        self.callback = callback

    def get_argument_options(self):
        """Get command line argument options.

        :rtype: list.

        """

        return [
            click.option(
                '-D', '--debug',
                is_flag=True,
                ),
            click.option(
                '-n', '--name',
                required=True,
                help='Component name',
                ),
            click.option(
                '-p', '--platform-version',
                required=True,
                help='KATANA platform version',
                ),
            click.option(
                '-s', '--socket',
                help='IPC socket name',
                ),
            click.option(
                '-v', '--version',
                required=True,
                help='Component version',
                ),
            click.option(
                '-V', '--var',
                multiple=True,
                callback=key_value_strings_callback,
                help='Variables',
                ),
            ]

    def __start_component_server(self, **kwargs):
        """Start component server.

        This call blocks the caller script until server finishes.

        Caller script is stopped when server finishes, by exiting
        with an exit code.

        """

        self._args = kwargs

        # Initialize component logging
        setup_katana_logging(logging.DEBUG if self.debug else logging.INFO)

        # Set main event loop
        install_uvevent_loop()
        loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(loop)

        # Run component server
        exit_code = EXIT_OK
        try:
            server = self.server_factory(
                self.socket_name,
                self.callback,
                self.args,
                debug=self.debug,
                )
            loop.run_until_complete(server.listen())
        except zmq.error.ZMQError as err:
            if err.errno == 98:
                msg = 'Address unavailable: "{}"'.format(self.socket_name)
            else:
                LOG.error(err.strerror)
                msg = 'Operation failed'

            LOG.error(msg)
            exit_code = EXIT_ERROR
        except KeyboardInterrupt:
            LOG.info('HARAKIRI!')
        except:
            LOG.exception('Component failed')
            exit_code = EXIT_ERROR
        finally:
            server.stop()

        # Finish event loop and exit with an exit code
        loop.close()
        os._exit(exit_code)

    def run(self, callback):
        """Run SDK component.

        Callback must be a callable that receives a
        `katana.api.base.Api` argument.

        Calling this method checks command line arguments before
        component server starts.

        :param callback: Callable to handle requests.
        :type callback: A callable.

        """

        self.set_callback(callback)

        # Create a command object to run the SDK component.
        # Use callback source file as command name, and the
        # docstring from the module where callback is defined
        # as help string for the command.
        command = click.command(name=inspect.getfile(callback), help=self.help)
        # Command must call `__start_component_server` method when
        # command line options are valid.
        start_component = command(self.__start_component_server)

        # Apply CLI options to command
        for option in self.get_argument_options():
            start_component = option(start_component)

        # Run SDK component
        start_component()
