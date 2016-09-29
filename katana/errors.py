"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

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


class RequestTimeoutError(KatanaError):
    """Error for request timeouts."""

    message = 'Request timeout'


class PayloadExpired(KatanaError):
    """Error for payload expiration."""

    def __init__(self, offset):
        self.offset = offset
        super().__init__('Payload expired {:.3f} seconds ago'.format(offset))


class PayloadError(KatanaError):
    """Error for invalid payloads."""

    message = 'Payload error'

    def __init__(self, message=None, status=None, code=None):
        super().__init__(message or self.message)
        self.status = status or '500 Internal Server Error'
        self.code = code


class HTTPError(KatanaError):
    """Base HTTP error exception."""

    headers = None
    message = '500 Internal Server Error'

    def __init__(self, body=None, headers=None):
        super().__init__(self.message)
        self.body = body or self.message
        self.headers = headers or []

    def __str__(self):
        return self.message

    @property
    def status(self):
        """Get HTTP status code and message.

        :rtype: str.

        """

        return self.message

    @property
    def status_code(self):
        """Get HTTP status code.

        :rtype: int.

        """

        return int(self.status[:3])

    @property
    def status_message(self):
        """Get HTTP status message.

        :rtype: str.

        """

        return self.status[4:]


class MiddlewareError(HTTPError):
    """Error class for middleware related errors."""

    message = '509 Middleware Error'
