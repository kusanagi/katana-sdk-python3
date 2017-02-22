"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import logging

from .schema.service import ServiceSchema
from ..errors import KatanaError
from ..logging import value_to_log_string
from ..schema import get_schema_registry
from ..versions import VersionString

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class ApiError(KatanaError):
    """Exception class for API errors."""


class Api(object):
    """Base API class for SDK components."""

    def __init__(self, component, path, name, version, framework_version, **kw):
        self.__path = path
        self.__name = name
        self.__version = version
        self.__framework_version = framework_version
        self.__variables = kw.get('variables') or {}
        self.__debug = kw.get('debug', False)
        self._schema = get_schema_registry()
        self._component = component

        # Logging is only enabled when debug is True
        if self.__debug:
            self.__logger = logging.getLogger('katana.api')
        else:
            self.__logger = None

    def is_debug(self):
        """Determine if component is running in debug mode.

        :rtype: bool

        """

        return self.__debug

    def get_framework_version(self):
        """Get KATANA framework version.

        :rtype: str

        """

        return self.__framework_version

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

        return self._component.has_resource(name)

    def get_resource(self, name):
        """Get a resource.

        :param name: Name of the resource.
        :type name: str

        :raises: ComponentError

        :rtype: object

        """

        return self._component.get_resource(name)

    def get_services(self):
        """Get service names and versions.

        :rtype: list

        """

        services = []
        for name in self._schema.get_service_names():
            for version in self._schema.get(name).keys():
                services.append({'name': name, 'version': version})

        return services

    def get_service_schema(self, name, version):
        """Get service schema.

        Service version string may contain many `*` that will be
        resolved to the higher version available. For example: `1.*.*`.

        :param name: Service name.
        :type name: str
        :param version: Service version string.
        :type version: str

        :raises: ApiError

        :rtype: ServiceSchema

        """

        # Resolve service version when wildcards are used
        if '*' in version:
            try:
                version = VersionString(version).resolve(
                    self._schema.get(name, {}).keys()
                    )
                payload = self._schema.get('{}/{}'.format(name, version), None)
            except KatanaError:
                payload = None
        else:
            payload = self._schema.get('{}/{}'.format(name, version), None)

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
