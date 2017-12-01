"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

from .api.action import Action
from .payload import ErrorPayload
from .payload import get_path
from .payload import path_exists
from .payload import Payload
from .payload import TransportPayload
from .server import ComponentServer
from .server import DOWNLOAD
from .server import FILES
from .server import SERVICE_CALL
from .server import TRANSACTIONS
from .utils import nomap

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class ServiceServer(ComponentServer):
    """Server class for service component."""

    def __init__(self, *args, **kwargs):
        from .sdk.service import get_component

        super().__init__(*args, **kwargs)
        self.__component = get_component()
        self.__return_value = None
        self.__transport = None

    @staticmethod
    def get_type():
        return 'service'

    @property
    def component_path(self):
        return '{}/{}'.format(
            nomap(self.component_name),
            self.component_version,
            )

    def get_response_meta(self, payload):
        meta = super().get_response_meta(payload)
        transport = payload.get('command_reply/result/transport', None)
        if not transport:
            return meta

        # When a download is registered add files flag
        if get_path(transport, 'body', None):
            meta += DOWNLOAD

        # Add transactions flag when any transaction is registered
        if get_path(transport, 'transactions', None):
            meta += TRANSACTIONS

        # Add meta for service call when inter service calls are made
        calls = get_path(
            transport,
            'calls/{}'.format(self.component_path),
            None,
            )
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
                    address = get_path(transport, 'meta/gateway')[1]  # Public gateway address
                    for call in calls:
                        files_path = '{} {} {} {}'.format(
                            address,
                            nomap(get_path(call, 'name')),
                            get_path(call, 'version'),
                            nomap(get_path(call, 'action')),
                            )

                        # Add flag and exit when at least one call has files
                        if path_exists(files, files_path, delimiter=' '):
                            meta += FILES
                            break

        return meta

    def create_component_instance(self, action, payload, *args):
        """Create a component instance for current command payload.

        :param action: Name of action that must process payload.
        :type action: str
        :param payload: Command payload.
        :type payload: `CommandPayload`

        :rtype: `Action`

        """

        payload = payload.get('command/arguments')

        # Save transport locally to use it for response payload
        self.__transport = TransportPayload(get_path(payload, 'transport'))
        # Create an empty return value
        # TODO: This should use the extra argument that this method receives
        #       See middlewares and "attributes".
        self.__return_value = Payload()

        return Action(
            action,
            get_path(payload, 'params', []),
            self.__transport,
            self.__component,
            self.source_file,
            self.component_name,
            self.component_version,
            self.framework_version,
            variables=self.variables,
            debug=self.debug,
            return_value=self.__return_value,
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

        if not self.__return_value:
            return self.__transport.entity()

        # Use return value as base payload and add transport entity
        self.__return_value.update(self.__transport.entity())
        return self.__return_value

    def create_error_payload(self, exc, action, payload):
        # Add error to transport and return transport
        transport = TransportPayload(
            payload.get('command/arguments/transport')
            )
        transport.push(
            'errors|{}|{}|{}'.format(
                transport.get('meta/gateway')[1],  # Public gateway address
                nomap(action.get_name()),
                action.get_version(),
                ),
            ErrorPayload.new(str(exc)),
            delimiter='|',
            )
        return transport.entity()
