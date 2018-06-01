"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ...payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class Error(object):
    """Represents an error object in the Transport."""

    def __init__(self, address, service, version, data):
        self.__address = address
        self.__service = service
        self.__version = version
        self.__data = Payload(data)

    def get_address(self):
        """
        Get the Gateway address of the Service.

        :rtype: str

        """

        return self.__address

    def get_name(self):
        """
        Get the name of the Service.

        :rtype: str

        """

        return self.__service

    def get_version(self):
        """
        Get the Service version.

        :rtype: str

        """

        return self.__version

    def get_message(self):
        """
        Get the error message.

        An empty string is returned when the error has no message.

        :rtype: str

        """

        return self.__data.get('message', '')

    def get_code(self):
        """
        Get the error code.

        A zero is returned when the error has no code.

        :rtype: int

        """

        return self.__data.get('code', 0)

    def get_status(self):
        """
        Get the status text for the error.

        An empty string is returned when the error has no status.

        :rtype: str

        """

        return self.__data.get('status', '')
