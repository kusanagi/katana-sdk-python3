from time import time

from .errors import PayloadExpired
from .utils import date_to_str
from .utils import LookupDict
from .utils import utcnow

# Field name mappings for all payload fields
FIELD_MAPPINGS = {
    'action': 'a',
    'address': 'a',
    'arguments': 'a',
    'attributes': 'a',
    'available': 'a',
    'actions': 'ac',
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
    'component': 'c',
    'config': 'c',
    'count': 'c',
    'cpu': 'c',
    'consumes': 'cn',
    'data': 'd',
    'datetime': 'd',
    'default_value': 'd',
    'disk': 'd',
    'path_delimiter': 'd',
    'allow_empty': 'e',
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
    'result': 'r',
    'response': 'R',
    'schema': 's',
    'schemes': 's',
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
    'value': 'v',
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

    # Payload entity name
    name = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use global payload field name mappings
        self.set_mappings(FIELD_MAPPINGS)

    def entity(self, name=None):
        """Get payload as an entity.

        When a payload is created it contains all fields as first
        level values. A payload entity moves all fields in payload
        to a "namespace"; This way is possible to reference fields
        using a path like 'entity-name/field' instead of just using
        'field'.

        :param name: Alternative entity name to use.
        :type nme: str.

        :rtype: `Payload`

        """

        name = name or self.name
        if name:
            payload = Payload()
            payload.set(name, self)
            return payload

        return self


class ErrorPayload(Payload):
    """Class definition for error payloads."""

    name = 'error'

    @classmethod
    def new(cls, message=None, code=None, status=None):
        payload = cls()
        payload.set('message', message or 'Internal Server Error')
        payload.set('code', code)
        payload.set('status', status or '500 Internal Server Error')
        return payload


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

    name = 'meta'

    @classmethod
    def new(cls, version, request_id, date_time=None):
        payload = cls()
        payload.set('version', version)
        payload.set('id', request_id)
        payload.set('datetime', date_to_str(date_time or utcnow()))
        return payload


class RequestPayload(Payload):
    """Class definition for request payloads."""

    name = 'request'

    @classmethod
    def new(cls, request, files=None):
        payload = cls()
        payload.set('version', request.version)
        payload.set('method', request.method)
        payload.set('url', request.url)
        payload.set('query', list(request.query.multi_items()))
        payload.set('post_data', list(request.post_data.multi_items()))
        payload.set('headers', request.headers)
        payload.set('body', request.body)
        payload.set('files', files or {})
        return payload


class ServiceCallPayload(Payload):
    """Class definition for service call payloads."""

    name = 'call'

    @classmethod
    def new(cls, service=None, version=None, action=None):
        payload = cls()
        payload.set('service', service or '')
        payload.set('version', version or '')
        payload.set('action', action or '')
        return payload


class ResponsePayload(Payload):
    """Class definition for response payloads."""

    name = 'response'

    @classmethod
    def new(cls, version=None, status=None, body=None, headers=None):
        payload = cls()
        payload.set('version', version or '1.1')
        payload.set('status', status or '200 OK')
        payload.set('body', body or '')
        if headers:
            payload.set('headers', headers)

        return payload


class TransportPayload(Payload):
    """Class definition for transport payloads."""

    name = 'transport'

    @classmethod
    def new(cls, version, request_id, origin=None, date_time=None):
        payload = cls()
        payload.set('meta/version', version)
        payload.set('meta/id', request_id)
        payload.set('meta/datetime', date_to_str(date_time or utcnow()))
        payload.set('meta/origin', origin or '')
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

    name = 'command'

    @classmethod
    def new(cls, name, scope, args=None):
        payload = cls()
        payload.set('command/name', name)
        payload.set('command/arguments', args)
        payload.set('meta/scope', scope)
        return payload


class CommandResultPayload(Payload):
    """Class definition for command result payloads."""

    name = 'command'

    @classmethod
    def new(cls, name, result=None):
        payload = cls()
        payload.set('name', name)
        payload.set('result', result)
        return payload
