"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import os

from ..payload import ErrorPayload
from ..payload import Payload

from .base import Api
from .file import File
from .file import file_to_payload
from .file import payload_to_file
from .param import Param


def parse_params(params):
    """Parse a list of parameters to be used in payloads.

    Each parameter is converted to a `Payload`.

    :param params: List of `Param` instances.
    :type params: list

    :returns: A list of `Payload`.
    :rtype: list

    """

    result = []
    if not params:
        return result

    if not isinstance(params, list):
        raise TypeError('Parameters must be a list')

    for param in params:
        if not isinstance(param, Param):
            raise TypeError('Parameter must be an instance of Param class')
        else:
            result.append(Payload().set_many({
                'location': param.get_location(),
                'name': param.get_name(),
                'value': param.get_value(),
                'type': param.get_type(),
                }))

    return result


class Action(Api):
    """Action API class for Service component."""

    def __init__(self, action, params, transport, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__action = action
        self.__params = params
        self.__transport = transport

        # Get files for current service, version and action
        path = 'files/{}/{}/{}'.format(
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            )
        self.__files = transport.get(path, default={})

    def is_origin(self):
        """Determines if the current service is the origin of the request.

        :rtype: bool

        """

        origin = self.__transport.get('meta/origin')
        return (origin == [self.get_name(), self.get_version()])

    def get_action_name(self):
        """Get the name of the action.

        :rtype: str

        """

        return self.__action

    def set_property(self, name, value):
        """Sets a user land property.

        Sets a userland property in the transport with the given
        name and value.

        :param name: The property name.
        :type name: str
        :param value: The property value.
        :type value: str

        :rtype: bool

        """

        if not isinstance(value, str):
            raise TypeError('Value is not a string')

        return self.__transport.set(
            'meta/properties/{}'.format(name),
            str(value),
            )

    def get_param(self, location, name):
        """Gets a parameter passed to the action.

        Returns a Param object containing the parameter for the given location
        and name.

        Valid location values are "path", "query", "form-data", "header"
        and "body".

        :param location: The parameter location.
        :type location: str
        :param name: The parameter name.
        :type name: str

        :rtype: `Param`

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
        :type location: str
        :param name: The parameter name.
        :type name: str
        :param value: The parameter value.
        :type value: mixed
        :param datatype: The data type of the value.
        :type datatype: str

        :rtype: `Param`

        """

        if datatype and Param.resolve_type(value) != datatype:
            raise TypeError('Incorrect data type given for parameter value')
        else:
            datatype = Param.resolve_type(value)

        return Param(location, name, value, datatype, True)

    def has_file(self, name):
        """Check if a file was provided for the action.

        :param name: File name.
        :type name: str

        :rtype: bool

        """

        return name in self.__files

    def get_file(self, name):
        """Get a file with a given name.

        :param name: File name.
        :type name: str

        :rtype: `File` or None

        """

        if self.has_file(name):
            return payload_to_file(name, self.__files[name])

    def new_file(self, name, path, mime=None):
        """Create a new file.

        :param name: File name.
        :type name: str
        :param path: File path.
        :type path: str
        :param mime: Optional file mime type.
        :type mime: str

        :rtype: `File`

        """

        if not path.startswith('file://'):
            path = 'file://{}'.format(path)

        # Initialize dynamic file values
        extra = {'filename': os.path.basename(path)}
        try:
            extra['size'] = os.path.getsize(path[7:])
            extra['exists'] = True
        except OSError:
            extra['size'] = None
            extra['exists'] = False

        return File(name, path, mime=mime, **extra)

    def set_download(self, file):
        """Set a file as the download.

        Sets a File object as the file to be downloaded via the Gateway.

        :param file: The file object.
        :type file: `File`

        :rtype: bool

        """

        if not isinstance(file, File):
            raise TypeError('File must be an instance of File class')

        return self.__transport.set('body', file_to_payload(file))

    def set_entity(self, entity):
        """Sets the entity data.

        Sets an object as the entity to be returned by the action.

        :param entity: The entity object.
        :type entity: dict

        """

        if not isinstance(entity, dict):
            raise TypeError('Entity must be an dict')

        return self.__transport.push(
            'data/{}/{}/{}'.format(
                self.get_name(),
                self.get_version(),
                self.get_action_name(),
                ),
            entity,
            )

    def set_collection(self, collection):
        """Sets the collection data.

        Sets a list as the collection of entities to be returned by the action.

        :param collection: The collection list.
        :type collection: list

        """

        if not isinstance(collection, list):
            raise TypeError('Collection must be a list')

        for entity in collection:
            if not isinstance(entity, dict):
                raise TypeError('Entity must be an dict')

        return self.__transport.push(
            'data/{}/{}/{}'.format(
                self.get_name(),
                self.get_version(),
                self.get_action_name(),
                ),
            collection,
            )

    def relate_one(self, primary_key, service, foreign_key):
        """Creates a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity with the given
        primary key and service with the foreign key.

        :param primery_key: The primary key.
        :type primary_key: mixed
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign key.
        :type foreign_key: mixed

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
        :type primary_key: mixed
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign keys.
        :type foreign_key: list

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
        :type link: str
        :param uri: The link URI.
        :type uri: str

        """

        return self.__transport.set(
            'links/{}/{}'.format(self.get_name(), link),
            uri,
            )

    def transaction(self, action, params=None):
        """Registers a transaction for this service.

        :param action: The action name.
        :type action: str
        :param params: The list of Param objects.
        :type params: list

        """

        return self.__transport.push(
            'transactions/{}/{}'.format(self.get_name(), self.get_version()),
            Payload.set_many({
                'action': action,
                'params': parse_params(params),
                })
            )

    def call(self, service, version, action, params=None, files=None):
        """Register a call to a service.

        :param service: The service name.
        :type service: str
        :param version: The service version.
        :type version: str
        :param action: The action name.
        :type action: str
        :param params: The list of Param objects.
        :type params: list
        :param files: The list of File objects.
        :type files: list

        """

        # Add files to transport
        if files:
            self.__transport.set(
                'files/{}/{}/{}'.format(service, version, action),
                {file.get_name(): file_to_payload(file) for file in files}
                )

        return self.__transport.push(
            'calls/{}/{}'.format(self.get_name(), self.get_version()),
            Payload().set_many({
                'name': service,
                'version': version,
                'action': action,
                'params': parse_params(params),
                })
            )

    def error(self, message, code=None, status=None):
        """Adds an error for the current Service.

        Adds an error object to the Transport with the specified message.
        If the code is not set then 0 is assumed. If the status is not
        set then 500 Internal Server Error is assumed.

        :param message: The error message.
        :type message: str
        :param code: The error code.
        :type code: int
        :param status: The HTTP status message.
        :type status: str

        """

        return self.__transport.push(
            'errors/{}/{}'.format(self.get_name(), self.get_version()),
            ErrorPayload.new(message, code, status),
            )
