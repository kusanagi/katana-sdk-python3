import asyncio
import logging
import signal

from multiprocessing import Process

import zmq.asyncio

from .utils import install_uvevent_loop

LOG = logging.getLogger(__name__)


class ComponentProcess(Process):
    """Component child process class.

    Each process initializes an event loop to run a given number
    of worker tasks.

    Each worker task is used to asynchronically handle service
    discovery commands.

    """

    def __init__(self, channel, workers, callback, cli_args, *args, **kwargs):
        """Constructor.

        :param channel: IPC channel to connect to parent process.
        :type channel: str.
        :param workers: Number of component workers to start.
        :type workers: int.
        :param callback: A callable to use a request handler callback.
        :type callback: callable.
        :param cli_args: Command line arguments used to run current process.
        :type cli_args: dict.

        """

        super().__init__(*args, **kwargs)
        self.__loop = None
        self.__tasks = []
        self.channel = channel
        self.workers = workers
        self.callback = callback
        self.cli_args = cli_args

    @property
    def worker_factory(self):
        """Worker class or factory.

        When factory is a callable it must return a
        `ComponentWorker` instance.

        :rtype: `ComponentWorker` or callable.

        """

        raise NotImplementedError()

    def run(self):
        """Child process main code."""

        # Create an event loop for current process
        install_uvevent_loop()
        self.__loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(self.__loop)

        # Gracefully terminate process on SIGTERM events.
        self.__loop.add_signal_handler(signal.SIGTERM, self._cleanup)

        # Create a task for each worker
        for number in range(self.workers):
            worker = self.worker_factory(
                self.callback,
                self.channel,
                self.cli_args,
                )
            task = self.__loop.create_task(worker())
            self.__tasks.append(task)

        try:
            self.__loop.run_forever()
        except KeyboardInterrupt:
            LOG.debug('Component process SIGINT')
            self._cleanup()

    def _cleanup(self, *args):
        """Cleanup process."""

        # Finish all tasks
        LOG.debug('Canceling component PID %s workers', self.pid)
        for task in self.__tasks:
            task.cancel()

        # After tasks are cancelled close event loop
        self.__loop.call_soon(self.__loop.stop)
