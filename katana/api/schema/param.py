import json
import logging
import sys

from ...payload import Payload

LOG = logging.getLogger(__name__)


class ParamSchema(object):
    """Parameter schema in the platform."""

    def __init__(self, name, payload):
        self.__name = name
        self.__payload = Payload(payload)

    def get_name(self):
        """Get parameter name.

        :rtype: str

        """

        return self.__name

    def get_type(self):
        """Get parameter value type.

        :rtype: str

        """

        return self.__payload.get('type', 'string')

    def get_format(self):
        """Get parameter value format.

        :rtype: str

        """

        return self.__payload.get('format', '')

    def get_array_format(self):
        """Get format for the parameter if the type property is set to "array".

        Formats:
          - "csv" for comma separated values (default)
          - "ssv" for space separated values
          - "tsv" for tab separated values
          - "pipes" for pipe separated values
          - "multi" for multiple parameter instances instead of multiple
            values for a single instance.

        :rtype: str

        """

        return self.__payload.get('array_format', 'csv')

    def get_pattern(self):
        """Get ECMA 262 compliant regular expression to validate the parameter.

        :rtype: str

        """

        return self.__payload.get('pattern', '')

    def allow_empty(self):
        """Check if the parameter allows an empty value.

        :rtype: bool

        """

        return self.__payload.get('allow_empty', False)

    def has_default_value(self):
        """Check if the parameter has a default value defined.

        :rtype: bool

        """

        return self.__payload.path_exists('default')

    def get_default_value(self):
        """Get default value for parameter.

        :rtype: str

        """

        return self.__payload.get('default', '')

    def is_required(self):
        """Check if parameter is required.

        :rtype: bool

        """

        return self.__payload.get('required', False)

    def get_items(self):
        """Get JSON items defined for the parameter.

        An empty string is returned when parameter type is not "array".

        :rtype: list

        """

        if self.get_type() != 'array':
            return ''

        if not self.__payload.path_exists('items'):
            return ''

        try:
            # Items must be a valid JSON string
            return json.loads(self.__payload.get('items'))
        except:
            LOG.exception('Value for "items" is not valid JSON')
            return ''

    def get_max(self):
        """Get maximum value for parameter.

        :rtype: int

        """

        return self.__payload.get('maximum', sys.maxint)

    def is_exclusive_max(self):
        """Check if max value is inclusive.

        When max is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('maximum'):
            return False

        return self.__payload.get('exclusive_maximum', False)

    def get_min(self):
        """Get minimum value for parameter.

        :rtype: int

        """

        return self.__payload.get('maximum', -sys.maxint - 1)

    def is_exclusive_min(self):
        """Check if minimum value is inclusive.

        When min is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('minimum'):
            return False

        return self.__payload.get('exclusive_minimum', False)

    def get_max_length(self):
        """Get max length defined for the parameter.

        result is -1 when this values is not defined.

        :rtype: int

        """

        return self.__payload.get('maximum_length', -1)

    def get_min_length(self):
        """Get minimum length defined for the parameter.

        result is -1 when this values is not defined.

        :rtype: int

        """

        return self.__payload.get('minimum_length', -1)

    def get_max_items(self):
        """Get maximum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        :rtype: int

        """

        if self.get_type() != 'array':
            return -1

        return self.__payload.get('maximum_items', -1)

    def get_min_items(self):
        """Get minimum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        :rtype: int

        """

        if self.get_type() != 'array':
            return -1

        return self.__payload.get('minimum_items', -1)

    def has_unique_items(self):
        """Check if param must contain a set of unique items.

        :rtype: bool

        """

        return self.__payload.get('unique_items', False)

    def get_enum(self):
        """Get the set of unique values that parameter allows.

        :rtype: list

        """

        if not self.__payload.path_exists('enum'):
            return ''

        try:
            # Items must be a valid JSON string
            return json.loads(self.__payload.get('enum'))
        except:
            LOG.exception('Value for "enum" is not valid JSON')
            return ''

    def get_multiple_of(self):
        """Get value that parameter must be divisible by.

        Result is -1 when this property is not defined.

        :rtype: int

        """

        return self.__payload.get('multiple_of', -1)

    def get_http_schema(self):
        """Get HTTP param schema.

        :rtype: HttpParamSchema

        """

        return HttpParamSchema(self.get_name(), self.__payload.get('http', {}))


class HttpParamSchema(object):
    """HTTP semantics of a parameter schema in the platform."""

    def __init__(self, name, payload):
        self.__name = name
        self.__payload = Payload(payload)

    def is_accessible(self):
        """Check if the Gateway has access to the parameter.

        :rtype: bool

        """

        return self.__payload.get('gateway', True)

    def get_input(self):
        """Get location of the parameter.

        :rtype: str

        """

        return self.__payload.get('input', 'query')

    def get_param(self):
        """Get name as specified via HTTP to be mapped to the name property.

        :rtype: str

        """

        return self.__payload.get('param', self.__name)
