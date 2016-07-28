import asyncio
import inspect
import logging
import sys

import click
import zmq.asyncio

from ..errors import KatanaError
from ..utils import EXIT_ERROR
from ..utils import EXIT_OK
from ..utils import install_uvevent_loop

LOG = logging.getLogger(__name__)


class SDKError(KatanaError):
    """Base exception for SDK errors."""


class SDK(object):
    """Base KATANA SDK component class."""

    def __init__(self):
        """Constructor.

        :rtype: `SDK`.

        """

        self.__callback = None

    def __start_component(self, **kwargs):
        """Start component server.

        This call blocks the caller script until server finishes.

        Caller script is stopped when server finishes, by exiting
        with an exit code.

        """

        # Initialize component logging
        level = logging.DEBUG if kwargs['debug'] else logging.INFO
        logging.basicConfig(level=level)

        # Set main event loop
        install_uvevent_loop()
        loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(loop)

        # Run component server
        try:
            server = self.get_server(self.__callback, kwargs)
            exit_code = loop.run_until_complete(server.listen())
        except KeyboardInterrupt:
            exit_code = EXIT_OK
        except Exception as exc:
            LOG.exception('Component server failed')
            exit_code = EXIT_ERROR
        finally:
            server.stop()

        # Finish event loop and exit with an exit code
        loop.close()
        sys.exit(exit_code)

    def set_callback(self, callback):
        """Assign a callback to the SDK.

        :param callback: A callback with the bootstrap code.
        :type callback: callable.

        """

        self.__callback = callback

    def get_argument_options(self):
        """Get command line argument options.

        :rtype: list.

        """

        return [
            click.option(
                '-a', '--address',
                required=True,
                help='Component address',
                ),
            click.option(
                '-n', '--name',
                required=True,
                help='Component name',
                ),
            click.option(
                '-v', '--version',
                required=True,
                help='Component version',
                ),
            click.option(
                '-p', '--platform-version',
                required=True,
                help='KATANA platform version',
                ),
            click.option(
                '-e', '--endpoint',
                required=True,
                help='Endpoint name',
                ),
            click.option(
                '--debug',
                is_flag=True,
                ),
            ]

    def get_server(self, callback, args):
        """Get server instance to run current SDK component.

        Child classes MUST implement this method.

        :param callback: Callable to handle requests.
        :type callback: A callable.
        :param args: Command line arguments.
        :type args: dict.

        :rtype: `katana.sdk.server.Server`.

        """

        raise NotImplementedError()

    def run(self, callback):
        """Run SDK component.

        Callback must be a callable that receives a
        `katana.sdk.component.Component` argument.

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
        command = click.command(
            name=inspect.getfile(callback),
            help=inspect.getdoc(inspect.getmodule(callback)),
            )
        # Command must call `__start_component` method when
        # command line options are valid.
        start_component = command(self.__start_component)

        # Apply CLI options to command
        for option in self.get_argument_options():
            start_component = option(start_component)

        # Run SDK component
        start_component()
