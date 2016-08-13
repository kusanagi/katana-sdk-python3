from ..utils import MultiDict

from .base import Api


class Response(Api):
    """Response API class for Middleware component."""

    def __init__(self, status, transport, *args, **kwargs):
        self.__transport = transport
        self.__headers = MultiDict()
        self.set_status(status)
        self.set_protocol_version(
            kwargs.pop('protocol_version', None) or '1.1'
            )
        self.set_body(kwargs.pop('body', None) or '')

        # Set response headers
        headers = kwargs.pop('headers', None)
        if headers:
            # Headers should be a list of tuples
            if isinstance(headers, dict):
                headers = headers.items()

            for name, value in headers:
                self.set_header(name, value)

        super().__init__(*args, **kwargs)

    def is_protocol_version(self, version):
        """Determine if the response uses the given HTTP version.

        :param version: The HTTP version.
        :type version: str.

        :rtype: bool.

        """

        return self.__protocol_version == version

    def get_protocol_version(self):
        """Get the HTTP version.

        :rtype: str.

        """

        return self.__protocol_version

    def set_protocol_version(self, version):
        """Set the HTTP version to the given protocol version.

        Sets the HTTP version of the response to the specified
        protocol version.

        :param version: The HTTP version.
        :type version: str.

        """

        self.__protocol_version = version

    def is_status(self, status):
        """Determine if the response uses the given status.

        :param status: The HTTP status.
        :type status: str.

        :rtype: bool.

        """

        return self.__status == status

    def get_status(self):
        """Get the HTTP status.

        :rtype: str.

        """

        return self.__status

    def set_status(self, status):
        """Set the HTTP status to the given status.

        Sets the status of the response to the specified status code.

        :param status: The HTTP status code.
        :type status: str.

        """

        self.__status = status

    # TODO: We need more methods. Discuss w/ @JW
    def get_status_code(self):
        """Get HTTP status code.

        :rtype: int.

        """

        return int(self.get_status()[:3])

    def has_header(self, name):
        """Determines if the HTTP header is defined.

        :param name: The HTTP header name.
        :type name: str.

        :rtype: bool.

        """

        return name in self.__headers

    def get_header(self, name):
        """Get an HTTP header.

        :param name: The HTTP header.
        :type name: str.

        :rtype: str.

        """

        self.__headers.get(name)

    def set_header(self, name, value):
        """Set a HTTP with the given name and value.

        Sets a header in the HTTP response with the specified name and value.

        :param name: The HTTP header.
        :type name: str.
        :param value: The header value.
        :type value: str.

        """

        self.__headers[name] = value

    def get_headers(self):
        """Get all HTTP header.

        :rtype: MultiDict.

        """

        return self.__headers

    def has_body(self):
        """Determines if the response has content.

        Returns True if the HTTP response body has content, otherwise False.

        :rtype: bool.

        """

        return self.__body != ''

    def get_body(self):
        """Gets the response body.

        :returns: The HTTP response body.
        :rtype: str.

        """

        return self.__body

    def set_body(self, content=''):
        """Set the content of the HTTP response.

        Sets the content of the body of the HTTP response with
        the specified content.

        :param content: The content for the HTTP response body.
        :type content: str.

        """

        self.__body = content

    def get_transport(self):
        """Gets the Transport object.

        Returns the Transport object returned by the Services.

        :rtype: Transport.

        """

        return self.__transport
