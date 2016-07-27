import argparse
import asyncio
import logging
import sys

import zmq.asyncio

from ..errors import KatanaError
from ..utils import EXIT_ERROR
from ..utils import EXIT_OK
from ..utils import install_uvevent_loop

LOG = logging.getLogger(__name__)


class SDKError(KatanaError):
    """Base exception for SDK errors."""


class SDK(object):
    """Base Kusanagi SDK component class."""

    def __init__(self):
        """Constructor.

        :rtype: `SDK`.

        """

        self.callback = None

    def get_arguments_parser(self):
        parser = getattr(self, '__parser', None)
        # TODO: Use click for argument parsing and validation ?
        if not parser:
            parser = self.__parser = argparse.ArgumentParser()
            parser.add_argument('-a', '--address')
            parser.add_argument('-n', '--name')
            parser.add_argument('-v', '--version')
            parser.add_argument('-p', '--platform-version')
            parser.add_argument('-e', '--endpoint')
            # TODO: Make SDK debug argument boolean
            parser.add_argument('--debug')

        return parser

    def get_arguments(self):
        """Get command line arguments.

        :rtype: dict.

        """

        parser = self.get_arguments_parser()
        # Return argument values as a dictionary
        return parser.parse_args().__dict__

    def get_server(self, callback):
        """Get server instance to run current SDK component.

        Child classes MUST implement this method.

        Callback receives a single argument.

        :param callback: Callable to handle requests.
        :type callback: A callable.

        :rtype: `katana.sdk.platform.server.Server`.

        """

        raise NotImplementedError()

    def _run(self, callback):
        """Run component.

        This call blocks the caller script until server finishes.

        Caller script is stopped when server finishes, by exiting
        with an exit code.

        :param callback: Callable to handle requests.
        :type callback: A callable.

        """

        # TODO: Implement proper logging initialization for SDK
        logging.basicConfig(level=logging.DEBUG)

        install_uvevent_loop()
        loop = zmq.asyncio.ZMQEventLoop()
        asyncio.set_event_loop(loop)

        try:
            server = self.get_server(callback)
            exit_code = loop.run_until_complete(server.listen())
        except KeyboardInterrupt:
            exit_code = EXIT_OK
        except Exception as exc:
            LOG.exception('Component server failed')
            exit_code = EXIT_ERROR
        finally:
            server.stop()

        loop.close()
        sys.exit(exit_code)
