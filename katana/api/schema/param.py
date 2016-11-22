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

        # TODO: Implement. Default: ''
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

        # TODO: Implement. Default: 'csv'
        return 'csv'

    def get_pattern(self):
        """Get ECMA 262 compliant regular expression to validate the parameter.

        :rtype: str

        """

        # TODO: Implement. Default: ''
        return ''

    def allow_empty(self):
        """Check if the parameter allows an empty value.

        :rtype: bool

        """

        # TODO: Implement. Default: False
        return False

    def has_default_value(self):
        """Check if the parameter has a default value defined.

        :rtype: bool

        """

        # TODO: Implement. Default: False
        return False

    def get_default_value(self):
        """

        :rtype: str

        """

    def is_required(self):
        """

        :rtype: bool

        """

    def get_items(self):
        """

        :rtype: list

        """

    def get_max(self):
        """

        :rtype: int

        """

    def is_exclusive_max(self):
        """

        :rtype: bool

        """

    def get_min(self):
        """

        :rtype: int

        """

    def is_exclusive_min(self):
        """

        :rtype: bool

        """

    def get_max_length(self):
        """

        :rtype: int

        """

    def get_min_length(self):
        """

        :rtype: int

        """

    def get_max_items(self):
        """

        :rtype: int

        """

    def get_min_items(self):
        """

        :rtype: int

        """

    def has_unique_items(self):
        """

        :rtype: bool

        """

    def get_enum(self):
        """

        :rtype: list

        """

    def get_multiple_of(self):
        """

        :rtype: int

        """

    def get_http_schema(self):
        """

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
