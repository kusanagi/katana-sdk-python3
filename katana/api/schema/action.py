from collections import OrderedDict

from .error import ServiceSchemaError
from .param import ParamSchema
from .file import FileSchema
from ... payload import get_path
from ... payload import Payload


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

        Each entity property is a field name, and the value either the data
        type as a string or an object with fields.

        :rtype: object

        """

        return self.__payload.get('entity', {})

    def has_relations(self):
        """Check if any relations exists for the action.

        :rtype: bool

        """

        return self.__payload.path_exists('relation')

    def get_relations(self):
        """Get action relations.

        Each item is an array containins the relation type, the Service name,
        the Service version and the action name as a string, and the validation
        setting as a boolean value.

        :rtype: list

        """

        return self.__payload.get('relation', [])

    def get_params(self):
        """Get the parameters names defined for the action.

        :rtype: list

        """

        return self.__params.keys()

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

        return self.__files.keys()

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
