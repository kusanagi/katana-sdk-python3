"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class KatanaError(Exception):
    """Base exception for KATANA errors."""

    message = None

    def __init__(self, message=None):
        if message:
            self.message = message

        super().__init__(self.message)

    def __str__(self):
        return self.message or self.__class__.__name__
