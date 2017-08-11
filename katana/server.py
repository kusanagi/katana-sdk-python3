"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

import asyncio
import logging
import os

from collections import namedtuple

import zmq.asyncio

from .errors import KatanaError
from .json import serialize
from .payload import CommandPayload
from .payload import CommandResultPayload
from .payload import ErrorPayload
from .payload import Payload
from .schema import get_schema_registry
from .serialization import pack
from .serialization import unpack

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

LOG = logging.getLogger(__name__)

# Constants for response meta
EMPTY_META = b'\x00'
SE = SERVICE_CALL = b'\x01'
FI = FILES = b'\x02'
TR = TRANSACTIONS = b'\x03'
DL = DOWNLOAD = b'\x04'

# Allowed response meta values
META_VALUES = (EMPTY_META, SE, FI, TR, DL)

# Multipart request frames
Frames = namedtuple('Frames', ['action', 'mappings', 'stream'])


def create_error_stream(message, *args, **kwargs):
    """Create a new multipart error stream.

    :param message: Error message.
    :type message: str

    :rtype: list

    """

    if args or kwargs:
        message = message.format(*args, **kwargs)

    return [EMPTY_META, pack(ErrorPayload.new(message).entity())]


class ComponentServer(object):
    """Server class for components."""

    def __init__(self, callbacks, args, **kwargs):
        """Constructor.

        :param callbacks: Callbacks for registered action handlers.
        :type callbacks: dict
        :param args: CLI arguments.
        :type args: dict
        :param error_callback: Callback to use when errors occur.
        :type error_callback: function
        :param source_file: Full path to component source file.
        :type source_file: str

        """

        self.__args = args
        self.__socket = None
        self.__schema_registry = get_schema_registry()

        # Check the first callback to see if asyncio is being used,
        # otherwise callbacks are standard python callables.
        first_callback = next(iter(callbacks.values()))
        self.__use_async = asyncio.iscoroutinefunction(first_callback)

        self.loop = asyncio.get_event_loop()
        self.callbacks = callbacks
        self.error_callback = kwargs.get('error_callback')
        self.source_file = kwargs.get('source_file')

        self.context = None
        self.poller = None

    @property
    def component_name(self):
        return self.__args['name']

    @property
    def component_version(self):
        return self.__args['version']

    @property
    def framework_version(self):
        return self.__args['framework_version']

    @property
    def debug(self):
        return self.__args['debug']

    @property
    def variables(self):
        return self.__args.get('var')

    @property
    def component_title(self):
        return '"{}" ({})'.format(self.component_name, self.component_version)

    def create_error_payload(self, exc, component, **kwargs):
        """Create a payload for the error response.

        :params exc: The exception raised in user land callback.
        :type exc: Exception
        :params component: The component being used.
        :type component: Component

        :returns: A result payload.
        :rtype: Payload

        """

        raise NotImplementedError()

    def create_component_instance(self, action, payload, extra):
        """Create a component instance for a payload.

        The type of component created depends on the payload type.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: A payload.
        :type payload: Payload
        :param extra: A payload to add extra command reply values to result.
        :type extra: Payload

        :returns: A component instance.
        :rtype: `Component`

        """

        raise NotImplementedError()

    def component_to_payload(self, command_name, component):
        """Convert callback result to a command result payload.

        :params command_name: Name of command being executed.
        :type command_name: str
        :params component: The component being used.
        :type component: Component

        :returns: A command result payload.
        :rtype: CommandResultPayload

        """

        raise NotImplementedError()

    def get_response_meta(self, payload):
        """Get metadata for multipart response.

        By default no metadata is added to response.

        :param payload: Response payload.
        :type payload: Payload

        :rtype: bytes

        """

        return b''

    def __update_schema_registry(self, stream):
        """Update schema registry with new service schemas.

        :param stream: Mappings stream.
        :type stream: bytes

        """

        LOG.debug('Updating schemas for Services ...')
        try:
            self.__schema_registry.update_registry(unpack(stream))
        except asyncio.CancelledError:
            raise
        except:
            LOG.exception('Failed to update schemas')

    @asyncio.coroutine
    def __process_request_payload(self, action, payload):
        # Call request handler and send response back
        try:
            payload = yield from self.process_payload(
                action,
                CommandPayload(payload),
                )
        except asyncio.CancelledError:
            # Avoid logging task cancel errors by catching it here
            raise
        except KatanaError as err:
            payload = ErrorPayload.new(message=err.message).entity()
        except:
            LOG.exception('Component failed')
            payload = ErrorPayload.new('Component failed').entity()

        return payload

    @asyncio.coroutine
    def __process_request(self, stream):
        try:
            frames = Frames(*stream)
        except asyncio.CancelledError:
            raise
        except:
            LOG.error('Received an invalid multipart stream')
            return

        # Update global schema registry when mappings are sent
        if frames.mappings:
            self.__update_schema_registry(frames.mappings)

        # Get action name
        action = frames.action.decode('utf8')
        if action not in self.callbacks:
            # Return an error when action doesn't exist
            return create_error_stream(
                'Invalid action for component {}: "{}"',
                self.component_title,
                action,
                )

        # Get command payload from request stream
        try:
            payload = unpack(frames.stream)
        except asyncio.CancelledError:
            raise
        except:
            LOG.exception('Received an invalid message format')
            return create_error_stream('Internal communication failed')

        payload = yield from self.__process_request_payload(action, payload)

        return [self.get_response_meta(payload) or EMPTY_META, pack(payload)]

    @asyncio.coroutine
    def process_payload(self, action, payload):
        """Process a request payload.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: A command payload.
        :type payload: CommandPayload

        :returns: A Payload with the component response.
        :rtype: coroutine.

        """

        if not payload.path_exists('command'):
            LOG.error("Invalid request: Command payload is missing")
            return ErrorPayload.new('Internal communication failed').entity()

        command_name = payload.get('command/name')

        # Create a variable to hold extra command reply result values.
        # This is used for example to the request attributes.
        # Because extra is passed by reference any modification by the
        # create component modifies the extra payload.
        extra = Payload()

        # Create a component instance using the command payload and
        # call user land callback to process it and get a response component.
        component = self.create_component_instance(action, payload, extra)
        if not component:
            return ErrorPayload.new('Internal communication failed').entity()

        error = None
        try:
            if self.__use_async:
                # Call callback asynchronusly
                component = yield from self.callbacks[action](component)
            else:
                # Call callback in a different thread
                component = yield from self.loop.run_in_executor(
                    None,  # Use default executor
                    self.callbacks[action],
                    component,
                    )
        except asyncio.CancelledError:
            # Avoid logging task cancel errors by catching it here.
            raise
        except KatanaError as exc:
            error = exc
            payload = self.create_error_payload(
                exc,
                component,
                payload=payload,
                )
        except Exception as exc:
            LOG.exception('Component failed')
            error = exc
            payload = ErrorPayload.new(str(exc)).entity()
        else:
            payload = self.component_to_payload(payload, component)

        if error and self.error_callback:
            LOG.debug('Running error callback ...')
            try:
                self.error_callback(error)
            except:
                LOG.exception('Error callback failed for "%s"', action)

        # Add extra command reply result values to payload
        if extra:
            payload.update(extra)

        # Convert callback result to a command payload
        return CommandResultPayload.new(command_name, payload).entity()

    @asyncio.coroutine
    def process_input(self, message):
        """Process input message and print result payload.

        Input message is given from the CLI using the `--callback`
        option.

        :param message: Input message with action name and payload.
        :type message: dict

        :returns: The response payload as JSON
        :rtype: str

        """

        action = message['action']
        if action not in self.callbacks:
            message = 'Invalid action for component {}: "{}"'.format(
                self.component_title,
                action,
                )
            raise KatanaError(message)

        payload = yield from self.__process_request_payload(
            action,
            message['payload'],
            )
        # When an error payload is returned use its message
        # to raise an exception.
        error = payload.get('error/message', None)
        if error:
            raise KatanaError(error)

        output = serialize(payload, prettify=True).decode('utf8')
        print(output)

    @asyncio.coroutine
    def listen(self, channel):
        """Start listening for incoming requests.

        :param channel: Channel to listen for incoming requests.
        :type channel: str

        """

        # Create a generic error stream
        error_stream = create_error_stream('Failed to handle request')

        self.context = zmq.asyncio.Context()
        self.poller = zmq.asyncio.Poller()

        LOG.debug('Listening for requests in channel: "%s"', channel)
        self.__socket = self.context.socket(zmq.REP)
        self.__socket.bind(channel)
        self.poller.register(self.__socket, zmq.POLLIN)

        timeout = self.__args["timeout"] / 1000.0
        pid = os.getpid()

        LOG.info('Component initiated...')
        try:
            while 1:
                events = yield from self.poller.poll()
                events = dict(events)

                if events.get(self.__socket) == zmq.POLLIN:
                    # Get request multipart stream
                    stream = yield from self.__socket.recv_multipart()

                    # Process request and get response stream
                    try:
                        stream = yield from asyncio.wait_for(
                            self.__process_request(stream),
                            timeout=timeout,
                            )
                    except asyncio.TimeoutError:
                        msg = 'SDK execution timed out after {}ms'.format(
                            int(timeout * 1000),
                            pid,
                            )
                        LOG.warn('{}. PID: {}'.format(msg, pid))
                        stream = create_error_stream(msg)

                    # When there is no response send a generic error
                    if not stream:
                        stream = error_stream

                    yield from self.__socket.send_multipart(stream)
        except:
            self.stop()
            raise

    def stop(self):
        """Stop server."""

        LOG.debug('Stopping Component...')
        if self.__socket:
            self.poller.unregister(self.__socket)
            self.__socket.close()
            self.__socket = None
