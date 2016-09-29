"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class Component(object):
    """Base KATANA SDK component class."""

    def __init__(self):
        self._runner = None

    def run(self, callback):
        """Run SDK component.

        Callback must be a callable that receives a
        `katana.api.base.Api` argument.

        Calling this method checks command line arguments before
        component server starts.

        :param callback: Callable to handle requests.
        :type callback: A callable.

        """

        if not self._runner:
            # Child classes must create a component runner instance
            raise Exception('No component runner defined')

        self._runner.run(callback)
