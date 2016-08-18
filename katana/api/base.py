class Api(object):
    """Base API class for SDK components."""

    def __init__(self, path, name, version, platform_version, **kwargs):
        self.__path = path
        self.__name = name
        self.__version = version
        self.__platform_version = platform_version
        self.__variables = kwargs.get('variables') or {}
        self.__debug = kwargs.get('debug', False)

    def is_debug(self):
        """Determine if component is running in debug mode.

        :rtype: bool.

        """

        return self.__debug

    def get_platform_version(self):
        """Get KATANA platform version.

        :rtype: str.

        """

        return self.__platform_version

    def get_path(self):
        """Get source file path.

        Returns the path to the endpoint userland source file.

        :returns: Source path file.
        :rtype: str.

        """

        return self.__path

    def get_name(self):
        """Get component name.

        :rtype: str.

        """

        return self.__name

    def get_version(self):
        """Get component version.

        :rtype: str.

        """

        return self.__version

    def get_variables(self):
        """Gets all component variables.

        :rtype: dict.

        """

        return self.__variables

    def get_variable(self, name):
        """Get a single component variable.

        :param name: Variable name.
        :type name: str.

        :rtype: str or None.

        """

        if name in self.__variables:
            return self.__variables[name]