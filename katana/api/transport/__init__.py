"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ...payload import get_path
from ...payload import Payload
from ..base import ApiError
from ..file import payload_to_file

from .call import Caller
from .data import ServiceData
from .error import Error
from .link import Link
from .relation import Relation
from .transaction import Transaction

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"

EMPTY = object()


class TransactionTypeError(ApiError):
    """Error raised for invalid transaction types."""

    message = 'Unknown transaction type provided: "{}"'

    def __init__(self, type):
        super().__init__(self.message.format(type))


class Transport(object):
    """
    The Transport class encapsulates the Transport object.

    It provides read-only access to response Middleware.

    """

    def __init__(self, payload):
        self.__transport = Payload(payload)

    def get_request_id(self):
        """
        Get the request UUID.

        :rtype: str

        """

        return self.__transport.get('meta/id')

    def get_request_timestamp(self):
        """
        Get the request creation timestamp.

        :rtype: str

        """

        return self.__transport.get('meta/datetime')

    def get_origin_service(self):
        """
        Get the origin of the request.

        Result is an array containing name, version and action
        of the Service that was the origin of the request.

        :rtype: tuple

        """

        return tuple(self.__transport.get('meta/origin', []))

    def get_origin_duration(self):
        """
        Get the Service execution time in milliseconds.

        This time is the number of milliseconds spent by the Service
        that was the origin of the request.

        :rtype: int

        """

        return self.__transport.get('meta/duration', 0)

    def get_property(self, name, default=EMPTY):
        """
        Get a userland property value.

        The name of the property is case sensitive.

        An empty string is returned when a property with the specified
        name does not exist, and no default value is provided.

        :rtype: str

        """

        if default == EMPTY:
            default = ''
        elif not isinstance(default, str):
            raise TypeError('Default value must be a string')

        return self.__transport.get('meta/properties/{}'.format(name), default)

    def get_properties(self):
        """
        Get all the properties defined in the Transport.

        :rtype: dict

        """

        return self.__transport.get('meta/properties', {})

    def has_download(self):
        """
        Check if a file download has been registered for the response.

        :rtype: bool

        """

        return self.__transport.path_exists('body')

    def get_download(self):
        """
        Get the file download defined for the response.

        :rtype: `File`

        """

        if self.has_download():
            return payload_to_file(self.__transport.get('body'))

    def get_data(self):
        """
        Get the Transport data.

        An empty list is returned when there is no data in the Transport.

        :returns: A list of `SeviceData`.
        :rtype: list

        """

        data = []
        transport_data = self.__transport.get('data', {})
        if not transport_data:
            return data

        for address, services in transport_data.items():
            for svc, versions in services.items():
                for ver, actions in versions.items():
                    data.append(ServiceData(address, svc, ver, actions))

        return data

    def get_relations(self):
        """
        Get the Service relations.

        An empty list is returned when there are no relations defined
        in the Transport.

        :returns: A list of `Relation`.
        :rtype: list

        """

        relations = []
        data = self.__transport.get('relations', {})
        if not data:
            return relations

        for address, services in data.items():
            for name, pks in services.items():
                for pk, foreign_services in pks.items():
                    relations.append(
                        Relation(address, name, pk, foreign_services)
                        )

        return relations

    def get_links(self):
        """
        Get the Service links.

        An empty list is returned when there are no links defined
        in the Transport.

        :returns: A list of `Link`.
        :rtype: list

        """

        links = []
        data = self.__transport.get('links', {})
        if not data:
            return links

        for address, services in data.items():
            for name, references in services.items():
                for ref, uri in references.items():
                    links.append(Link(address, name, ref, uri))

        return links

    def get_calls(self):
        """
        Get the Service calls.

        An empty list is returned when there are no calls defined
        in the Transport.

        :returns: A list of `Caller`.
        :rtype: list

        """

        calls = []
        data = self.__transport.get('calls', {})
        if not data:
            return calls

        for service, versions in data.items():
            for version, service_calls in versions.items():
                for call_data in service_calls:
                    action = get_path(call_data, 'caller', '')
                    calls.append(Caller(service, version, action, call_data))

        return calls

    def get_transactions(self, type):
        """
        Get the transactions

        The transaction type is case sensitive, and supports "commit",
        "rollback" or "complete" as value.
        An exception is raised when the type is not valid.

        An empty list is returned when there are no transactions
        defined in the Transport.

        :raises: TransactionTypeError

        :returns: A list of `Transaction`.
        :rtype: list

        """

        if type not in ('commit', 'rollback', 'complete'):
            raise TransactionTypeError(type)

        data = self.__transport.get('transactions/{}'.format(type), {})
        if not data:
            return []

        return [Transaction(type, tr_data) for tr_data in data]

    def get_errors(self):
        """
        Get Transport errors.

        An empty list is returned when there are no errors
        defined in the Transport.

        :returns: A list of `Error`.
        :rtype: list

        """

        errors = []
        data = self.__transport.get('errors', {})
        if not data:
            return errors

        for address, services in data.items():
            for name, versions in services.items():
                for version, error_data in versions.items():
                    for data in error_data:
                        errors.append(Error(address, name, version, data))

        return errors
