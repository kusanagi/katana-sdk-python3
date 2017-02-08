"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from .action import ActionSchema
from .error import ServiceSchemaError
from ... payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class ServiceSchema(object):
    """Service schema in the framework."""

    def __init__(self, name, version, payload):
        self.__name = name
        self.__version = version
        self.__payload = Payload(payload)
        self.__actions = self.__payload.get('actions', {})

    def get_name(self):
        """Get Service name.

        :rtype: str

        """

        return self.__name

    def get_version(self):
        """Get Service version.

        :rtype: str

        """

        return self.__version

    def has_file_server(self):
        """Check if service has a file server.

        :rtype: bool

        """

        return self.__payload.get('files', False)

    def get_actions(self):
        """Get Service action names.

        :rtype: list

        """

        return list(self.__actions.keys())

    def has_action(self, name):
        """Check if an action exists for current Service schema.

        :param name: Action name.
        :type name: str

        :rtype: bool

        """

        return name in self.__actions

    def get_action_schema(self, name):
        """Get schema for an action.

        :param name: Action name.
        :type name: str

        :raises: ServiceSchemaError

        :rtype: ActionSchema

        """

        if not self.has_action(name):
            error = 'Cannot resolve schema for action: {}'.format(name)
            raise ServiceSchemaError(error)

        return ActionSchema(name, self.__actions[name])

    def get_http_schema(self):
        """Get HTTP Service schema.

        :rtype: HttpServiceSchema

        """

        return HttpServiceSchema(self.__payload.get('http', {}))


class HttpServiceSchema(object):
    """HTTP semantics of a Service schema in the framework."""

    def __init__(self, payload):
        self.__payload = Payload(payload)

    def is_accessible(self):
        """Check if the Gateway has access to the Service.

        :rtype: bool

        """

        return self.__payload.get('gateway', True)

    def get_base_path(self):
        """Get base HTTP path for the Service.

        :rtype: str

        """

        return self.__payload.get('base_path', '')
