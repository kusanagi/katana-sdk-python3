
"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ...payload import Payload
from ..param import payload_to_param

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class Transaction(object):
    """Represents a transaction object in the Transport."""

    def __init__(self, type, transaction_data):
        self.__type = type
        self.__data = Payload(transaction_data)

    def get_type(self):
        """
        Get the transaction type.

        The supported types are "commit", "rollback" or "complete".

        :rtype: str

        """

        return self.__type

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

    def get_caller_action(self):
        """
        Get the name of the Service action that registered the transaction.

        :rtype: str

        """

        return self.__data.get('caller', '')

    def get_callee_action(self):
        """
        Get the name of the action to be called by the transaction.

        :rtype: str

        """

        return self.__data.get('action', '')

    def get_params(self):
        """
        Get the transaction parameters.

        An empty list is returned when there are no parameters
        defined for the transaction.

        :returns: A list of `Param`.
        :rtype: list

        """

        return [
            payload_to_param(payload)
            for payload in self.__data.get('params', [])
            ]
