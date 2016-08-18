import logging

from ..api.action import Action
from ..payload import ErrorPayload
from ..payload import Payload
from ..payload import TransportPayload
from ..worker import ComponentWorker

LOG = logging.getLogger(__name__)


class ServiceWorker(ComponentWorker):
    """Service worker task class."""

    def create_component_instance(self, payload):
        """Create a component instance for current command payload.

        :param payload: Command payload.
        :type payload: `CommandPayload`

        :rtype: `Action`

        """

        # Save transport locally to use it for response payload
        self.__transport = TransportPayload(
            payload.get('command/arguments/transport')
            )

        return Action(
            payload.get('command/name'),
            Payload(payload.get('command/arguments/params')),
            self.__transport,
            self.source_file,
            self.component_name,
            self.component_version,
            self.platform_version,
            variables=self.cli_args.get('var'),
            debug=self.debug,
            )

    def component_to_payload(self, payload, *args, **kwargs):
        """Convert component to a command result payload.

        :params payload: Command payload from current request.
        :type payload: `CommandPayload`
        :params component: The component being used.
        :type component: `Component`

        :returns: A command result payload.
        :rtype: `CommandResultPayload`

        """

        return self.__transport.entity()

    def create_error_payload(self, exc, action, payload):
        # Add error to transport and return transport
        transport = TransportPayload(
            payload.get('command/arguments/transport')
            )
        transport.push(
            'errors/{}/{}'.format(action.get_name(), action.get_version()),
            ErrorPayload.new(str(exc))
            )
        return transport
