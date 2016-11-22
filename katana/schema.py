from .errors import KatanaError
from .payload import Payload
from .utils import Singleton


class SchemaRegistry(object, metaclass=Singleton):
    """Global service schema registry."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__mappings = Payload()

    @staticmethod
    def is_empty(value):
        """Check if a value is the empty value.

        :rtype: bool

        """

        return Payload.is_empty(value)

    def update_registry(self, mappings):
        """Update schema registry with mappings info.

        :param mappings: Mappings payload.
        :type mappings: dict

        """

        self.__mappings = Payload(mappings or {})

    def path_exists(self, path):
        """Check if a path is available.

        For arguments see `Payload.path_exists()`.

        :param path: Path to a value.
        :type path: str

        :rtype: bool

        """

        return self.__mappings.path_exists(path)

    def get(self, path, *args, **kwargs):
        """Get value by key path.

        For arguments see `Payload.get()`.

        :param path: Path to a value.
        :type path: str

        :returns: The value for the given path.
        :rtype: object

        """

        return self.__mappings.get(path, *args, **kwargs)


def get_schema_registry():
    """Get global schema registry.

    :rtype: SchemaRegistry

    """

    if not SchemaRegistry.instance:
        raise KatanaError('Global schema registry is not initialized')

    return SchemaRegistry.instance
