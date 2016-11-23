class ParamSchema(object):
    """Parameter schema in the platform."""

    def __init__(self):
        pass

    def get_name(self):
        """Get parameter name.

        :rtype: str

        """

    def get_type(self):
        """Get parameter value type.

        :rtype: str

        """

    def get_format(self):
        """Get parameter value format.

        :rtype: str

        """

        return ''

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

        return 'csv'

    def get_pattern(self):
        """Get ECMA 262 compliant regular expression to validate the parameter.

        :rtype: str

        """

        return ''

    def allow_empty(self):
        """Check if the parameter allows an empty value.

        :rtype: bool

        """

        return False

    def has_default_value(self):
        """Check if the parameter has a default value defined.

        :rtype: bool

        """

        return False

    def get_default_value(self):
        """Get default value for parameter.

        :rtype: str

        """

        return ''

    def is_required(self):
        """Check if parameter is required.

        :rtype: bool

        """

    def get_items(self):
        """Get JSON items defined for the parameter.

        An empty string is returned when parameter type is not "array".

        :rtype: list

        """

        return ''

    def get_max(self):
        """Get maximum value for parameter.

        :rtype: int

        """

        # TODO: Return maximum integer value possible for python
        return 999999

    def is_exclusive_max(self):
        """Check if max value is inclusive.

        When max is not defined inclusive is False.

        :rtype: bool

        """

        return False

    def get_min(self):
        """Get minimum value for parameter.

        :rtype: int

        """

        # TODO: Return minimum integer value possible for python
        return -99999

    def is_exclusive_min(self):
        """Check if minimum value is inclusive.

        When min is not defined inclusive is False.

        :rtype: bool

        """

        return False

    def get_max_length(self):
        """Get max length defined for the parameter.

        :rtype: int

        """

        return -1

    def get_min_length(self):
        """Get minimum length defined for the parameter.

        :rtype: int

        """

        return -1

    def get_max_items(self):
        """Get maximum number of items allowed for the parameter.

        Result is -1 When type is not "array".

        :rtype: int

        """

        return -1

    def get_min_items(self):
        """Get minimum number of items allowed for the parameter.

        Result is -1 When type is not "array".

        :rtype: int

        """

        return -1

    def has_unique_items(self):
        """Check if param must contain a set of unique items.

        :rtype: bool

        """

    def get_enum(self):
        """Get the set of unique values that parameter allows.

        :rtype: set

        """

        return set()

    def get_multiple_of(self):
        """Get value that parameter must be divisible by.

        Result is -1 when this property is not defined.

        :rtype: int

        """

    def get_http_schema(self):
        """Get HTTP param schema.

        :rtype: HttpParamSchema

        """


class HttpParamSchema(object):
    """HTTP semantics of a parameter schema in the platform."""

    def __init__(self):
        pass

    def is_accessible(self):
        """Check if the Gateway has access to the parameter.

        :rtype: bool

        """

    def get_input(self):
        """Get location of the parameter.

        :rtype: str

        """

        # TODO: Implement. Default 'query'
        return 'query'

    def get_param(self):
        """Get name as specified via HTTP to be mapped to the name property.

        :rtype: str

        """

        # TODO: Defaults to the parameter name.
