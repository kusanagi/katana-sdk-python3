"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

from .base import Api
from .http.request import HttpRequest
from .param import Param
from .param import param_to_payload
from .param import payload_to_param
from .response import Response
from .transport import Transport
from .. import urn
from ..payload import get_path
from ..payload import Payload


class Request(Api):
    """Request API class for Middleware component."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__gateway_protocol = kwargs.get('gateway_protocol')
        self.__gateway_addresses = kwargs.get('gateway_addresses')

        http_request = kwargs.get('http_request')
        if http_request:
            self.__http_request = HttpRequest(**http_request)
        else:
            self.__http_request = None

        # Save parameters by name as payloads
        self.__params = {
            get_path(param, 'name'): Payload(param)
            for param in (kwargs.get('params') or [])
            }

        self.set_service_name(kwargs.get('service_name', ''))
        self.set_service_version(kwargs.get('service_version', ''))
        self.set_action_name(kwargs.get('action_name', ''))

    def get_gateway_protocol(self):
        """Get the protocol implemented by the Gateway handling current request.

        :rtype: str

        """

        return self.__gateway_protocol

    def get_gateway_address(self):
        """Get public gateway address.

        :rtype: str

        """

        return self.__gateway_addresses[1]

    def get_service_name(self):
        """Get the name of the service.

        :rtype: str

        """

        return self.__service_name

    def set_service_name(self, service):
        """Set the name of the service.

        Sets the name of the service passed in the HTTP request.

        :param service: The service name.
        :type service: str

        :rtype: Request

        """

        self.__service_name = service or ''
        return self

    def get_service_version(self):
        """Get the version of the service.

        :type version: str

        """

        return self.__service_version

    def set_service_version(self, version):
        """Set the version of the service.

        Sets the version of the service passed in the HTTP request.

        :param version: The service version.
        :type version: str

        :rtype: Request

        """

        self.__service_version = version or ''
        return self

    def get_action_name(self):
        """Get the name of the action.

        :rtype: str

        """

        return self.__action_name

    def set_action_name(self, action):
        """Set the name of the action.

        Sets the name of the action passed in the HTTP request.

        :param action: The action name.
        :type action: str

        :rtype: Request

        """

        self.__action_name = action or ''
        return self

    def new_response(self, status_code=None, status_text=None):
        """Create a new Response object.

        Arguments `status_code` and `status_text` are used when Gateway
        protocol is `urn:katana:protocol:http`.

        :param status_code: Optional HTTP status code.
        :type status_code: int
        :param status_text: Optional HTTP status text.
        :type status_text: str

        :returns: The response object.
        :rtype: `Response`

        """

        http_response = None
        if self.get_gateway_protocol() == urn.HTTP:
            http_response = {
                'status_code': status_code or 200,
                'status_text': status_text or '200 OK',
                }

        return Response(
            self._component,
            Transport({}),
            self.get_path(),
            self.get_name(),
            self.get_version(),
            self.get_platform_version(),
            http_response=http_response,
            )

    def get_http_request(self):
        """Get HTTP request for current request.

        :rtype: HttpRequest

        """

        return self.__http_request

    def new_param(self, name, value=None, type=None):
        """Creates a new parameter object.

        Creates an instance of Param with the given name, and optionally
        the value and data type. If the value is not provided then
        an empty string is assumed. If the data type is not defined then
        "string" is assumed.

        Valid data types are "null", "boolean", "integer", "float", "string",
        "array" and "object".

        :param name: The parameter name.
        :type name: str
        :param value: The parameter value.
        :type value: mixed
        :param type: The data type of the value.
        :type type: str

        :raises: TypeError

        :rtype: Param

        """

        if type and Param.resolve_type(value) != type:
            raise TypeError('Incorrect data type given for parameter value')
        else:
            type = Param.resolve_type(value)

        return Param(name, value=value, type=type, exists=True)

    def set_param(self, param):
        """Add a new param for current request.

        :param param: The parameter.
        :type param: Param

        :rtype: Request

        """

        self.__params[param.get_name()] = param_to_payload(param)
        return self

    def has_param(self, name):
        """Check if a parameter exists.

        :param name: The parameter name.
        :type name: str

        :rtype: bool

        """

        return (name in self.__params)

    def get_param(self, name):
        """Get a request parameter.

        :param name: The parameter name.
        :type name: str

        :rtype: Param

        """

        if not self.has_param(name):
            return Param(name)

        return payload_to_param(self.__params[name])

    def get_params(self):
        """Get all request parameters.

        :rtype: list

        """

        return [
            payload_to_param(payload)
            for payload in self.__params.values()
            ]
