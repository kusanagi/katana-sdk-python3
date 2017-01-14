"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

from .errors import KatanaError
from .payload import Payload
from .utils import Singleton

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


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

    @property
    def has_mappings(self):
        """Check if registry contains mappings.

        :rtype: bool

        """

        return len(self.__mappings) > 0

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
