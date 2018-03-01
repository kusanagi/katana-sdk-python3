"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import sys

from ...payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class ParamSchema(object):
    """Parameter schema in the framework."""

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

        return self.__payload.path_exists('default_value')

    def get_default_value(self):
        """Get default value for parameter.

        :rtype: object

        """

        return self.__payload.get('default_value', None)

    def is_required(self):
        """Check if parameter is required.

        :rtype: bool

        """

        return self.__payload.get('required', False)

    def get_items(self):
        """Get JSON schema with items object definition.

        An empty dicitonary is returned when parameter is not an "array",
        otherwise the result contains a dictionary with a JSON schema
        definition.

        :rtype: dict

        """

        if self.get_type() != 'array':
            return {}

        return self.__payload.get('items', {})

    def get_max(self):
        """Get maximum value for parameter.

        :rtype: int

        """

        return self.__payload.get('max', sys.maxsize)

    def is_exclusive_max(self):
        """Check if max value is inclusive.

        When max is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('max'):
            return False

        return self.__payload.get('exclusive_max', False)

    def get_min(self):
        """Get minimum value for parameter.

        :rtype: int

        """

        return self.__payload.get('min', -sys.maxsize - 1)

    def is_exclusive_min(self):
        """Check if minimum value is inclusive.

        When min is not defined inclusive is False.

        :rtype: bool

        """

        if not self.__payload.path_exists('min'):
            return False

        return self.__payload.get('exclusive_min', False)

    def get_max_length(self):
        """Get max length defined for the parameter.

        result is -1 when this values is not defined.

        :rtype: int

        """

        return self.__payload.get('max_length', -1)

    def get_min_length(self):
        """Get minimum length defined for the parameter.

        result is -1 when this values is not defined.

        :rtype: int

        """

        return self.__payload.get('min_length', -1)

    def get_max_items(self):
        """Get maximum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        :rtype: int

        """

        if self.get_type() != 'array':
            return -1

        return self.__payload.get('max_items', -1)

    def get_min_items(self):
        """Get minimum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        :rtype: int

        """

        if self.get_type() != 'array':
            return -1

        return self.__payload.get('min_items', -1)

    def has_unique_items(self):
        """Check if param must contain a set of unique items.

        :rtype: bool

        """

        return self.__payload.get('unique_items', False)

    def get_enum(self):
        """Get the set of unique values that parameter allows.

        :rtype: list

        """

        return self.__payload.get('enum', [])

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
    """HTTP semantics of a parameter schema in the framework."""

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
