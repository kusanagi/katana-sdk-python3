class KatanaError(Exception):
    """Base exception for Katana errors."""

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


class InvalidOrigin(PayloadError):
    """Error for invalid/unknown request origins.

    Used when origin is unknown to a service or is not handled by it.

    """

    message = 'Invalid origin'


class InvalidScope(PayloadError):
    """Error for invalid/unknown request scopes.

    Used when scope is unknown to a component or is not handled by it.

    """

    message = 'Invalid scope'


class HTTPError(KatanaError):
    """Base HTTP error exception."""

    message = '500 Internal Server Error'

    def __init__(self, body=None):
        super().__init__(self.message)
        self.body = body or self.message

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
