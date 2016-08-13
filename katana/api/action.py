from ..payload import ErrorPayload

from .base import Api
from .file import File
from .param import Param


def _new_payload_from_params(payload, params):
    if not params:
        return

    if not isinstance(params, list):
        raise TypeError('Parameters must be a list')

    for param in params:
        if not isinstance(param, Param):
            raise TypeError('Parameter must be an instance of Param class')
        else:
            payload[param.location][param.name] = param.value

    return payload


class Action(Api):
    """Action API class for Service component."""

    def __init__(self, action, params, transport, *args, **kwargs):
        self.__action = action
        self.__params = params
        self.__transport = transport
        super().__init__(*args, **kwargs)

    def is_origin(self):
        """Determines if the current service is the origin of the request.

        :rtype: bool.

        """

        return (
            self.__transport.get('meta/origin')
            == [self.get_name(), self.get_version()]
            )

    def set_property(self, name, value=''):
        """Sets a user land property.

        Sets a userland property in the transport with the given
        name and value.

        :param name: The property name.
        :type name: str.
        :param value: The property value.
        :type value: str.

        :rtype: bool.

        """

        return self.__transport.set(
            'meta/userland/{}'.format(name),
            str(value),
            )

    def get_action_name(self):
        """Gets the action name.

        :rtype: str.

        """

        return self.__action

    def get_param(self, location, name):
        """Gets a parameter passed to the action.

        Returns a Param object containing the parameter for the given location
        and name.

        Valid location values are "path", "query", "form-data", "header"
        and "body".

        :param location: The parameter location.
        :type location: str.
        :param name: The parameter name.
        :type name: str.

        :rtype: Param.

        """

        param_path = '{}/{}'.format(location, name)
        value = self.__params.get(param_path + '/value', None)
        return Param(
            location,
            name,
            value=value,
            datatype=self.__params.get(param_path + '/type', None),
            exists=self.__params.path_exists(param_path),
            )

    def new_param(self, location, name, value=None, datatype=None):
        """Creates a new parameter object.

        Creates an instance of Param with the given location and name, and
        optionally the value and data type. If the value is not provided then
        an empty string is assumed. If the data type is not defined then
        "string" is assumed.

        Valid location values are "path", "query", "form-data", "header"
        and "body".

        Valid data types are "null", "boolean", "integer", "float", "string",
        "array" and "object".

        :param location: The parameter location.
        :type location: str.
        :param name: The parameter name.
        :type name: str.
        :param value: The parameter value.
        :type value: mixed.
        :param datatype: The data type of the value.
        :type datatype: str.

        :rtype: Param.

        """

        if datatype and Param.resolve_type(value) != datatype:
            raise TypeError('Incorrect data type given for parameter value')
        else:
            datatype = Param.resolve_type(value)

        return Param(location, name, value, datatype, True)

    def set_download(self, file):
        """Sets a file as the download.

        Sets a File object as the file to be downloaded via the Gateway.

        :param file: The file object.
        :type file: File.

        :rtype: bool.

        """

        if not isinstance(file, File):
            raise TypeError('File must be an instance of File class')

        return self.__transport.set('body', file)

    def set_entity(self, entity):
        """Sets the entity data.

        Sets an object as the entity to be returned by the action.

        :param entity: The entity object.
        :type entity: dict.

        """

        if not isinstance(entity, dict):
            raise TypeError('Entity must be an dict')

        self.__transport.set('data', entity)

    def set_collection(self, collection):
        """Sets the collection data.

        Sets a list as the collection of entities to be returned by the action.

        :param collection: The collection list.
        :type collection: list.

        :rtype: bool.

        """

        if not isinstance(collection, list):
            raise TypeError('Collection must be a list')

        for entity in collection:
            if not isinstance(entity, dict):
                raise TypeError('Entity must be an dict')

        return self.__transport.set('data', collection)

    def relate_one(self, primary_key, service, foreign_key):
        """Creates a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity with the given
        primary key and service with the foreign key.

        :param primery_key: The primary key.
        :type primary_key: mixed.
        :param service: The foreign service.
        :type service: str.
        :param foreign_key: The foreign key.
        :type foreign_key: mixed.

        :rtype: bool.

        """

        return self.__transport.set(
            'relations/{}/{}/{}'.format(self.get_name(), primary_key, service),
            foreign_key
            )

    def relate_many(self, primary_key, service, foreign_keys):
        """Creates a "one-to-many" relation between entities.

        Creates a "one-to-many" relation between the entity with the given
        primary key and service with the foreign keys.

        :param primery_key: The primary key.
        :type primary_key: mixed.
        :param service: The foreign service.
        :type service: str.
        :param foreign_key: The foreign keys.
        :type foreign_key: list.

        :rtype: bool.

        """

        if not isinstance(foreign_keys, list):
            raise TypeError('Foreign keys must be a list')

        return self.__transport.set(
            'relations/{}/{}/{}'.format(self.get_name(), primary_key, service),
            foreign_keys
            )

    def set_link(self, link, uri):
        """Sets a link for the given URI.

        :param link: The link name.
        :type link: str.
        :param uri: The link URI.
        :type uri: str.

        :rtype: bool.

        """

        return self.__transport.set(
            'links/{}/{}'.format(self.get_name(), link),
            uri,
            )

    def transaction(self, action, params=None):
        """Registers a transaction for this service.

        :param action: The action name.
        :type action: str.
        :param params: The list of Param objects.
        :type params: list.

        :rtype: bool.

        """

        return self.__transport.push(
            'transactions/{}/{}/{}'.format(
                self.get_name(),
                self.get_version(),
                action
                ),
            _new_payload_from_params(params),
            )

    def call(self, service, version, action, params=None, files=None):
        """Registers a call to a service.

        :param service: The service name.
        :type service: str.
        :param version: The service version.
        :type version: str.
        :param action: The action name.
        :type action: str.
        :param params: The list of Param objects.
        :type params: list.
        :param files: The list of File objects.
        :type files: list.

        :rtype: bool.

        """

        return self.__transport.push(
            'calls/{}/{}/{}/{}/{}'.format(
                self.get_name(),
                self.get_version(),
                service,
                version,
                action
                ),
            _new_payload_from_params(params),
            )

    def error(self, message, code=None, status=None):
        """Adds an error for the current Service.

        Adds an error object to the Transport with the specified message.
        If the code is not set then 0 is assumed. If the status is not
        set then 500 Internal Server Error is assumed.

        :param message: The error message.
        :type message: str.
        :param code: The error code.
        :type code: int.
        :param status: The HTTP status message.
        :type status: str.

        :rtype: bool.

        """

        return self.__transport.push(
            'errors/{}/{}'.format(self.get_name(), self.get_version()),
            ErrorPayload.new(message, code, status),
            )
