"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ..errors import KatanaError
from ..logging import RequestLogger

from .base import Api
from .http.request import HttpRequest
from .http.response import HttpResponse

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"

NO_RETURN_VALUE = object()


class NoReturnValueDefined(KatanaError):
    """Raised when no return value is defined or available for a Service."""

    message = 'No return value defined on {} for action: "{}"'

    def __init__(self, service, version, action):
        server = '"{}" ({})'.format(service, version)
        super().__init__(self.message.format(server, action))


class Response(Api):
    """Response API class for Middleware component."""

    def __init__(self, transport, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = RequestLogger(kwargs.get('rid'), 'katana.api')
        self.__attributes = kwargs['attributes']
        self.__gateway_protocol = kwargs.get('gateway_protocol')
        self.__gateway_addresses = kwargs.get('gateway_addresses')

        http_request = kwargs.get('http_request')
        if http_request:
            self.__http_request = HttpRequest(**http_request)
        else:
            self.__http_request = None

        http_response = kwargs.get('http_response')
        if http_response:
            self.__http_response = HttpResponse(**http_response)
        else:
            self.__http_response = None

        self.__transport = transport
        self.__return_value = kwargs.get('return_value', NO_RETURN_VALUE)

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

    def get_http_request(self):
        """Get HTTP request for current request.

        :rtype: HttpRequest

        """

        return self.__http_request

    def get_http_response(self):
        """Get HTTP response for current request.

        :rtype: HttpResponse

        """

        return self.__http_response

    def has_return(self):
        """Check if there is a return value.

        Return value is available when the initial Service that is called
        has a return value, and returned a value in its command reply.

        :rtype: bool

        """

        return self.__return_value != NO_RETURN_VALUE

    def get_return_value(self):
        """Get the return value returned by the called Service.

        :raises: NoReturnValueDefined

        :rtype: object

        """

        if not self.has_return():
            transport = self.get_transport()
            origin = transport.get_origin_service()
            if not origin:
                # During testing there is no origin
                return

            raise NoReturnValueDefined(*origin)

        return self.__return_value

    def get_transport(self):
        """Gets the Transport object.

        Returns the Transport object returned by the Services.

        :rtype: `Transport`

        """

        return self.__transport

    def get_request_attribute(self, name, default=''):
        """
        Get a request attribute value.

        :param name: Attribute name.
        :type name: str
        :param default: Default value to use when attribute is not defined.
        :type default: str

        :raises: TypeError

        :rtype: str

        """

        return self.__attributes.get(name, default)

    def get_request_attributes(self):
        """
        Get all request attributes.

        :rtype: dict

        """

        return self.__attributes
