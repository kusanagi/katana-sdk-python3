import asyncio
import functools
import logging

from collections import defaultdict

from .errors import KatanaError
from .payload import CommandPayload
from .payload import CommandResultPayload
from .serialization import unpack

LOG = logging.getLogger(__name__)


class CommandError(KatanaError):
    """Command exception class."""

    message = 'Operation failed'


class InvalidCommand(CommandError):
    """Error for invalid/unknown component commands."""

    message = 'Invalid component command {}:{}'

    def __init__(self, scope, name):
        super().__init__(message=self.message.format(scope, name))


class InvalidCommandPayload(CommandError):
    """Error for invalid command payloads.

    Payload can be invalid because it can't be deserialized/unpacked
    or just because its data formas is not valid.

    """

    message = 'Invalid command payload'


class InvalidCommandScope(CommandError):
    """Exception raised when command scope is invalid for current command."""

    message = 'Invalid command scope'


def register_handler(cls, scopes, name=None):
    """Function decorator to register a shared command handler with a class.

    Handler function name is used as command name when name
    argument is missing.

    :params scopes: Authorized components names.
    :type scopes: list.
    :params name: Command name.
    :type name: string.

    """

    def decorator(handler):
        # When name is missing use handler function name for the command
        command_name = name or handler.__name__
        cls.register_shared_handler(scopes, command_name, handler)

    return decorator


class CommandsManager(object):
    """Manager for component commands."""

    handlers = defaultdict(dict, {})

    payload_cls = CommandPayload

    @classmethod
    def register_handler(cls, scope, name, handler):
        """Register a command handler with this class.

        Handler can be any callable that receives a single
        argument with the `CommandPayload`.

        :params scope: Authorized component name.
        :type scope: str.
        :params name: Command name.
        :type name: str.
        :params handler: A callable to handle command.
        :type handler: callable.

        """

        cls.handlers[scope][name] = handler

    @classmethod
    def register_shared_handler(cls, scopes, name, handler):
        """Register a shared command handler with this class.

        This method registers a handler for many scopes.

        Handler can be any callable that receives a single
        argument with the `CommandPayload`.

        :params scopes: Authorized components names.
        :type scopes: list.
        :params name: Command name.
        :type name: str.
        :params handler: A callable to handle command.
        :type handler: callable.

        """

        for scope in scopes:
            cls.handlers[scope][name] = handler

    @classmethod
    def register_decorator(cls):
        """Decorator to register handlers for current class.

        This method uses partial to wrap `register_handler` decorator
        to use current class for handler registration.

        :returns: A function decorator.
        :rtype: function.

        """

        return functools.partial(register_handler, cls)

    def is_valid_command(self, payload):
        """Checks if a payload contains a valid command.

        :param payload: Payload with command data.
        :type: payload: CommandPayload.

        :rtype: bool.

        """

        scope = payload.get('meta/scope', None)
        return (
            scope in self.handlers and
            payload.get('command/name', None) in self.handlers[scope]
            )

    def get_handler(self, scope, name):
        """Get handler for a command.

        :params scope: Authorized component name.
        :type scope: str.
        :params name: Command name.
        :type name: str.

        :raises: InvalidCommand
        :raises: InvalidCommandScope

        :rtype: callable.

        """

        if scope not in self.handlers:
            raise InvalidCommandScope()

        try:
            return self.handlers[scope][name]
        except KeyError:
            raise InvalidCommand(scope, name)

    def get_handler_kwargs(self, scope, name):
        """Get keyword arguments for a handler.

        :params scope: Component name.
        :type scope: str.
        :params name: Command name.
        :type name: str.

        :rtype: dict.

        """

        return {'scope': scope}

    def process_payload(self, payload):
        """Process a command payload.

        :param payload: Payload with command data.
        :type payload: CommandPayload.

        :raises: InvalidCommand
        :raises: InvalidCommandScope

        :returns: The command result payload.
        :rtype: `CommandResultPayload`

        """

        scope = payload.get('meta/scope', 'MISSING')
        name = payload.get('command/name', 'MISSING')
        args = payload.get('command/arguments', None) or {}
        handler = self.get_handler(scope, name)
        result = handler(args, **self.get_handler_kwargs(scope, name))
        return CommandResultPayload.new(name, result).entity()

    def process_stream(self, stream):
        """Process a stream that contains a packed command payload.

        This method unpacks the stream into a `CommandPayload` and then
        calls `process_payload`.

        :param stream: Packed payload with command data.
        :type stream: bytes

        :raises: CommandError
        :raises: InvalidCommand
        :raises: InvalidCommandScope
        :raises: InvalidCommandPayload

        :returns: The command result payload.
        :rtype: `CommandResultPayload`

        """

        try:
            payload = self.payload_cls(unpack(stream))
            return self.process_payload(payload)
        except (TypeError, ValueError) as err:
            LOG.error('Command payload stream process failed: %s', err)
            raise InvalidCommandPayload()
        except CommandError:
            raise
        except:
            LOG.exception('Command stream processing failed')
            raise CommandError()


class AsyncCommandsManager(CommandsManager):
    """Manager for component commands.

    This manager calls commands using asyncio.

    Handlers registered in this class should be async.

    """

    handlers = defaultdict(dict, {})

    @asyncio.coroutine
    def process_payload(self, payload):
        """Process a command payload.

        :param payload: Payload with command data.
        :type payload: CommandPayload.

        :raises: InvalidCommand
        :raises: InvalidCommandScope

        :returns: The command result payload.
        :rtype: coroutine.

        """

        scope = payload.get('meta/scope', 'MISSING')
        name = payload.get('command/name', 'MISSING')
        args = payload.get('command/arguments', None) or {}
        kwargs = self.get_handler_kwargs(scope, name)
        handler = self.get_handler(scope, name)
        result = yield from handler(args, **kwargs)
        return CommandResultPayload.new(name, result).entity()

    @asyncio.coroutine
    def process_stream(self, stream):
        """Process a stream that contains a packed command payload.

        This method unpacks the stream into a `CommandPayload` and then
        calls `process_payload`.

        :param stream: Packed payload with command data.
        :type stream: bytes

        :raises: CommandError
        :raises: InvalidCommand
        :raises: InvalidCommandScope
        :raises: InvalidCommandPayload

        :returns: The command result payload.
        :rtype: coroutine.

        """

        try:
            payload = self.payload_cls(unpack(stream))
            payload = yield from self.process_payload(payload)
            return payload
        except (TypeError, ValueError) as err:
            LOG.error('Command payload stream process failed: %s', err)
            raise InvalidCommandPayload()
        except CommandError:
            raise
        except:
            LOG.exception('Async command stream processing failed')
            raise CommandError()
