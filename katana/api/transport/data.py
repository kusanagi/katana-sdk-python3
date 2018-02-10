"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class ServiceData(object):
    """Represents a Service which stored data in the Transport."""

    def __init__(self, address, service, version, actions):
        self.__address = address
        self.__service = service
        self.__version = version
        self.__actions = actions

    def get_address(self):
        """
        Get the Gateway address of the Service.

        :rtype: str

        """

        return self.__address

    def get_name(self):
        """
        Get the Service name.

        :rtype: str

        """

        return self.__service

    def get_version(self):
        """
        Get the Service version.

        :rtype: str

        """

        return self.__version

    def get_actions(self):
        """
        Get the list of action data items for current service.

        Each item represents an action on the Service for which data exists.
        The data is added all the calls to this service.

        :returns: A list of `ActionData`.
        :rtype: list

        """

        return [
            ActionData(name, call_data)
            for name, call_data in self.__actions.items()
            ]


class ActionData(object):
    """The ActionData class represents action data in the Transport."""

    def __init__(self, name, data):
        self.__name = name
        self.__data = data

    def get_name(self):
        """
        Get the name of the Service action that returned the data.

        :rtype: str

        """

        return self.__name

    def is_collection(self):
        """
        Checks if the data for this action is a collection.

        :rtype: bool

        """

        return isinstance(self.__data[0], list)

    def get_data(self):
        """
        Get the Transport data for the Service action.

        Each item in the list represents a call that included data
        in the Transport, where each item may be a list or an object,
        depending on whether the data is a collection or not.

        :returns: A list of list, or a list of dict.
        :rtype: list

        """

        return self.__data
