"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

from ..errors import KatanaError


class ComponentError(KatanaError):
    """Exception calss for component errors."""


class Component(object):
    """Base KATANA SDK component class."""

    def __init__(self):
        self.__resources = {}
        self._callbacks = {}
        self._runner = None

    def has_resource(self, name):
        """Check if a resource name exist.

        :param name: Name of the resource.
        :type name: str

        :rtype: bool

        """

        return name in self.__resources

    def set_resource(self, name, callable):
        """Store a resource.

        :param name: Name of the resource.
        :type name: str
        :param callable: A callable that returns the resource value.
        :type callable: function

        :raises: ComponentError

        """

        value = callable()
        if value is None:
            err = 'Invalid result value for resource "{}"'.format(name)
            raise ComponentError(err)

        self.__resources[name] = value

    def get_resource(self, name):
        """Get a resource.

        :param name: Name of the resource.
        :type name: str

        :rtype: object

        """

        if not self.has_resource(name):
            raise ComponentError('Resource "{}" not found'.format(name))

        return self.__resources[name]

    def run(self):
        """Run SDK component.

        Calling this method checks command line arguments before
        component server starts.

        """

        if not self._runner:
            # Child classes must create a component runner instance
            raise Exception('No component runner defined')

        self._runner.set_callbacks(self._callbacks)
        self._runner.run()
