"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import logging

from ..errors import KatanaError
from ..logging import value_to_log_string
from ..schema import SchemaRegistry
from ..utils import Singleton


class ComponentError(KatanaError):
    """Exception calss for component errors."""


class Component(object, metaclass=Singleton):
    """Base KATANA SDK component class."""

    def __init__(self):
        self.__resources = {}
        self.__startup_callback = None
        self.__shutdown_callback = None
        self.__error_callback = None
        self._callbacks = {}
        self._runner = None
        self.__logger = logging.getLogger('katana.api')

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

        :raises: ComponentError

        :rtype: object

        """

        if not self.has_resource(name):
            raise ComponentError('Resource "{}" not found'.format(name))

        return self.__resources[name]

    def startup(self, callback):
        """Register a callback to be called during component startup.

        Callback receives a single argument with the Component instance.

        :param callback: A callback to execute on startup.
        :type callback: function

        """

        self.__startup_callback = callback

    def shutdown(self, callback):
        """Register a callback to be called during component shutdown.

        Callback receives a single argument with the Component instance.

        :param callback: A callback to execute on shutdown.
        :type callback: function

        """

        self.__shutdown_callback = callback

    def error(self, callback):
        """Register a callback to be called on message callback errors.

        Callback receives a single argument with the Exception instance.

        :param callback: A callback to execute a message callback fails.
        :type callback: function

        """

        self.__error_callback = callback

    def run(self):
        """Run SDK component.

        Calling this method checks command line arguments before
        component server starts.

        """

        if not self._runner:
            # Child classes must create a component runner instance
            raise Exception('No component runner defined')

        if self.__startup_callback:
            self._runner.set_startup_callback(self.__startup_callback)

        if self.__shutdown_callback:
            self._runner.set_shutdown_callback(self.__shutdown_callback)

        if self.__error_callback:
            self._runner.set_error_callback(self.__error_callback)

        # Create the global schema registry instance on run
        SchemaRegistry()

        self._runner.set_callbacks(self._callbacks)
        self._runner.run()

    def log(self, value):
        """Write a value to KATANA logs.

        Given value is converted to string before being logged.

        Output is truncated to have a maximum of 100000 characters.

        """

        self.__logger.debug(value_to_log_string(value))
