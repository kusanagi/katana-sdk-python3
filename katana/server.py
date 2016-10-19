"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import asyncio
import logging

from concurrent.futures import CancelledError

import zmq.asyncio

from .utils import safe_cast

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

    def __init__(self, channel, callbacks, cli_args, **kwargs):
        """Constructor."""

        self.__process_list = []

        self.callbacks = callbacks
        self.cli_args = cli_args
        self.channel = channel
        self.poller = zmq.asyncio.Poller()
        self.context = zmq.asyncio.Context()
        self.sock = None
        self.workers_sock = None
        self.debug = kwargs.get('debug', False)
        self.source_file = kwargs.get('source_file')

        var = self.cli_args.get('var') or {}
        self.workers = safe_cast(var.get('workers'), int, self.workers)
        self.processes = safe_cast(var.get('processes'), int, self.processes)

    @property
    def workers_channel(self):
        """Component workers IPC connection channel.

        :rtype: str.

        """

        # Strip protocol from channel, in case channel is TCP
        return 'ipc://{}-workers'.format(self.channel[6:])

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
                self.callbacks,
                self.cli_args,
                source_file=self.source_file,
                )
            process.daemon = True
            self.__process_list.append(process)

    def start_child_processes(self):
        """Start all previously created child processes.

        Child processes has to be created before by calling
        `create_child_processes` method.

        """

        LOG.debug('Starting %s child process(es)', self.processes)
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

        LOG.debug('Stopping Component...')
        if not self.sock:
            return

        if self.sock:
            self.sock.close()
            self.sock = None

        if self.workers_sock:
            self.workers_sock.close()
            self.workers_sock = None

        self.terminate_child_processes()

    @asyncio.coroutine
    def proxy(self, frontend_sock, backend_sock):
        """Proxy requests between two sockets.

        :param frontend_sock: `zmq.Socket`.
        :param backend_sock: `zmq.Socket`.

        :rtype: coroutine.

        """

        while 1:
            events = yield from self.poller.poll()
            if dict(events).get(frontend_sock) == zmq.POLLIN:
                stream = yield from frontend_sock.recv_multipart()
                yield from backend_sock.send_multipart(stream)

            if dict(events).get(backend_sock) == zmq.POLLIN:
                stream = yield from backend_sock.recv_multipart()
                yield from frontend_sock.send_multipart(stream)

    def initialize_sockets(self):
        """Initialize component server sockets."""

        LOG.debug('Initializing internal sockets...')
        # Connect to katana forwarder
        self.sock = self.context.socket(zmq.ROUTER)
        LOG.debug('Opening incoming socket: "%s"', self.channel)
        self.sock.bind(self.channel)

        # Socket to forwrard incoming requests to workers
        self.workers_sock = self.context.socket(zmq.DEALER)
        LOG.debug(
            'Opening subprocess communication socket: "%s"',
            self.workers_channel,
            )
        self.workers_sock.bind(self.workers_channel)

        self.poller.register(self.sock, zmq.POLLIN)
        self.poller.register(self.workers_sock, zmq.POLLIN)

    @asyncio.coroutine
    def listen(self):
        """Start listening for requests."""

        self.initialize_sockets()
        # Create subprocesses to handle requests
        self.create_child_processes()
        self.start_child_processes()

        LOG.debug('Component action(s): %s', ','.join(
            sorted(self.callbacks.keys())
            ))
        try:
            LOG.info('Component initiated...')
            yield from self.proxy(self.sock, self.workers_sock)
        except CancelledError:
            # Call stop before cancelling task
            self.stop()
            # Re raise exception to signal task cancellation
            raise
