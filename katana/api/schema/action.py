"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from .error import ServiceSchemaError
from .param import ParamSchema
from .file import FileSchema
from ... payload import get_path
from ... payload import path_exists
from ... payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


def entity_from_payload(entity_payload, entity=None):
    """Create a new entity definition object from a payload.

    :param entity_payload: Entity definition payload.
    :type entity_payload: dict

    :rtype: dict

    """

    entity = entity or {}
    if not entity_payload:
        return entity

    # Add validate field only to top level entity
    if not entity:
        entity['validate'] = get_path(entity_payload, 'validate', False)

    # Add fields to entity
    if path_exists(entity_payload, 'field'):
        entity['field'] = []
        for payload in get_path(entity_payload, 'field'):
            entity['field'].append({
                'name': get_path(payload, 'name'),
                'type': get_path(payload, 'type', 'string'),
                'optional': get_path(payload, 'optional', False),
                })

    # Add field sets to entity
    if path_exists(entity_payload, 'fields'):
        entity['fields'] = []
        for payload in get_path(entity_payload, 'fields'):
            fieldset = {
                'name': get_path(payload, 'name'),
                'optional': get_path(payload, 'optional', False),
                }

            # Add inner field and fieldsets
            if path_exists(payload, 'field') or path_exists(payload, 'fields'):
                fieldset = entity_from_payload(payload, fieldset)

        entity['fields'].append(fieldset)

    return entity


def relations_from_payload(relations_payload):
    """Create a new relations definition list from a payload.

    :param relations_payload: Relation definitions from payload.
    :type relations_payload: list

    :rtype: list

    """

    relations = []
    if not relations_payload:
        return relations

    for relation in relations_payload:
        relations.append([
            get_path(relation, 'type', 'one'),
            get_path(relation, 'name'),
            ])

    return relations


class ActionSchemaError(ServiceSchemaError):
    """Error class for schema action errors."""


