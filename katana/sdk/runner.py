"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import asyncio
import inspect
import logging
import os
import signal

import click
import zmq.asyncio

import katana.payload

from ..logging import setup_katana_logging
from ..utils import EXIT_ERROR
from ..utils import EXIT_OK
from ..utils import install_uvevent_loop
from ..utils import ipc
from ..utils import tcp

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
        parts = value.split('=', 1)
        if len(parts) != 2:
            raise click.BadParameter('Invalid parameter format')

        param_name, param_value = parts
        params[param_name] = param_value

    return params


class ComponentRunner(object):
    """Component runner.

    This class allows to isolate Component implementation details and
    keep the Component itself consisten with KATANA SDK specifications.

    """

    def __init__(self, component, server_factory, help):
        """Constructor."""

        self.__component = component
        self.__tasks = []
        self.__stop = False
        self.__server = None
        self.__startup_callback = None
        self.__shutdown_callback = None
        self.__error_callback = None
        self._args = {}
        self.source_file = None
        self.sleep_period = 0.1
        self.loop = None
        self.callbacks = None
        self.server_factory = server_factory
        self.help = help

    @property
    def args(self):
        """Command line arguments.

        Command line arguments are initialized during `run`
        with the values used to run the component.

        :rtype: dict

        """

        return self._args

    @property
    def socket_name(self):
        """IPC socket name.

        :rtype: str

        """

        return self._args.get('socket') or self.get_default_socket_name()

    @property
    def tcp_port(self):
        """TCP port number.

        :rtype: str or None

        """

        return self._args.get('tcp')

    @property
    def name(self):
        """Component name.

        :rtype: str

        """

        return self._args['name']

    @property
    def version(self):
        """Component version.

        :rtype: str

        """

        return self._args['version']

    @property
    def component_type(self):
        """Component type.

        :rtype: str

        """

        return self._args['component']

    @property
    def debug(self):
        """Check if debug is enabled for current component.

        :rtype: bool

        """

        return self._args.get('debug', False)

    @property
    def compact_names(self):
        """Check if payloads should use compact names.

        :rtype: bool

        """

        return not self._args.get('disable_compact_names', False)

    def get_default_socket_name(self):
        """Get a default socket name to use when socket name is missing.

        :rtype: str

        """

        # Remove 'ipc://' from string to get socket name
        return ipc(self.component_type, self.name, self.version)[6:]

    def get_argument_options(self):
        """Get command line argument options.

        :rtype: list.

        """

        return [
            click.option(
                '-c', '--component',
                type=click.Choice(['service', 'middleware']),
                help='Component type',
                required=True,
                ),
            click.option(
                '-d', '--disable-compact-names',
                is_flag=True,
                help='Use full property names instead of compact in payloads.',
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
                '-q', '--quiet',
                is_flag=True,
                help='Disable all logs',
                ),
            click.option(
                '-s', '--socket',
                help='IPC socket name',
                ),
            click.option(
                '-t', '--tcp',
                help='TCP port',
                type=click.INT,
                ),
            click.option(
                '-v', '--version',
                required=True,
                help='Component version',
                ),
            click.option(
                '-D', '--debug',
                is_flag=True,
                ),
            click.option(
                '-V', '--var',
                multiple=True,
                callback=key_value_strings_callback,
                help='Variables',
                ),
            ]

    def set_startup_callback(self, callback):
        """Set a callback to be run during startup.

        :param callback: A callback to run on startup.
        :type callback: function

        """

        self.__startup_callback = callback

    def set_shutdown_callback(self, callback):
        """Set a callback to be run during shutdown.

        :param callback: A callback to run on shutdown.
        :type callback: function

        """

        self.__shutdown_callback = callback

    def set_error_callback(self, callback):
        """Set a callback to be run on message callback errors.

        :param callback: A callback to run on message callback errors.
        :type callback: function

        """

        self.__error_callback = callback

    def set_callbacks(self, callbacks):
        """Set message callbacks for each component action.

        :params callbacks: Callbacks for each action.
        :type callbacks: dict

        """

        self.callbacks = callbacks

    def __start_component_server(self, **kwargs):
        """Start component server.

        This call blocks the caller script until server finishes.

        Caller script is stopped when server finishes, by exiting
        with an exit code.

        """

        self._args = kwargs

        # Initialize component logging only when `quiet` argument is False
        if not kwargs.get('quiet'):
            setup_katana_logging(logging.DEBUG if self.debug else logging.INFO)

        LOG.debug('Using PID: "%s"', os.getpid())

        # Set main event loop
        install_uvevent_loop()
        self.loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(self.loop)

        # Create channel for TCP or IPC conections
        if self.tcp_port:
            channel = tcp('127.0.0.1:{}'.format(self.tcp_port))
        else:
            # Abstract domain unix socket
            channel = 'ipc://{}'.format(self.socket_name)

        # When compact mode is enabled use long payload field names
        if not self.compact_names:
            katana.payload.DISABLE_FIELD_MAPPINGS = True

        # Gracefully terminate component on SIGTERM events.
        self.loop.add_signal_handler(signal.SIGTERM, self.stop)
        self.loop.add_signal_handler(signal.SIGINT, self.stop)

        # Create component server and add it as a task
        self.__server = self.server_factory(
            channel,
            self.callbacks,
            self.args,
            debug=self.debug,
            source_file=self.source_file,
            error_callback=self.__error_callback,
            )
        task = self.loop.create_task(self.__server.listen())
        self.__tasks.append(task)

        # Create a task to monitor running tasks
        self.loop.create_task(self.monitor_tasks())

        # By default exit successfully
        exit_code = EXIT_OK

        # Call startup callback
        if self.__startup_callback:
            LOG.info('Running startup callback ...')
            try:
                self.__startup_callback(self.__component)
            except:
                LOG.exception('Startup callback failed')
                LOG.error('Component failed')
                exit_code = EXIT_ERROR

        # Run component server
        if exit_code != EXIT_ERROR:
            try:
                self.loop.run_forever()
            except Exception as exc:
                exit_code = EXIT_ERROR
                if isinstance(exc, zmq.error.ZMQError):
                    if exc.errno == 98:
                        LOG.error(
                            'Address unavailable: "%s"',
                            self.socket_name,
                            )
                    else:
                        LOG.error(exc.strerror)

                    LOG.error('Component failed')
                else:
                    LOG.exception('Component failed')

            # Finish event loop and exit with an exit code
            self.loop.close()

        # Call shutdown callback
        if self.__shutdown_callback:
            LOG.info('Running shutdown callback ...')
            try:
                self.__shutdown_callback(self.__component)
            except:
                LOG.exception('Shutdown callback failed')
                LOG.error('Component failed')
                exit_code = EXIT_ERROR

        if exit_code == EXIT_OK:
            LOG.info('Operation complete')

        os._exit(exit_code)

    @asyncio.coroutine
    def monitor_tasks(self):
        """Run until halt is called or a task exception is raised.

        Runs an infinite loop that checks status for all tasks
        and then sleeps for a short period.

        """

        while 1:
            yield from asyncio.sleep(self.sleep_period)

            # Check tasks status
            for task in self.__tasks:
                # Skip when task is not done
                if not task.done():
                    continue

                # When task is finished check for errors
                exc = task.exception()
                if exc:
                    raise exc

            if self.__stop:
                yield from self.stop_tasks()
                break

        # When monitor exists stop event loop
        self.loop.stop()

    @asyncio.coroutine
    def stop_tasks(self, timeout=1.5):
        """Stop all tasks.

        :param timeout: Seconds to wait for all tasks to be finished.
        :param timeout: float

        """

        for task in self.__tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to finish
        yield from asyncio.wait(self.__tasks, timeout=timeout)

    def run(self):
        """Run SDK component.

        Calling this method checks command line arguments before
        component server starts.

        """

        # Create a command object to run the SDK component.
        # Component caller source file name is used as command name.
        caller_frame = inspect.getouterframes(inspect.currentframe())[2]
        self.source_file = caller_frame[1]
        command = click.command(name=self.source_file, help=self.help)
        # Command must call `__start_component_server` method when
        # command line options are valid.
        start_component = command(self.__start_component_server)

        # Apply CLI options to command
        for option in self.get_argument_options():
            start_component = option(start_component)

        # Run SDK component
        start_component()

    def stop(self, *args, **kwargs):
        """Stop main loop and all running tasks."""

        LOG.info('HARAKIRI!')
        self.__stop = True
