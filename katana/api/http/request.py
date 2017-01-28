"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from itertools import chain
from urllib.parse import urlparse

from ..file import File
from ...utils import MultiDict

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class HttpRequest(object):
    """HTTP request class."""

    def __init__(self, method, url, **kwargs):
        super().__init__()
        self.__method = method.upper()
        self.__url = url
        self.__protocol_version = kwargs.get('protocol_version') or '1.1'
        self.__query = kwargs.get('query') or MultiDict()
        self.__headers = kwargs.get('headers') or MultiDict()
        self.__post_data = kwargs.get('post_data') or MultiDict()
        self.__body = kwargs.get('body') or ''
        self.__files = kwargs.get('files') or MultiDict()

        # Save parsed URL
        self.__parsed_url = urlparse(self.get_url())

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

    def get_query_param(self, name, default=''):
        """Gets a param from the HTTP query string.

        Returns the param from the HTTP query string with the given
        name, or and empty string if not defined.

        :param name: The param from the HTTP query string.
        :type name: str
        :param default: The optional default value.
        :type name: str

        :returns: The HTTP param value.
        :rtype: str

        """

        return self.__query.get(name, (default, ))[0]

    def get_query_param_array(self, name, default=None):
        """Gets a param from the HTTP query string.

        Parameter is returned as a list of values.

        :param name: The param from the HTTP query string.
        :type name: str
        :param default: The optional default value.
        :type default: list

        :returns: The HTTP param values as a list.
        :rtype: list

        """

        return self.__query.get(name, default or [])

    def get_query_params(self):
        """Get all HTTP query params.

        :returns: The HTTP params.
        :rtype: dict

        """

        return {key: value[0] for key, value in self.__query.items()}

    def get_query_params_array(self):
        """Get all HTTP query params.

        Each parameter value is returned as a list.

        :returns: The HTTP params.
        :rtype: `MultiDict`

        """

        return self.__query

    def has_post_param(self, name):
        """Determines if the param is defined.

        Returns True if the param is defined in the HTTP post data,
        otherwise False.

        :param name: The HTTP param.
        :type name: str

        :rtype: bool

        """

        return name in self.__post_data

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

    def get_post_param_array(self, name, default=None):
        """Gets a param from the HTTP post data.

        Parameter is returned as a list of values.

        :param name: The param from the HTTP post data.
        :type name: str
        :param default: The optional default value.
        :type default: list

        :returns: The HTTP param values as a list.
        :rtype: list

        """

        return self.__post_data.get(name, default or [])

    def get_post_params(self):
        """Get all HTTP post params.

        :returns: The HTTP post params.
        :rtype: dict

        """

        return {key: value[0] for key, value in self.__post_data.items()}

    def get_post_params_array(self):
        """Get all HTTP post params.

        Each parameter value is returned as a list.

        :returns: The HTTP post params.
        :rtype: `MultiDict`

        """

        return self.__post_data

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

        return self.__headers.get(name)[0]

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

    def has_file(self, name):
        """Check if a file was uploaded in current request.

        :param name: File name.
        :type name: str

        :rtype: bool

        """

        return name in self.__files

    def get_file(self, name):
        """Get an uploaded file.

        Returns the file uploaded with the HTTP request, or None.

        :param name: Name of the file.
        :type name: str

        :returns: The uploaded file.
        :rtype: `File`

        """

        if name in self.__files:
            # Get only the first file
            return self.__files.getone(name)
        else:
            return File(name, path='')

    def get_files(self):
        """Get uploaded files.

        Returns the files uploaded with the HTTP request.

        :returns: A list of `File` objects.
        :rtype: iter

        """

        # Fields might have more than one file uploaded for the same name,
        # there for it can happen that file names are duplicated.
        return chain.from_iterable(self.__files.values())