class ActionSchema(object):
    """Action schema in the platform."""

    def __init__(self, name, payload):
        self.__name = name
        self.__payload = Payload(payload)
        self.__params = self.__payload.get('params', {})
        self.__files = self.__payload.get('files', {})

    def is_deprecated(self):
        """Check if action has been deprecated.

        :rtype: bool

        """

        return self.__payload.get('deprecated', False)

    def is_collection(self):
        """Check if the action returns a collection of entities.

        :rtype: bool

        """

        return self.__payload.get('collection', False)

    def get_name(self):
        """Get action name.

        :rtype: str

        """

        return self.__name

    def get_entity_path(self):
        """Get path to the entity.

        :rtype: str

        """

        return self.__payload.get('entity_path', '')

    def get_path_delimiter(self):
        """Get delimiter to use for the entity path.

        :rtype: str

        """

        return self.__payload.get('path_delimiter', '/')

    def get_primary_key(self):
        """Get primary key field name.

        Gets the name of the property in the entity which
        contains the primary key.

        :rtype: str

        """

        return self.__payload.get('primary_key', 'id')

    def resolve_entity(self, data):
        """Get entity from data.

        Get the entity part, based upon the `entity-path` and `path-delimiter`
        properties in the action configuration.

        :param data: Object to get entity from.
        :type data: dict

        :rtype: dict

        """

        path = self.get_entity_path()
        # When there is no path no traversing is done
        if not path:
            return data

        try:
            return get_path(data, path, delimiter=self.get_path_delimiter())
        except KeyError:
            error = 'Cannot resolve entity for action: {}'
            raise ActionSchemaError(error.format(self.get_name()))

    def has_entity_definition(self):
        """Check if an entity definition exists for the action.

        :rtype: bool

        """

        return self.__payload.path_exists('entity')

    def get_entity(self):
        """Get the entity definition as an object.

        :rtype: dict

        """

        return entity_from_payload(self.__payload.get('entity', None))

    def has_relations(self):
        """Check if any relations exists for the action.

        :rtype: bool

        """

        return self.__payload.path_exists('relations')

    def get_relations(self):
        """Get action relations.

        Each item is an array containins the relation type
        and the Service name.

        :rtype: list

        """

        return relations_from_payload(self.__payload.get('relations', None))

    def has_call(self, name, version=None, action=None):
        """Check if an internal call exists for a Service.

        :param name: Service name.
        :type name: str
        :param version: Optional Service version.
        :type version: str
        :param action: Optional action name.
        :type action: str

        :rtype: bool

        """

        for call in self.get_calls():
            if call[0] != name:
                continue

            if version and call[1] != version:
                continue

            if action and call[2] != action:
                continue

            # When all given arguments match the call return True
            return True

        # By default call does not exist
        return False

    def has_calls(self):
        """Check if any internal call exists for the action.

        :rtype: bool

        """

        return self.__payload.path_exists('calls')

    def get_calls(self):
        """Get Service calls.

        Each call items is a list containing the Service name,
        the Service version and the action name.

        :rtype: list

        """

        return self.__payload.get('calls', [])

    def has_remote_call(self, address, name=None, version=None, action=None):
        """Check if a remote call exists for a Service.

        :param address: Gateway address.
        :type address: str
        :param name: Optional Service name.
        :type name: str
        :param version: Optional Service version.
        :type version: str
        :param action: Optional action name.
        :type action: str

        :rtype: bool

        """

        for call in self.get_remote_calls():
            if call[0] != address:
                continue

            if name and call[1] != name:
                continue

            if version and call[2] != version:
                continue

            if action and call[3] != action:
                continue

            # When all given arguments match the call return True
            return True

        # By default call does not exist
        return False

    def has_remote_calls(self):
        """Check if any remote call exists for the action.

        :rtype: bool

        """

        return self.__payload.path_exists('remote_calls')

    def get_remote_calls(self):
        """Get remote Service calls.

        Each remote call items is a list containing the public address
        of the Gateway, the Service name, the Service version and the
        action name.

        :rtype: list

        """

        return self.__payload.get('remote_calls', [])

    def get_params(self):
        """Get the parameters names defined for the action.

        :rtype: list

        """

        return list(self.__params.keys())

    def has_param(self, name):
        """Check that a parameter schema exists.

        :param name: Parameter name.
        :type name: str

        :rtype: bool

        """

        return name in self.__params

    def get_param_schema(self, name):
        """Get schema for a parameter.

        :param name: Parameter name.
        :type name: str

        :rtype: ParamSchema

        """

        if not self.has_param(name):
            error = 'Cannot resolve schema for parameter: {}'
            raise ActionSchemaError(error.format(name))

        return ParamSchema(name, self.__params[name])

    def get_files(self):
        """Get the file parameter names defined for the action.

        :rtype: list

        """

        return list(self.__files.keys())

    def has_file(self, name):
        """Check that a file parameter schema exists.

        :param name: File parameter name.
        :type name: str

        :rtype: bool

        """

        return name in self.__files

    def get_file_schema(self, name):
        """Get schema for a file parameter.

        :param name: File parameter name.
        :type name: str

        :rtype: FileSchema

        """

        if not self.has_file(name):
            error = 'Cannot resolve schema for file parameter: {}'
            raise ActionSchemaError(error.format(name))

        return FileSchema(name, self.__files[name])

    def get_http_schema(self):
        """Get HTTP action schema.

        :rtype: HttpActionSchema

        """

        return HttpActionSchema(self.__payload.get('http', {}))


class HttpActionSchema(object):
    """HTTP semantics of an action schema in the platform."""

    def __init__(self, payload):
        self.__payload = Payload(payload)

    def is_accessible(self):
        """Check if the Gateway has access to the action.

        :rtype: bool

        """

        return self.__payload.get('gateway', True)

    def get_method(self):
        """Get HTTP method for the action.

        :rtype: str

        """

        return self.__payload.get('method', 'get')

    def get_path(self):
        """Get URL path for the action.

        :rtype: str

        """

        return self.__payload.get('path', '')

    def get_input(self):
        """Get default location of parameters for the action.

        :rtype: str

        """

        return self.__payload.get('input', 'query')

    def get_body(self):
        """Get expected MIME type of the HTTP request body.

        Result may contain a comma separated list of MIME types.

        :rtype: str

        """

        return ','.join(self.__payload.get('body', ['text/plain']))
