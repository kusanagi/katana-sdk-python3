"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import logging

from ..api.action import Action
from ..payload import ErrorPayload
from ..payload import get_path
from ..payload import path_exists
from ..payload import TransportPayload
from ..worker import ComponentWorker
from ..worker import DOWNLOAD
from ..worker import FILES
from ..worker import SERVICE_CALL
from ..worker import TRANSACTIONS

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

LOG = logging.getLogger(__name__)


class ServiceWorker(ComponentWorker):
    """Service worker task class."""

    def __get_component(self):
        from ..sdk.service import get_component

        return get_component()

    def get_response_meta(self, payload):
        meta = super().get_response_meta(payload)
        transport = payload.get('command_reply/result/transport', None)
        if not transport:
            return meta

        # When a download is registered add files flag
        if transport.get('body', None):
            meta += DOWNLOAD

        # Add transactions flag when any transaction is registered
        if transport.get('transactions', None):
            meta += TRANSACTIONS

        # Add meta for service call when inter service calls are made
        calls = get_path(transport, 'calls/{}'.format(self.component_path), None)
        if calls:
            meta += SERVICE_CALL

            # TODO: Check for file paths to be sure flag is added when local
            # files are used in any call.
            # Check if there are files added to calls
            if FILES not in meta:
                # Add meta for files only when service calls are made.
                # Files are setted in a service ONLY when a call to
                # another service is made.
                files = get_path(transport, 'files', None)
                if files:
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

    def create_component_instance(self, action, payload):
        """Create a component instance for current command payload.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: Command payload.
        :type payload: `CommandPayload`

        :rtype: `Action`

        """

        # Save transport locally to use it for response payload
        self.__transport = TransportPayload(
            payload.get('command/arguments/transport')
            )

        return Action(
            action,
            payload.get('command/arguments/params'),
            self.__transport,
            self.__get_component(),
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
            'errors|{}|{}|{}'.format(
                transport.get('meta/gateway')[1],  # Public gateway address
                action.get_name(),
                action.get_version(),
                ),
            ErrorPayload.new(str(exc)),
            delimiter='|',
            )
        return transport.entity()
