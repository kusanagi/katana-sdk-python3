"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import logging
import types

from .schema.service import ServiceSchema
from .. import json
from ..errors import KatanaError
from ..schema import get_schema_registry


class ApiError(KatanaError):
    """Exception class for API errors."""


def value_to_log_string(value, max_chars=100000):
    """Convert a value to a string.

    :param value: A value to log.
    :type value: object
    :param max_chars: Optional maximum number of characters to return.
    :type max_chars: int

    :rtype: str

    """

    if value is None:
        output = 'NULL'
    elif isinstance(value, bool):
        output = 'TRUE' if value else 'FALSE'
    elif isinstance(value, str):
        output = value
    elif isinstance(value, bytes):
        output = value.decode('utf8')
    elif isinstance(value, (dict, list, tuple)):
        output = json.serialize(value, prettify=True).decode('utf8')
    elif isinstance(value, types.FunctionType):
        if value.__name__ == '<lambda>':
            output = 'anonymous'
        else:
            output = '[function {}]'.format(value.__name__)
    else:
        output = repr(value)

    return output[:max_chars]


class Api(object):
    """Base API class for SDK components."""

    def __init__(self, component, path, name, version, platform_version, **kw):
        self.__component = component
        self.__path = path
        self.__name = name
        self.__version = version
        self.__platform_version = platform_version
        self.__variables = kw.get('variables') or {}
        self.__debug = kw.get('debug', False)
        self.__schema = get_schema_registry()

        # Logging is only enabled when debug is True
        if self.__debug:
            self.__logger = logging.getLogger('katana.api')

    def is_debug(self):
        """Determine if component is running in debug mode.

        :rtype: bool

        """

        return self.__debug

    def get_platform_version(self):
        """Get KATANA platform version.

        :rtype: str

        """

        return self.__platform_version

    def get_path(self):
        """Get source file path.

        Returns the path to the endpoint userland source file.

        :returns: Source path file.
        :rtype: str

        """

        return self.__path

    def get_name(self):
        """Get component name.

        :rtype: str

        """

        return self.__name

    def get_version(self):
        """Get component version.

        :rtype: str

        """

        return self.__version

    def get_variables(self):
        """Gets all component variables.

        :rtype: dict

        """

        return self.__variables

    def get_variable(self, name):
        """Get a single component variable.

        :param name: Variable name.
        :type name: str

        :rtype: str

        """

        return self.__variables.get(name, '')

    def has_resource(self, name):
        """Check if a resource name exist.

        :param name: Name of the resource.
        :type name: str

        :rtype: bool

        """

        return self.__component.has_resource(name)

    def get_resource(self, name):
        """Get a resource.

        :param name: Name of the resource.
        :type name: str

        :raises: ComponentError

        :rtype: object

        """

        return self.__component.get_resource(name)

    def get_service_schema(self, name, version):
        """Get service schema.

        :param name: Service name.
        :type name: str
        :param version: Service version.
        :type version: str

        :raises: ApiError

        :rtype: ServiceSchema

        """

        payload = self.__schema.get('{}/{}'.format(name, version), None)
        if not payload:
            error = 'Cannot resolve schema for Service: "{}" ({})'
            raise ApiError(error.format(name, version))

        return ServiceSchema(name, version, payload)

    def log(self, value):
        """Write a value to KATANA logs.

        Given value is converted to string before being logged.

        Output is truncated to have a maximum of 100000 characters.

        """

        if self.__logger:
            self.__logger.debug(value_to_log_string(value))
