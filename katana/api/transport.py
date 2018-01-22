"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ..payload import get_path
from ..payload import Payload

from .file import payload_to_file

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class Transport(object):
    """Endpoint transport class."""

    def __init__(self, payload):
        self.__transport = Payload(payload)

    def get_request_id(self):
        """Gets the request ID.

        Returns the request ID of the Transport.

        :returns: The request ID.
        :rtype: str

        """

        return self.__transport.get('meta/id')

    def get_request_timestamp(self):
        """Get request timestamp.

        :rtype: str

        """

        return self.__transport.get('meta/datetime')

    def get_origin_service(self):
        """Get transport origin service.

        Service origin is a list with origin name, version and action.

        :rtype: list

        """

        return self.__transport.get('meta/origin', [])

    def get_origin_duration(self):
        """Get origin Service execution time.

        The execution time in milliseconds is the time that was spent by
        the Service that was the origin of the request.

        :rtype: int

        """

        return self.__transport.get('meta/duration', 0)

    def get_property(self, name, default=''):
        """Get a userland property.

        :param name: Name of the property.
        :type name: str
        :param default: A default value to return when property is missing.
        :type default: str

        :rtype: str

        """

        if not isinstance(default, str):
            raise TypeError('Default value must be a string')

        return self.__transport.get('meta/properties/{}'.format(name), default)

    def get_properties(self):
        """Get userland properties.

        :rtype: dict

        """

        return self.__transport.get('meta/properties', {})

    def has_download(self):
        """Determines if a download has been registered.

        Returns True if a download has been registered, otherwise False.

        :rtype: bool

        """

        return self.__transport.path_exists('body')

    def get_download(self):
        """Gets the download from the Transport.

        Return the download from the Transport as a File object.

        :returns: The File object.
        :rtype: `File`

        """

        if self.has_download():
            return payload_to_file(self.__transport.get('body'))

    def get_data(self, address=None, service=None, version=None, action=None):
        """Get data from Transport.

        By default get all data from Transport.

        Data is returned as a list when all parameters are present, otherwise
        data is a dict.

        :param address: Optional public address of a Gateway.
        :type address: str
        :param service: Optional Service name.
        :type service: str
        :param version: Optional Service version.
        :type version: str
        :param action: Optional Service action name.
        :type action: str

        :returns: The Transport data.
        :rtype: object

        """

        data = self.__transport.get('data', {})
        for key in (address, service, version, action):
            if not key:
                break

            data = data.get(key, {})

        return data

    def get_relations(self, address=None, service=None):
        """Get relations from Transport.

        Return all of the relations as an object, as they are stored in the
        Transport. If the service is specified, it only returns the relations
        stored by that service.

        :param address: Optional public address of a Gateway.
        :type address: str
        :param service: Optional service name.
        :type service: str

        :returns: The relations from the Transport.
        :rtype: dict

        """

        relations = self.__transport.get('relations', {})
        for key in (address, service):
            if not key:
                break

            relations = relations.get(key, {})

        return relations

    def get_links(self, address=None, service=None):
        """Gets the links from the Transport.

        Return all of the links as an object, as they are stored in the
        Transport. If the service is specified, it only returns the links
        stored by that service.

        :param address: Optional public address of a Gateway.
        :type address: str
        :param service: Optional service name.
        :type service: str

        :returns: The links from the Transport.
        :rtype: dict

        """

        links = self.__transport.get('links', {})
        for key in (address, service):
            if not key:
                break

            links = links.get(key, {})

        return links

    def get_calls(self, address=None, service=None):
        """Gets the calls from the Transport.

        Return all of the internal calls to Services as an object, as
        they are stored in the Transport. If the service is specified,
        it only returns the calls performed by that service.

        :param address: Optional public address of a Gateway.
        :type address: str
        :param service: Optional service name.
        :type service: str

        :returns: The calls from the Transport.
        :rtype: dict

        """

        if address:
            has_calls = False
            result = {}
            for name, versions in self.__transport.get('calls', {}).items():
                # When a service name is given skip other services
                if service and service != name:
                    continue

                # Add service name to result
                if name not in result:
                    result[name] = {}

                # Filter calls by address in each service version
                for version, calls in versions.items():
                    result[name][version] = [
                        call for call in calls
                        if get_path(call, 'gateway', None) == address
                        ]
                    # Flag to know when calls exists for at least
                    # one service version.
                    if len(result[name][version]):
                        has_calls = True

            return result if has_calls else {}
        elif service:
            calls = self.__transport.get('calls/{}'.format(service), {})
            return {service: calls} if calls else {}
        else:
            return self.__transport.get('calls', {})

    def get_transactions(self, service=None):
        """Gets the transactions from the Transport.

        Return all of the internal Service transactions as an object, as
        they are stored in the Transport. If the service is specified,
        it only returns the transactions registered by that service. Note
        that at this point the registered transactions have already been
        executed by the Gateway.

        :param service: The optional service.
        :type service: str

        :returns: The transactions from the Transport.
        :rtype: dict

        """

        transactions = self.__transport.get('transactions', {})
        if service and transactions:
            # Get filtered transactions in a new object
            result = {}
            for action, items in transactions.items():
                # Filter transaction items by service name
                result[action] = [
                    item for item in items
                    if get_path(item, 'name') == service
                    ]
                # Remove action from results if its empty
                if not result[action]:
                    del result[action]

            return result

        return transactions

    def get_errors(self, address=None, service=None):
        """Gets the errors from the Transport.

        Return all of the Service errors as an object, as they
        are stored in the Transport. If the service is specified,
        it only returns the errors registered by that service.

        :param address: Optional public address of a Gateway.
        :type address: str
        :param service: Optional service name.
        :type service: str

        :returns: The errors from the Transport.
        :rtype: dict

        """

        errors = self.__transport.get('errors', {})
        for key in (address, service):
            if not key:
                break

            errors = errors.get(key, {})

        return errors
