from .error import ServiceSchemaError
from .param import ParamSchema


class ActionSchemaError(ServiceSchemaError):
    """Error class for schema action errors."""


class ActionSchema(object):
    """Action schema in the platform."""

    def __init__(self):
        pass

    def is_deprecated(self):
        """Check if action has been deprecated.

        :rtype: bool

        """

        # TODO: get value and use false as default
        return False

    def is_collection(self):
        """Check if the action returns a collection of entities.

        :rtype: bool

        """

        # TODO: get value and use false as default
        return False

    def get_name(self):
        """Get action name.

        :rtype: str

        """

    def get_entity_path(self):
        """Get path to the entity.

        :rtype: str

        """

        # TODO: get value and use '' as default
        return ''

    def get_path_delimiter(self):
        """Get delimiter to use for the entity path.

        :rtype: str

        """

        # TODO: get value and use '/' as default
        return '/'

    def get_primary_key(self):
        """Get primary key field name.

        Gets the name of the property in the entity which
        contains the primary key.

        :rtype: str

        """

        # TODO: get value and use 'id' as default
        return 'id'

    def resolve_entity(self, data):
        """Get entity from data.

        Get the entity part, based upon the `entity-path` and `path-delimiter`
        properties in the action configuration.

        :param data: Object to get entity from.
        :type data: object

        :rtype: object

        """

        # TODO: Implement
        if False:
            error = 'Cannot resolve entity for action: {}'
            raise ActionSchemaError(error.format(self.get_name()))

    def has_entity(self):
        """Check if an entity definition exists for the action.

        :rtype: bool

        """

    def get_entity(self):
        """Get the entity definition as an object.

        Each entity property is a field name, and the value either the data
        type as a string or an object with fields.

        :rtype: object

        """

        # TODO: get value and use {} as default
        return {}

    def has_relations(self):
        """Check if any relations exists for the action.

        :rtype: bool

        """

    def get_relations(self):
        """Get action relations.

        Each item is an array containins the relation type, the Service name,
        the Service version and the action name as a string, and the validation
        setting as a boolean value.

        :rtype: list

        """

        # TODO: get value and use [] as default
        return []

    def get_params(self):
        """Get the parameters names defined for the action.

        :rtype: list

        """

    def has_param(self, name):
        """Check that a parameter schema exists.

        :param name: Parameter name.
        :type name: str

        :rtype: bool

        """

    def get_param_schema(self, name):
        """Get schema for a parameter.

        :param name: Parameter name.
        :type name: str

        :rtype: ParamSchema

        """

        # TODO: Implement
        if not self.has_param(name):
            error = 'Cannot resolve schema for parameter: {}'
            raise ActionSchemaError(error.format(name))

    def get_http_schema(self):
        """Get HTTP action schema.

        :rtype: HttpActionSchema

        """


class HttpActionSchema(object):
    """HTTP semantics of an action schema in the platform."""

    def __init__(self):
        pass

    def is_accessible(self):
        """Check if the Gateway has access to the action.

        :rtype: bool

        """

    def get_method(self):
        """Get HTTP method for the action.

        :rtype: str

        """

        # TODO: get value and use 'get' as default
        return 'get'

    def get_path(self):
        """Get URL path for the action.

        :rtype: str

        """

        # TODO: Implement `http-base-path` + `http-path`. Default ''
        return ''

    def get_input(self):
        """Get default location of parameters for the action.

        :rtype: str

        """

        # TODO: Implement. Default 'query'
        return 'query'

    def get_body(self):
        """Get expected MIME type of the HTTP request body.

        Result may contain a comma separated list of MIME types.

        :rtype: str

        """

        # TODO: Implement. Default 'text/plain'
        return 'text/plain'
