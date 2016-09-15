import logging

from ..api.action import Action
from ..payload import ErrorPayload
from ..payload import get_path
from ..payload import path_exists
from ..payload import Payload
from ..payload import TransportPayload
from ..worker import ComponentWorker
from ..worker import FILES
from ..worker import SERVICE_CALL

LOG = logging.getLogger(__name__)


class ServiceWorker(ComponentWorker):
    """Service worker task class."""

    @property
    def action(self):
        """Name of service action this service handles.

        :rtype: str

        """

        return self.cli_args['action']

    @property
    def component_action_path(self):
        return '{}/{}'.format(self.component_path, self.action)

    def get_response_meta(self, payload):
        meta = super().get_response_meta(payload)
        transport = payload.get('command_reply/result/transport', None)
        if not transport:
            return meta

        # Add meta for service call when inter service calls are made
        calls = get_path(transport, 'calls/{}'.format(self.component_path), None)
        if calls:
            meta += SERVICE_CALL

            # Add meta for files only when service calls are made.
            # Files are setted in a service ONLY when a call to
            # another service is made.
            files = get_path(transport, 'files', None)
            for call in calls:
                files_path = '{}/{}/{}'.format(
                    get_path(call, 'name'),
                    get_path(call, 'version'),
                    get_path(call, 'action'),
                    )
                # Add flag and exit when at least one call has files
                if path_exists(files, files_path):
                    meta += FILES
                    break

        return meta

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
            self.action,
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
        return transport.entity()
