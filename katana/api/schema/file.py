"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import logging
import sys

from ...payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

LOG = logging.getLogger(__name__)


class FileSchema(object):
    """File parameter schema in the platform."""

    def __init__(self, name, payload):
        self.__name = name
        self.__payload = Payload(payload)

    def get_name(self):
        """Get file parameter name.

        :rtype: str

        """

        return self.__name

    def get_mime(self):
        """Get mime type.

        :rtype: str

        """

        return self.__payload.get('mime', 'text/plain')

    def is_required(self):
        """Check if file parameter is required.

        :rtype: bool

        """

        return self.__payload.get('required', False)

    def get_max(self):
        """Get minimum file size allowed for the parameter.

        Returns 0 if not defined.

        :rtype: int

        """

        return self.__payload.get('maximum', sys.maxsize)

    def is_exclusive_max(self):
        """Check if maximum size is inclusive.

        When max is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('maximum'):
            return False

        return self.__payload.get('exclusive_maximum', False)

    def get_min(self):
        """Get minimum file size allowed for the parameter.

        Returns 0 if not defined.

        :rtype: int

        """

        return self.__payload.get('minimum', 0)

    def is_exclusive_min(self):
        """Check if minimum size is inclusive.

        When min is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('minimum'):
            return False

        return self.__payload.get('exclusive_minimum', False)

    def get_http_schema(self):
        """Get HTTP file param schema.

        :rtype: HttpFileSchema

        """

        return HttpFileSchema(self.get_name(), self.__payload.get('http', {}))


class HttpFileSchema(object):
    """HTTP semantics of a file parameter schema in the platform."""

    def __init__(self, name, payload):
        self.__name = name
        self.__payload = Payload(payload)

    def is_accessible(self):
        """Check if the Gateway has access to the parameter.

        :rtype: bool

        """

        return self.__payload.get('gateway', True)

    def get_param(self):
        """Get name as specified via HTTP to be mapped to the name property.

        :rtype: str

        """

        return self.__payload.get('param', self.__name)
