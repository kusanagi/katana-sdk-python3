"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ...utils import MultiDict

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class HttpResponse(object):
    """HTTP response class."""

    def __init__(self, status_code, status_text, *args, **kwargs):
        super().__init__()
        self.__headers = MultiDict()
        self.set_status(status_code, status_text)
        self.set_protocol_version(kwargs.get('protocol_version'))
        self.set_body(kwargs.get('body'))

        # Save header name mappings to avoid changing use setted header name
        self.__header_names = {}
        # Set response headers
        headers = kwargs.get('headers')
        if headers:
            # Headers should be a list of tuples
            if isinstance(headers, dict):
                headers = headers.items()

            for name, values in headers:
                for value in values:
                    self.set_header(name, value)

                # Save header name mapping
                self.__header_names[name.upper()] = name

    def is_protocol_version(self, version):
        """Determine if the response uses the given HTTP version.

        :param version: The HTTP version.
        :type version: str

        :rtype: bool

        """

        return self.__protocol_version == version

    def get_protocol_version(self):
        """Get the HTTP version.

        :rtype: str

        """

        return self.__protocol_version

    def set_protocol_version(self, version):
        """Set the HTTP version to the given protocol version.

        Sets the HTTP version of the response to the specified
        protocol version.

        :param version: The HTTP version.
        :type version: str

        :rtype: HttpResponse

        """

        self.__protocol_version = version or '1.1'
        return self

    def is_status(self, status):
        """Determine if the response uses the given status.

        :param status: The HTTP status.
        :type status: str

        :rtype: bool

        """

        return self.__status == status

    def get_status(self):
        """Get the HTTP status.

        :rtype: str

        """

        return self.__status

    def get_status_code(self):
        """Get HTTP status code.

        :rtype: int

        """

        return self.__status_code

    def get_status_text(self):
        """Get HTTP status text.

        :rtype: str

        """

        return self.__status_text

    def set_status(self, code, text):
        """Set the HTTP status to the given status.

        Sets the status of the response to the specified
        status code and text.

        :param code: The HTTP status code.
        :type code: int
        :param text: The HTTP status text.
        :type text: str

        :rtype: HttpResponse

        """

        self.__status_code = code
        self.__status_text = text
        self.__status = '{} {}'.format(code, text)
        return self

    def has_header(self, name):
        """Determines if the HTTP header is defined.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :type name: str

        :rtype: bool

        """

        return name.upper() in self.__header_names

    def get_header(self, name, default=''):
        """Get an HTTP header.

        Returns the HTTP header with the given name, or and empty
        string if not defined.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :type name: str
        :param default: The optional default value.
        :type default: str

        :returns: The HTTP header value.
        :rtype: str

        """

        # Get the header name with the original casing
        name = self.__header_names.get(name.upper(), name)

        values = self.__headers.get(name)
        if not values:
            return ''

        # Get first header value
        return values[0]

    def get_header_array(self, name, default=None):
        """Gets an HTTP header.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :type name: str
        :param default: The optional default value.
        :type default: list

        :raises: ValueError

        :returns: The HTTP header values as a list.
        :rtype: list

        """

        if default is None:
            default = []
        elif not isinstance(default, list):
            raise ValueError('Default value is not a list')

        # Get the header name with the original casing
        name = self.__header_names.get(name.upper(), name)
        return self.__headers.get(name, default)

    def get_headers(self):
        """Get all HTTP headers.

        :returns: The HTTP headers.
        :rtype: dict

        """

        return {key: value[0] for key, value in self.__headers.items()}

    def get_headers_array(self):
        """Get all HTTP headers.

        :returns: The HTTP headers.
        :rtype: `MultiDict`

        """

        return self.__headers

    def set_header(self, name, value):
        """Set a HTTP with the given name and value.

        Sets a header in the HTTP response with the specified name and value.

        :param name: The HTTP header.
        :type name: str
        :param value: The header value.
        :type value: str

        :rtype: HttpResponse

        """

        self.__headers[name] = value
        self.__header_names[name.upper()] = name
        return self

    def has_body(self):
        """Determines if the response has content.

        Returns True if the HTTP response body has content, otherwise False.

        :rtype: bool

        """

        return self.__body != ''

    def get_body(self):
        """Gets the response body.

        :returns: The HTTP response body.
        :rtype: str

        """

        return self.__body

    def set_body(self, content=None):
        """Set the content of the HTTP response.

        Sets the content of the body of the HTTP response with
        the specified content.

        :param content: The content for the HTTP response body.
        :type content: str

        :rtype: HttpResponse

        """

        self.__body = content or ''
        return self
