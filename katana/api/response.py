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
from .http.response import HttpResponse


class Response(Api):
    """Response API class for Middleware component."""

    def __init__(self, transport, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def get_transport(self):
        """Gets the Transport object.

        Returns the Transport object returned by the Services.

        :rtype: `Transport`

        """

        return self.__transport
