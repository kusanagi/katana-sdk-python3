from urllib.parse import urlparse

from ..utils import MultiDict

from .base import Api
from .response import Response
from .transport import Transport


class Request(Api):
    """Request API class for Middleware component."""

    def __init__(self, method, url, *args, **kwargs):
        self.__method = method.upper()
        self.__url = url
        self.__protocol_version = kwargs.pop('protocol_version', None) or '1.1'
        self.__query = kwargs.pop('query', None) or MultiDict()
        self.__headers = kwargs.pop('headers', None) or MultiDict()
        self.__post_data = kwargs.pop('post_data', None) or MultiDict()
        self.__body = kwargs.pop('body', None) or ''
        self.__files = kwargs.pop('files', None) or MultiDict()

        # Save parsed URL
        self.__parsed_url = urlparse(self.get_url())

        self.set_service_name(kwargs.pop('service_name', None) or '')
        self.set_service_version(kwargs.pop('service_version', None) or '')
        self.set_action_name(kwargs.pop('action_name', None) or '')

        super().__init__(*args, **kwargs)

    def is_method(self, method):
        """Determine if the request used the given HTTP method.

        Returns True if the HTTP method of the request is the same
        as the specified method, otherwise False.

        :param method: The HTTP method.
        :type method: str

        :rtype: bool

        """

        return self.__method == method.upper()

    def get_method(self):
        """Gets the HTTP method.

        Returns the HTTP method used for the request.

        :returns: The HTTP method.
        :rtype: str

        """

        return self.__method

    def get_url(self):
        """Get request URL.

        :rtype: str

        """

        return self.__url

    def get_url_scheme(self):
        """Get request URL scheme.

        :rtype: str

        """

        return self.__parsed_url.scheme

    def get_url_host(self):
        """Get request URL host.

        When a port is given in the URL it will be added to host.

        :rtype: str

        """

        return self.__parsed_url.netloc

    def get_url_path(self):
        """Get request URL path.

        :rtype: str

        """

        return self.__parsed_url.path.rstrip('/')

    def has_query_param(self, name):
        """Determines if the param is defined.

        Returns True if the param is defined in the HTTP query string,
        otherwise False.

        :param name: The HTTP param.
        :type name: str

        :rtype: bool

        """

        return name in self.__query

    def get_query_params(self):
        """Get all HTTP query params.

        :returns: The HTTP params.
        :rtype: `MultiDict`

        """

        return self.__query

    def get_query_param(self, name, default=''):
        """Gets a param from the HTTP query string.

        Returns the param from the HTTP query string with the given
        name, or and empty string if not defined.

        :param name: The param from the HTTP query string.
        :type name: str

        :param default: The optional default value.
        :type name: str

        :returns: The HTTP param.
        :rtype: str

        """

        return self.__query.get(name, (default, ))[0]

    def has_post_param(self, name):
        """Determines if the param is defined.

        Returns True if the param is defined in the HTTP post data,
        otherwise False.

        :param name: The HTTP param.
        :type name: str

        :rtype: bool

        """

        return name in self.__post_data

    def get_post_params(self):
        """Get all HTTP post params.

        :returns: The HTTP post params.
        :rtype: `MultiDict`

        """

        return self.__post_data

    def get_post_param(self, name, default=''):
        """Gets a param from the HTTP post data.

        Returns the param from the HTTP post data with the given
        name, or and empty string if not defined.

        :param name: The param from the HTTP post data.
        :type name: str

        :param default: The optional default value.
        :type name: str

        :returns: The HTTP param.
        :rtype: str

        """

        return self.__post_data.get(name, (default, ))[0]

    def is_protocol_version(self, version):
        """Determine if the request used the given HTTP version.

        Returns True if the HTTP version of the request is the same
        as the specified protocol version, otherwise False.

        :param version: The HTTP version.
        :type version: str

        :rtype: bool

        """

        return self.__protocol_version == version

    def get_protocol_version(self):
        """Gets the HTTP version.

        Returns the HTTP version used for the request.

        :returns: The HTTP version.
        :rtype: str

        """

        return self.__protocol_version

    def has_header(self, name):
        """Determines if the HTTP header is defined.

        Returns True if the HTTP header is defined, otherwise False.

        :param name: The HTTP header.
        :type name: str

        :rtype: bool

        """

        return name in self.__headers

    def get_header(self, name, default=''):
        """Get an HTTP header.

        Returns the HTTP header with the given name, or and empty
        string if not defined.

        A comma separated list of values ir returned when header
        has multiple values.

        :param name: The HTTP header.
        :type name: str

        :returns: The HTTP header value.
        :rtype: str

        """

        if not self.has_header(name):
            return default

        return ', '.join(self.__headers[name])

    def get_headers(self):
        """Get all HTTP headers.

        :returns: The HTTP headers.
        :rtype: `MultiDict`

        """

        return self.__headers

    def has_body(self):
        """Determines if the HTTP request body has content.

        Returns True if the HTTP request body has content, otherwise False.

        :rtype: bool

        """

        return self.__body != ''

    def get_body(self):
        """Gets the HTTP request body.

        Returns the body of the HTTP request, or and empty string if
        no content.

        :returns: The HTTP request body.
        :rtype: str

        """

        return self.__body

    def has_files(self):
        """Determines if there were files uploaded.

        Returns True if the HTTP request included file uploads,
        otherwise False.

        :rtype: bool

        """

        return len(self.__files) > 0

    def get_files(self):
        """Gets the uploaded files.

        Returns the files uploaded with the HTTP request, or an empty object.

        :returns: The uploaded files.
        :rtype: `MultiDict`

        """

        return self.__files

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

        """

        self.__service_name = service

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

        """

        self.__service_version = version

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

        """

        self.__action_name = action

    def new_response(self, status_code, status_text):
        """Create a new Response object.

        :param status_code: The HTTP status code.
        :type status_code: int
        :param status_text: The HTTP status text.
        :type status_text: str

        :returns: The response object.
        :rtype: `Response`

        """

        return Response(
            status_code,
            status_text,
            Transport({}),
            self.get_path(),
            self.get_name(),
            self.get_version(),
            self.get_platform_version(),
            )
