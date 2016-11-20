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
from ..service.server import ServiceServer


class Service(Component):
    """KATANA SDK Service component."""

    def __init__(self):
        super().__init__()
        self._runner = ComponentRunner(
            self,
            ServiceServer,
            'Service component action to process application logic',
            )

    def action(self, name, callback):
        self._callbacks[name] = callback
