from .action import ActionSchema
from .error import ServiceSchemaError


class ServiceSchema(object):
    """Service schema in the platform."""

    def __init__(self):
        pass

    def get_name(self):
        """Get Service name.

        :rtype: str

        """

    def get_version(self):
        """Get Service version.

        :rtype: str

        """

    def get_actions(self):
        """Get Service action names.

        Action names are returned in the order in which they are defined.

        :rtype: list

        """

    def has_action(self, name):
        """Check if an action exists for current Service schema.

        :param name: Action name.
        :type name: str

        :rtype: bool

        """

    def get_action_schema(self, name):
        """Get schema for an action.

        :param name: Action name.
        :type name: str

        :raises: ServiceSchemaError

        :rtype: ActionSchema

        """

        if not self.has_action(name):
            error = 'Cannot resolve schema for action: {}'.format(name)
            raise ServiceSchemaError(error)

        # TODO: Get action schema

    def get_http_schema(self):
        """Get HTTP Service schema.

        :rtype: HttpServiceSchema

        """


class HttpServiceSchema(object):
    """HTTP semantics of a Service schema in the platform."""

    def __init__(self):
        pass

    def is_accessible(self):
        """Check if the Gateway has access to the Service.

        :rtype: bool

        """

    def get_base_path(self):
        """Get base HTTP path for the Service.

        :rtype: str

        """
