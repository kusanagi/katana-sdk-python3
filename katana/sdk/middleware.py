"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

from .component import Component
from .runner import ComponentRunner
from ..middleware.server import MiddlewareServer


class Middleware(Component):
    """KATANA SDK Middleware component."""

    def __init__(self):
        super().__init__()
        self._runner = ComponentRunner(
            MiddlewareServer,
            'Middleware component to process HTTP requests and responses',
            )

    def request(self, callback):
        self._callbacks['request'] = callback

    def response(self, callback):
        self._callbacks['response'] = callback
