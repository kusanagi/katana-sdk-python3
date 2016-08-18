from ..payload import Payload

from .file import File


class Transport(object):
    """Endpoint transport class."""

    def __init__(self, payload):
        self.__transport = Payload(payload)

    def get_request_id(self):
        """Gets the request ID.

        Returns the request ID of the Transport.

        :returns: The request ID.
        :rtype: str.

        """

        return self.__transport.get('meta/id')

    def get_request_timestamp(self):
        """Gets the request ID.

        Returns the request ID of the Transport.

        :returns: The request ID.
        :rtype: str.

        """

        return self.__transport.get('meta/datetime')

    def get_origin(self):
        """Gets the request ID.

        Returns the request ID of the Transport.

        :returns: The request ID.
        :rtype: str.

        """

        return self.__transport.get('meta/origin', '')

    def get_property(self, name):
        """Gets the request ID.

        Returns the request ID of the Transport.

        :returns: The property value.
        :rtype: str.

        """

        return self.__transport.get('meta/userland/{}'.format(name), '')

    def has_download(self):
        """Determines if a download has been registered.

        Returns True if a download has been registered, otherwise False.

        :rtype: bool.

        """

        return self.__transport.path_exists('body')

    def get_download(self):
        """Gets the download from the Transport.

        Return the download from the Transport as a File object.

        :returns: The File object.
        :rtype: File.

        """

        return File(
            self.__transport.get('body/name'),
            self.__transport.get('body/filename'),
            self.__transport.get('body/size'),
            self.__transport.get('body/mime'),
            self.__transport.get('body/path'),
            )

    def get_data(self, service=None):
        """Gets the data from the Transport.

        Return all of the data as an object, as it is stored in the Transport.

        If the service is specified, it only returns the data stored by that
        service.

        :param service: The optional service.
        :type service: str.

        :returns: The data from the Transport.
        :rtype: object.

        """

        data = self.__transport.get('data')
        if service:
            return data.get(service, {})

        return data

    def get_relations(self, service=None):
        """Gets the relations from the Transport.

        Return all of the relations as an object, as they are stored in the
        Transport. If the service is specified, it only returns the relations
        stored by that service.

        :param service: The optional service.
        :type service: str.

        :returns: The relations from the Transport.
        :rtype: object.

        """

        relations = self.__transport.get('relations')
        if service:
            return relations.get(service, {})

        return relations

    def get_links(self, service=None):
        """Gets the links from the Transport.

        Return all of the links as an object, as they are stored in the
        Transport. If the service is specified, it only returns the links
        stored by that service.

        :param service: The optional service.
        :type service: str.

        :returns: The links from the Transport.
        :rtype: object.

        """

        links = self.__transport.get('links')
        if service:
            return links.get(service, {})

        return links

    def get_calls(self, service=None):
        """Gets the calls from the Transport.

        Return all of the internal calls to Services as an object, as
        they are stored in the Transport. If the service is specified,
        it only returns the calls performed by that service.

        :param service: The optional service.
        :type service: str.

        :returns: The calls from the Transport.
        :rtype: object.

        """

        calls = self.__transport.get('calls')
        if service:
            return calls.get(service, {})

        return calls

    def get_transactions(self, service=None):
        """Gets the transactions from the Transport.

        Return all of the internal Service transactions as an object, as
        they are stored in the Transport. If the service is specified,
        it only returns the transactions registered by that service. Note
        that at this point the registered transactions have already been
        executed by the Gateway.

        :param service: The optional service.
        :type service: str.

        :returns: The transactions from the Transport.
        :rtype: object.

        """

        transactions = self.__transport.get('transactions')
        if service:
            return transactions.get(service, {})

        return transactions

    def get_errors(self, service=None):
        """Gets the errors from the Transport.

        Return all of the Service errors as an object, as they
        are stored in the Transport. If the service is specified,
        it only returns the errors registered by that service.

        :param service: The optional service.
        :type service: str.

        :returns: The errors from the Transport.
        :rtype: object.

        """

        errors = self.__transport.get('errors')
        if service:
            return errors.get(service, {})

        return errors