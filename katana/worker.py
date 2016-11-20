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

from collections import namedtuple
from concurrent.futures import CancelledError

import zmq.asyncio

from . import serialization
from .errors import HTTPError
from .payload import CommandPayload
from .payload import CommandResultPayload
from .payload import ErrorPayload

LOG = logging.getLogger(__name__)

# Constants for response meta frame
EMPTY_META = b'\x00'
SE = SERVICE_CALL = b'\x01'
FI = FILES = b'\x02'
TR = TRANSACTIONS = b'\x03'
DL = DOWNLOAD = b'\x04'

# Allowed response meta values
META_VALUES = (EMPTY_META, SE, FI, TR, DL)

# Request stream frames
RequestFrames = namedtuple('RequestFrames', ['action', 'stream'])


class ComponentWorker(object):
    """Component worker task class.

    This class handles component requests.

    A thread poll executor is used to allow concurrency in components
    that are not implemented as coroutines.

    """

    def __init__(self, context, poller, callbacks, channel, **kwargs):
        self.__socket = None
        self.context = context
        self.poller = poller
        self.callbacks = callbacks
        self.channel = channel
        self.error_callback = kwargs.get('error_callback')
        self.cli_args = kwargs['cli_args']
        self.source_file = kwargs.get('source_file', '')
        self.async = kwargs.get('async', False)
        self.loop = asyncio.get_event_loop()

    @property
    def component_name(self):
        return self.cli_args['name']

    @property
    def component_version(self):
        return self.cli_args['version']

    @property
    def platform_version(self):
        return self.cli_args['platform_version']

    @property
    def debug(self):
        return self.cli_args['debug']

    @property
    def component_path(self):
        return '{}/{}'.format(self.component_name, self.component_version)

    @property
    def component_title(self):
        return '"{}" ({})'.format(self.component_name, self.component_version)

    def create_error_payload(self, exc, component, **kwargs):
        """Create a payload for the error response.

        :params exc: The exception raised in user land callback.
        :type exc: `Exception`
        :params component: The component being used.
        :type component: `Component`

        :returns: A result payload.
        :rtype: `Payload`

        """

        raise NotImplementedError()

    def create_component_instance(self, payload):
        """Create a component instance for a payload.

        The type of component created depends on the payload type.

        :param payload: A payload.
        :type payload: Payload.

        :raises: HTTPError

        :returns: A component instance for the type of payload.
        :rtype: `Component`.

        """

        raise NotImplementedError()

    def component_to_payload(self, command_name, component):
        """Convert callback result to a command result payload.

        :params command_name: Name of command being executed.
        :type command_name: str
        :params component: The component being used.
        :type component: `Component`

        :returns: A command result payload.
        :rtype: `CommandResultPayload`

        """

        raise NotImplementedError()

    @asyncio.coroutine
    def process_payload(self, action, payload):
        """Process a request payload.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: A command payload.
        :type payload: `CommandPayload`

        :returns: A Payload with the component response.
        :rtype: coroutine.

        """

        if not payload.path_exists('command'):
            LOG.error('Payload missing command')
            return ErrorPayload.new('Internal communication failed').entity()

        command_name = payload.get('command/name')

        # Create a component instance using the command payload and
        # call user land callback to process it and get a response component.
        component = self.create_component_instance(action, payload)
        if not component:
            return ErrorPayload.new('Internal communication failed').entity()

        try:
            if self.async:
                # Call callback asynchronusly
                component = yield from self.callbacks[action](component)
            else:
                # Call callback in a different thread
                component = yield from self.loop.run_in_executor(
                    None,  # Use default executor
                    self.callbacks[action],
                    component,
                    )
        except CancelledError:
            # Avoid logging task cancel errors by catching it here.
            raise
        except Exception as exc:
            if self.error_callback:
                LOG.debug('Running error callback ...')
                try:
                    self.error_callback(exc)
                except:
                    LOG.exception('Error callback failed for "%s"', action)

            LOG.exception('Component failed')
            payload = self.create_error_payload(
                exc,
                component,
                payload=payload,
                )
        else:
            payload = self.component_to_payload(payload, component)

        # Convert callback result to a command payload
        return CommandResultPayload.new(command_name, payload).entity()

    def get_response_meta(self, payload):
        """Get metadata for multipart response.

        By default no metadata is added to response.

        :param payload: Response payload.
        :type payload: `Payload`

        :rtype: bytes

        """

        return b''

    @asyncio.coroutine
    def process_stream(self, action, stream):
        if action not in self.callbacks:
            message = 'Action does not exist in component {}: "{}"'.format(
                self.component_title,
                action,
                )
            # TODO: Implement a better DRY solution for error responses.
            return [
                EMPTY_META,
                serialization.pack(ErrorPayload.new(message).entity()),
                ]

        # Parse stream to get the commnd payload
        try:
            payload = CommandPayload(serialization.unpack(stream))
        except:
            LOG.exception('Invalid message format received')
            payload = ErrorPayload.new('Internal communication failed')
            return [
                EMPTY_META,
                serialization.pack(payload.entity()),
                ]

        # Process command and return payload response serialized
        try:
            payload = yield from self.process_payload(action, payload)
        except CancelledError:
            # Avoid logging task cancel errors by catching it here
            raise
        except HTTPError as err:
            payload = ErrorPayload.new(status=err.status, message=err.body)
            payload = payload.entity()
        except:
            LOG.exception('Component failed')
            payload = ErrorPayload.new().entity()

        return [
            self.get_response_meta(payload) or EMPTY_META,
            serialization.pack(payload),
            ]

    @asyncio.coroutine
    def _start_handling_requests(self):
        """Start handling incoming component requests and responses.

        This method starts an infinite loop that polls socket for
        incoming requests.

        """

        while True:
            events = yield from self.poller.poll()
            if dict(events).get(self.__socket) == zmq.POLLIN:
                # Get stream data from socket
                stream = yield from self.__socket.recv_multipart()

                # Parse multipart stream to get action name
                try:
                    frames = RequestFrames(*stream)
                except TypeError:
                    LOG.error('Invalid multipart stream received')
                except:
                    LOG.error('Invalid multipart stream format received')
                else:
                    # Call request handler and send response back
                    response_stream = yield from self.process_stream(
                        frames.action.decode('utf8'),
                        frames.stream,
                        )
                    yield from self.__socket.send_multipart(response_stream)

    @asyncio.coroutine
    def __call__(self):
        """Handle worker requests.

        :rtype: coroutine.

        """

        self.__socket = self.context.socket(zmq.REP)
        self.__socket.connect(self.channel)
        self.poller.register(self.__socket, zmq.POLLIN)
        try:
            yield from self._start_handling_requests()
        except CancelledError:
            # Call stop before cancelling task
            self.stop()
            # Re raise exception to signal task cancellation
            raise

    def stop(self):
        """Terminates worker task."""

        if self.__socket:
            self.poller.unregister(self.__socket)
            if not self.__socket.closed:
                self.__socket.close()

            self.__socket = None
