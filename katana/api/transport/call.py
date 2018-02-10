"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ...payload import Payload
from ..param import payload_to_param

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class Caller(object):
    """Represents a Service which registered call in the Transport."""

    def __init__(self, service, version, action, call_data):
        self.__service = service
        self.__version = version
        self.__action = action
        self.__call_data = call_data

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

    def get_action(self):
        """
        Get the name of the Service action.

        :rtype: str

        """

        return self.__action

    def get_callee(self):
        """
        Get the callee info for the Service being called.

        :rtype: `Callee`

        """

        return Callee(self.__call_data)


class Callee(object):
    """Represents a callee Service call info."""

    def __init__(self, call_data):
        self.__data = Payload(call_data)

    def get_duration(self):
        """
        Get the duration of the call in milliseconds.

        :rtype: int

        """

        return self.__data.get('duration', 0)

    def is_remote(self):
        """
        Check if the call is to a Service in another Realm.

        :rtype: bool

        """

        return self.__data.path_exists('gateway')

    def get_address(self):
        """
        Get the remote Gateway address.

        :rtype: str

        """

        return self.__data.get('gateway', '')

    def get_name(self):
        """
        Get the name of the Service.

        :rtype: str

        """

        return self.__data.get('name', '')

    def get_version(self):
        """
        Get the Service version.

        :rtype: str

        """

        return self.__data.get('version', '')

    def get_action(self):
        """
        Get the name of the Service action.

        :rtype: str

        """

        return self.__data.get('action', '')

    def get_params(self):
        """
        Get the call parameters.

        An empty list is returned when there are no parameters
        defined for the call.

        :returns: A list of `Param`.
        :rtype: list

        """

        return [
            payload_to_param(payload)
            for payload in self.__data.get('params', [])
            ]
