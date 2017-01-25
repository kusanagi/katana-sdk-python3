"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from ..payload import ErrorPayload
from ..payload import get_path
from ..payload import Payload
from ..utils import nomap

from .base import Api
from .base import ApiError
from .file import File
from .file import file_to_payload
from .file import payload_to_file
from .param import Param

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class NoFileServerError(ApiError):
    """Error raised when file server is not configured."""

    message = 'File server not configured: "{service}" ({version})'

    def __init__(self, service, version):
        self.service = service
        self.version = version
        super().__init__(self.message.format(service=service, version=version))


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
        self.__transport = transport
        self.__public_address = transport.get('meta/gateway')[1]
        self.__params = {
            get_path(param, 'name'): Payload(param)
            for param in params
            }

        # Get files for current service, version and action
        path = 'files|{}|{}|{}|{}'.format(
            self.__public_address,
            nomap(self.get_name()),
            self.get_version(),
            nomap(self.get_action_name()),
            )
        self.__files = transport.get(path, default={}, delimiter='|')

    def __files_to_payload(self, files):
        current_service = self.get_name()
        current_version = self.get_version()
        try:
            schema = self.get_service_schema(current_service, current_version)
        except ApiError:
            # When schema for current service can't be resolved it means action
            # is run from CLI and because of that there are no mappings to
            # resolve schemas. In this case is valid to set has_file_server to
            # true.
            has_file_server = True
        else:
            has_file_server = schema.has_file_server()

        files_payload = {}
        for file in files:
            if file.is_local() and not has_file_server:
                raise NoFileServerError(current_service, current_version)

            files_payload[file.get_name()] = file_to_payload(file)

        return files_payload

    def is_origin(self):
        """Determines if the current service is the origin of the request.

        :rtype: bool

        """

        origin = self.__transport.get('meta/origin')
        return (origin == [
            self.get_name(),
            self.get_version(),
            self.get_action_name()
            ])

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

        :raises: TypeError

        :rtype: Action

        """

        if not isinstance(value, str):
            raise TypeError('Value is not a string')

        self.__transport.set(
            'meta/properties/{}'.format(nomap(name)),
            str(value),
            )
        return self

    def has_param(self, name):
        """Check if a parameter exists.

        :param name: The parameter name.
        :type name: str

        :rtype: bool

        """

        return (name in self.__params)

    def get_param(self, name):
        """Get an action parameter.

        :param name: The parameter name.
        :type name: str

        :rtype: `Param`

        """

        if not self.has_param(name):
            return Param(name)

        return Param(
            name,
            value=self.__params[name].get('value'),
            type=self.__params[name].get('type'),
            exists=True,
            )

    def get_params(self):
        """Get all action parameters.

        :rtype: list

        """

        params = []
        for payload in self.__params.values():
            params.append(Param(
                payload.get('name'),
                value=payload.get('value'),
                type=payload.get('type'),
                exists=True,
                ))

        return params

    def new_param(self, name, value=None, type=None):
        """Creates a new parameter object.

        Creates an instance of Param with the given name, and optionally
        the value and data type. If the value is not provided then
        an empty string is assumed. If the data type is not defined then
        "string" is assumed.

        Valid data types are "null", "boolean", "integer", "float", "string",
        "array" and "object".

        :param name: The parameter name.
        :type name: str
        :param value: The parameter value.
        :type value: mixed
        :param type: The data type of the value.
        :type type: str

        :raises: TypeError

        :rtype: Param

        """

        if type and Param.resolve_type(value) != type:
            raise TypeError('Incorrect data type given for parameter value')
        else:
            type = Param.resolve_type(value)

        return Param(name, value=value, type=type, exists=True)

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

        :rtype: `File`

        """

        if self.has_file(name):
            return payload_to_file(name, self.__files[name])
        else:
            return File(name, path='')

    def get_files(self):
        """Get all action files.

        :rtype: list

        """

        files = []
        for name, payload in self.__files.items():
            files.append(payload_to_file(name, payload))

        return files

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

        return File(name, path, mime=mime)

    def set_download(self, file):
        """Set a file as the download.

        Sets a File object as the file to be downloaded via the Gateway.

        :param file: The file object.
        :type file: `File`

        :raises: TypeError
        :raises: NoFileServerError

        :rtype: Action

        """

        if not isinstance(file, File):
            raise TypeError('File must be an instance of File class')

        # Check that files server is enabled
        service = self.get_name()
        version = self.get_version()
        path = '{}/{}'.format(service, version)

        # Check if there are mappings to validate.
        # Note: When action is run from CLI mappings will be ampty.
        if self._schema.has_mappings:
            if not get_path(self._schema.get(path), 'files', False):
                raise NoFileServerError(service, version)

        self.__transport.set('body', file_to_payload(file))
        return self

    def set_entity(self, entity):
        """Sets the entity data.

        Sets an object as the entity to be returned by the action.

        Entity is validated when validation is enabled for an entity
        in the Service config file.

        :param entity: The entity object.
        :type entity: dict

        :raises: TypeError

        :rtype: Action

        """

        if not isinstance(entity, dict):
            raise TypeError('Entity must be an dict')

        self.__transport.push(
            'data|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                self.get_version(),
                nomap(self.get_action_name()),
                ),
            entity,
            delimiter='|',
            )
        return self

    def set_collection(self, collection):
        """Sets the collection data.

        Sets a list as the collection of entities to be returned by the action.

        Collextion is validated when validation is enabled for an entity
        in the Service config file.

        :param collection: The collection list.
        :type collection: list

        :raises: TypeError

        :rtype: Action

        """

        if not isinstance(collection, list):
            raise TypeError('Collection must be a list')

        for entity in collection:
            if not isinstance(entity, dict):
                raise TypeError('Entity must be an dict')

        self.__transport.push(
            'data|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                self.get_version(),
                nomap(self.get_action_name()),
                ),
            collection,
            delimiter='|',
            )
        return self

    def relate_one(self, primary_key, service, foreign_key):
        """Creates a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity with the given
        primary key and service with the foreign key.

        :param primery_key: The primary key.
        :type primary_key: str, int
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign key.
        :type foreign_key: str, int

        :rtype: Action

        """

        self.__transport.set(
            'relations|{}|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                nomap(primary_key),
                self.__public_address,
                nomap(service),
                ),
            foreign_key,
            delimiter='|',
            )
        return self

    def relate_many(self, primary_key, service, foreign_keys):
        """Creates a "one-to-many" relation between entities.

        Creates a "one-to-many" relation between the entity with the given
        primary key and service with the foreign keys.

        :param primery_key: The primary key.
        :type primary_key: str, int
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign keys.
        :type foreign_key: list

        :raises: TypeError

        :rtype: Action

        """

        if not isinstance(foreign_keys, list):
            raise TypeError('Foreign keys must be a list')

        self.__transport.set(
            'relations|{}|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                nomap(primary_key),
                self.__public_address,
                nomap(service),
                ),
            foreign_keys,
            delimiter='|',
            )
        return self

    def relate_one_remote(self, primary_key, address, service, foreign_key):
        """Creates a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity with the given
        primary key and service with the foreign key.

        This type of relation is done between entities in different realms.

        :param primery_key: The primary key.
        :type primary_key: str, int
        :param address: Foreign service public address.
        :type address: str
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign key.
        :type foreign_key: str, int

        :rtype: Action

        """

        self.__transport.set(
            'relations|{}|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                nomap(primary_key),
                address,
                nomap(service),
                ),
            foreign_key,
            delimiter='|',
            )
        return self

    def relate_many_remote(self, primary_key, address, service, foreign_keys):
        """Creates a "one-to-many" relation between entities.

        Creates a "one-to-many" relation between the entity with the given
        primary key and service with the foreign keys.

        This type of relation is done between entities in different realms.

        :param primery_key: The primary key.
        :type primary_key: str, int
        :param address: Foreign service public address.
        :type address: str
        :param service: The foreign service.
        :type service: str
        :param foreign_key: The foreign keys.
        :type foreign_key: list

        :raises: TypeError

        :rtype: Action

        """

        if not isinstance(foreign_keys, list):
            raise TypeError('Foreign keys must be a list')

        self.__transport.set(
            'relations|{}|{}|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                nomap(primary_key),
                address,
                nomap(service),
                ),
            foreign_keys,
            delimiter='|',
            )
        return self

    def set_link(self, link, uri):
        """Sets a link for the given URI.

        :param link: The link name.
        :type link: str
        :param uri: The link URI.
        :type uri: str

        :rtype: Action

        """

        self.__transport.set(
            'links|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                nomap(link),
                ),
            uri,
            delimiter='|',
            )
        return self

    def commit(self, action, params=None):
        """Register a transaction to be called when request succeeds.

        :param action: The action name.
        :type action: str
        :param params: Optional list of Param objects.
        :type params: list

        :rtype: Action

        """

        payload = Payload().set_many({
            'name': self.get_name(),
            'version': self.get_version(),
            'action': self.get_action_name(),
            'callee': action,
            })
        if params:
            payload.set('params', parse_params(params))

        self.__transport.push('transactions/commit', payload)
        return self

    def rollback(self, action, params=None):
        """Register a transaction to be called when request fails.

        :param action: The action name.
        :type action: str
        :param params: Optional list of Param objects.
        :type params: list

        :rtype: Action

        """

        payload = Payload().set_many({
            'name': self.get_name(),
            'version': self.get_version(),
            'action': self.get_action_name(),
            'callee': action,
            })
        if params:
            payload.set('params', parse_params(params))

        self.__transport.push('transactions/rollback', payload)
        return self

    def complete(self, action, params=None):
        """Register a transaction to be called when request finishes.

        This transaction is ALWAYS executed, it doesn't matter if request
        fails or succeeds.

        :param action: The action name.
        :type action: str
        :param params: Optional list of Param objects.
        :type params: list

        :rtype: Action

        """

        payload = Payload().set_many({
            'name': self.get_name(),
            'version': self.get_version(),
            'action': self.get_action_name(),
            'callee': action,
            })
        if params:
            payload.set('params', parse_params(params))

        self.__transport.push('transactions/complete', payload)
        return self

    def call(self, service, version, action, params=None, files=None):
        """Register a call to a service.

        :param service: The service name.
        :type service: str
        :param version: The service version.
        :type version: str
        :param action: The action name.
        :type action: str
        :param params: Optative list of Param objects.
        :type params: list
        :param files: Optative list of File objects.
        :type files: list

        :raises: NoFileServerError

        :rtype: Action

        """

        # Add files to transport
        if files:
            self.__transport.set(
                'files|{}|{}|{}|{}'.format(
                    self.__public_address,
                    nomap(service),
                    version,
                    nomap(action),
                    ),
                self.__files_to_payload(files),
                delimiter='|',
                )

        payload = Payload().set_many({
            'name': service,
            'version': version,
            'action': action,
            })
        if params:
            payload.set('params', parse_params(params))

        # Calls are aggregated to transport calls
        self.__transport.push(
            'calls/{}/{}'.format(nomap(self.get_name()), self.get_version()),
            payload
            )
        return self

    def call_remote(self, address, service, version, action, **kwargs):
        """Register a call to a remote service.

        :param address: Public address of a Gateway from another Realm.
        :type address: str
        :param service: The service name.
        :type service: str
        :param version: The service version.
        :type version: str
        :param action: The action name.
        :type action: str
        :param params: Optative list of Param objects.
        :type params: list
        :param files: Optative list of File objects.
        :type files: list

        :raises: NoFileServerError

        :rtype: Action

        """

        if address[:3] != 'ktp':
            address = 'ktp://{}'.format(address)

        # Add files to transport
        files = kwargs.get('files')
        if files:
            self.__transport.set(
                'files|{}|{}|{}|{}'.format(
                    self.__public_address,
                    nomap(service),
                    version,
                    nomap(action),
                    ),
                self.__files_to_payload(files),
                delimiter='|',
                )

        payload = Payload().set_many({
            'gateway': address,
            'name': service,
            'version': version,
            'action': action,
            })

        # callback = kwargs.get('callback')
        # if callback:
        #     payload.set('callback', callback)

        params = kwargs.get('params')
        if params:
            payload.set('params', parse_params(params))

        # Calls are aggregated to transport calls
        self.__transport.push(
            'calls/{}/{}'.format(nomap(self.get_name()), self.get_version()),
            payload
            )
        return self

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

        :rtype: Action

        """

        self.__transport.push(
            'errors|{}|{}|{}'.format(
                self.__public_address,
                nomap(self.get_name()),
                self.get_version(),
                ),
            ErrorPayload.new(message, code, status),
            delimiter='|',
            )
        return self
