"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

from .component import Component
from .runner import ComponentRunner
from ..middleware import MiddlewareServer

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class Middleware(Component):
    """KATANA SDK Middleware component."""

    def __init__(self):
        super().__init__()
        # Create a component runner for the middleware server
        help = 'Middleware component to process HTTP requests and responses'
        self._runner = ComponentRunner(self, MiddlewareServer, help)

    def request(self, callback):
        """Set a callback for requests.

        :param callback: Callback to handle requests.
        :type callback: callable

        """

        self._callbacks['request'] = callback

    def response(self, callback):
        """Set callback for response.

        :param callback: Callback to handle responses.
        :type callback: callable

        """

        self._callbacks['response'] = callback


def get_component():
    """Get global Middleware component instance.

    :rtype: Middleware

    """

    return Middleware.instance
