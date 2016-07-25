from datetime.datetime import utcnow
from time import time

from .errors import PayloadExpired
from .utils import date_to_str
from .utils import LookupDict

# Field name mappings for all payload fields
FIELD_MAPPINGS = {
    'action': 'a',
    'address': 'a',
    'arguments': 'a',
    'attributes': 'a',
    'available': 'a',
    'array_format': 'af',
    'body': 'b',
    'buffers': 'b',
    'busy': 'b',
    'cached': 'c',
    'call': 'c',
    'calls': 'c',
    'code': 'c',
    'collection': 'c',
    'command': 'c',
    'config': 'c',
    'count': 'c',
    'cpu': 'c',
    'data': 'd',
    'datetime': 'd',
    'default_value': 'd',
    'disk': 'd',
    'path_delimiter': 'd',
    'allow_empty_value': 'e',
    'entity_path': 'e',
    'errors': 'e',
    'error': 'E',
    'enum': 'em',
    'exclusive_minimum': 'en',
    'exclusive_maximum': 'ex',
    'family': 'f',
    'filename': 'f',
    'files': 'f',
    'format': 'f',
    'form_data': 'f',
    'free': 'f',
    'header': 'h',
    'headers': 'h',
    'id': 'i',
    'idle': 'i',
    'in': 'i',
    'items': 'i',
    'primary_key': 'k',
    'laddr': 'l',
    'level': 'l',
    'links': 'l',
    'memory': 'm',
    'message': 'm',
    'meta': 'm',
    'method': 'm',
    'mime': 'm',
    'minimum': 'mn',
    'multiple_of': 'mo',
    'maximum': 'mx',
    'name': 'n',
    'network': 'n',
    'minimum_items': 'ni',
    'minimum_length': 'nl',
    'origin': 'o',
    'out': 'o',
    'params': 'p',
    'path': 'p',
    'pattern': 'p',
    'percent': 'p',
    'pid': 'p',
    'post_data': 'p',
    'query': 'q',
    'raddr': 'r',
    'reads': 'r',
    'request': 'r',
    'required': 'r',
    'relations': 'r',
    'response': 'R',
    'schema': 's',
    'scope': 's',
    'service': 's',
    'shared': 's',
    'size': 's',
    'status': 's',
    'swap': 's',
    'system': 's',
    'terminate': 't',
    'token': 't',
    'total': 't',
    'transactions': 't',
    'transport': 't',
    'type': 't',
    'url': 'u',
    'used': 'u',
    'user': 'u',
    'userland': 'u',
    'unique_items': 'ui',
    'version': 'v',
    'iowait': 'w',
    'writes': 'w',
    'execution_timeout': 'x',
    'maximum_items': 'xi',
    'maximum_length': 'xl',
}


class Payload(LookupDict):
    """Class to wrap and access payload data using paths.

    Global payload field names mappings are used by default.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use global payload field name mappings
        self.set_mappings(FIELD_MAPPINGS)


class ErrorPayload(Payload):
    """Class definition for error payloads."""

    def __init__(self, message, code=None, status=None):
        super().__init__()
        self.set('error/message', message)
        self.set('error/code', code)
        self.set('error/status', status or '500 Internal Server Error')


class ShortLivedPayload(Payload):
    """Payload class that support a time to live (TTL) period.

    This class will raise `PayloadExpired` each time its items are
    accessed and TTL expired.

    Default TTL is 8 seconds.

    """

    def __init__(self, *args, **kwargs):
        self.__time = time()
        super().__init__(*args, **kwargs)
        self.ttl = 8.0

    @property
    def alive_offset(self):
        """Seconds since payload creation.

        :rtype: float.

        """

        return time() - self.__time

    @property
    def is_valid(self):
        """Check that payload is still valid.

        Payload is valid when TTL since creation didn't expire.

        :rtype: bool.

        """

        return self.alive_offset < self.ttl

    def validate_time_to_live(self):
        """Validate that TTL is still valid.

        Payload expiration exception is raised whe TTL expires.

        :raises: PayloadExpired.

        """

        if not self.is_valid:
            raise PayloadExpired(self.alive_offset - self.ttl)

    def __getitem__(self, key):
        """Get a dictionary value."""

        self.validate_time_to_live()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        """Updates a dictionary value."""

        self.validate_time_to_live()
        return super().__setitem__(key, value)


class MetaPayload(Payload):
    """Class definition for request/response meta payloads."""

    @classmethod
    def new(cls, version, request_id, date_time=None):
        payload = cls()
        payload.set('version', version)
        payload.set('id', request_id)
        payload.set('datetime', date_to_str(date_time or utcnow()))
        return payload


class RequestPayload(Payload):
    """Class definition for request payloads."""

    @classmethod
    def new(cls, request, files=None):
        payload = cls()
        payload.set('version', request.version)
        payload.set('method', request.method)
        payload.set('url', request.url)
        payload.set('query', request.query.multi_items())
        payload.set('post_data', request.post_data.multi_items())
        payload.set('headers', request.headers)
        payload.set('body', request.body)
        payload.set('files', files or {})
        return payload


class ServiceCallPayload(Payload):
    """Class definition for service call payloads."""

    @classmethod
    def new(cls):
        payload = cls()
        payload.set('service', '')
        payload.set('version', '')
        payload.set('action', '')
        payload.set('params', '')
        return payload


class ResponsePayload(Payload):
    """Class definition for response payloads."""

    @classmethod
    def new(cls, headers=None, **kwargs):
        payload = cls()
        payload.set('version', kwargs.get('version') or '1.1')
        payload.set('status', kwargs.get('status') or '200 OK')
        payload.set('body', kwargs.get('body') or '')
        if headers:
            payload.set('headers', headers)

        return payload


class TransportPayload(Payload):
    """Class definition for transport payloads."""

    @classmethod
    def new(cls, version, request_id, origin, date_time=None):
        payload = cls()
        payload.set('meta/version', version)
        payload.set('meta/id', request_id)
        payload.set('meta/datetime', date_to_str(date_time or utcnow()))
        payload.set('meta/origin', origin)
        payload.set('meta/level', 1)
        payload.set('meta/userland', {})
        payload.set('body', {})
        payload.set('files', {})
        payload.set('data', {})
        payload.set('relations', {})
        payload.set('links', {})
        payload.set('calls', {})
        payload.set('transactions', {})
        payload.set('errors', {})
        return payload


class CommandPayload(Payload):
    """Class definition for command payloads."""

    @classmethod
    def new(cls, name, scope, args=None):
        payload = cls()
        payload.set('command/name', name)
        payload.set('command/arguments', args)
        payload.set('meta/scope', scope)
        return payload
