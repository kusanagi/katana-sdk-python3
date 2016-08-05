import asyncio
import logging
import signal

import click
import zmq.asyncio

from .utils import EXIT_ERROR
from .utils import EXIT_OK
from .utils import ipc

LOG = logging.getLogger(__name__)


class ComponentServer(object):
    """Server class for component services.

    Server creates a number of child processes to handle command requests.
    Each child process uses asyncio internally to handle concurrent requests.

    """

    # Default number of child processes
    processes = 1

    # Default number of worker task per process
    workers = 5

    def __init__(self, address, endpoint, callback, cli_args, **kwargs):

        self.__process_list = []

        self.callback = callback
        self.cli_args = cli_args
        self.channel = ipc(address, endpoint)
        self.poller = zmq.asyncio.Poller()
        self.context = zmq.asyncio.Context()
        self.sock = None
        self.workers_sock = None
        self.debug = kwargs.get('debug', False)
        # TODO: Document and set engine variable values
        self.variables = kwargs.get('variables') or {}
        self.workers = self.variables.get('workers', self.workers)
        self.processes = self.variables.get('processes', self.processes)

    @property
    def workers_channel(self):
        """Component workers connection channel.

        :rtype: str.

        """

        return '{}-{}'.format(self.channel, 'workers')

    @property
    def process_factory(self):
        """Process class or factory.

        When factory is a callable it must return a
        `ComponentProcess` instance.

        :rtype: `ComponentProcess` or callable.

        """

        raise NotImplementedError()

    def create_child_processes(self):
        """Create child processes."""

        for number in range(self.processes):
            process = self.process_factory(
                self.workers_channel,
                self.workers,
                self.callback,
                self.cli_args,
                )
            process.daemon = True
            self.__process_list.append(process)

    def start_child_processes(self):
        """Start all previously created child processes.

        Child processes has to be created before by calling
        `create_child_processes` method.

        """

        for process in self.__process_list:
            process.start()

    def terminate_child_processes(self):
        """Terminate all child processes."""

        for process in self.__process_list:
            process.terminate()
            # TODO: Use wait to terminate children ?
            process.join()

    def stop(self, *args):
        """Stop service discovery.

        This terminate all child processes and closes all sockets.

        :note: This method can be called from a signal like SIGTERM.

        """

        if not self.sock:
            return

        self.sock.close()
        self.sock = None
        self.workers_sock.close()
        self.terminate_child_processes()

    @asyncio.coroutine
    def proxy(self, frontend_sock, backend_sock):
        """Proxy requests between two sockets.

        :param frontend_sock: `zmq.Socket`.
        :param backend_sock: `zmq.Socket`.

        :rtype: coroutine.

        """

        while True:
            events = yield from self.poller.poll()
            if dict(events).get(frontend_sock) == zmq.POLLIN:
                stream = yield from frontend_sock.recv_multipart()
                yield from backend_sock.send_multipart(stream)

            if dict(events).get(backend_sock) == zmq.POLLIN:
                stream = yield from backend_sock.recv_multipart()
                yield from frontend_sock.send_multipart(stream)

    def initialize_sockets(self):
        """Initialize component server sockets.

        :returns: False when initialization of a socket fails.
        :rtype: bool.

        """

        # Connect to katana forwarder
        try:
            self.sock = self.context.socket(zmq.ROUTER)
            self.sock.connect(self.channel)
        except zmq.error.ZMQError as err:
            msg = 'Unable to connect socket to %s. Error: %s'
            LOG.error(msg, self.channel, err)
            return False

        # Socket to forwrard incoming requests to workers
        try:
            self.workers_sock = self.context.socket(zmq.DEALER)
            self.workers_sock.bind(self.workers_channel)
        except zmq.error.ZMQError as err:
            msg = 'Unable to bind worker socket to %s. Error: %s'
            LOG.error(msg, self.workers_channel, err)
            return False

        self.poller.register(self.sock, zmq.POLLIN)
        self.poller.register(self.workers_sock, zmq.POLLIN)
        return True

    @asyncio.coroutine
    def listen(self):
        """Start listening for requests."""

        exit_code = EXIT_OK

        if not self.initialize_sockets():
            self.stop()
            return EXIT_ERROR
        else:
            # Create subprocesses to handle requests
            self.create_child_processes()
            self.start_child_processes()

            # Gracefully close on SIGTERM events to avoid
            # leaving child processes running in background.
            signal.signal(signal.SIGTERM, self.stop)

        try:
            click.echo('Listening for requests')
            yield from self.proxy(self.sock, self.workers_sock)
        except (KeyboardInterrupt, GeneratorExit):
            click.echo("Stopping server ..")
        except:
            LOG.exception('Component server error')
            exit_code = EXIT_ERROR
        finally:
            # Finally cleanup
            self.stop()

        return exit_code
