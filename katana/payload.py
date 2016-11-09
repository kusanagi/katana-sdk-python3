"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

from time import time

from . import utils
from .errors import PayloadExpired
from .utils import date_to_str
from .utils import EMPTY
from .utils import LookupDict
from .utils import utcnow

# Disable field mappings in all payloads
DISABLE_FIELD_MAPPINGS = False

# Field name mappings for all payload fields
FIELD_MAPPINGS = {
    'action': 'a',
    'address': 'a',
    'arguments': 'a',
    'attributes': 'a',
    'available': 'a',
    'actions': 'ac',
    'array_format': 'af',
    'base_path': 'b',
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
    'command_reply': 'cr',
    'data': 'd',
    'datetime': 'd',
    'default_value': 'd',
    'deprecated': 'dp',
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
    'form-data': 'f',  # Maps to parameter location name
    'free': 'f',
    'gateway': 'g',
    'header': 'h',
    'headers': 'h',
    'http': 'h',
    'http_body': 'hb',
    'http_input': 'hi',
    'http_method': 'hm',
    'http_security': 'hs',
    'id': 'i',
    'idle': 'i',
    'in': 'i',
    'input': 'i',
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
    'properties': 'p',
    'protocol': 'p',
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
    'type': 't',
    'transport': 'T',
    'url': 'u',
    'used': 'u',
    'user': 'u',
    'unique_items': 'ui',
    'value': 'v',
    'version': 'v',
    'iowait': 'w',
    'writes': 'w',
    'execution_timeout': 'x',
    'maximum_items': 'xi',
    'maximum_length': 'xl',
}


def get_path(payload, path, default=EMPTY, mappings=None):
    """Get payload dictionary value by path.

    Global payload field mappings are used when no mappings are given.

    See: `katana.utils.get_path`.

    :param payload: A dictionaty like object.
    :type payload: dict
    :param path: Path to a value.
    :type path: str
    :param default: Default value to return when value is not found.
    :type default: object

    :raises: `KeyError`

    :returns: The value for the given path.
    :rtype: object

    """

    return utils.get_path(payload, path, default, mappings or FIELD_MAPPINGS)


def set_path(payload, path, value, mappings=None):
    return utils.set_path(payload, path, value, mappings or FIELD_MAPPINGS)


def path_exists(payload, path, default=EMPTY, mappings=None):
    """Check if a path is available.

    :rtype: bool.

    """

    try:
        utils.get_path(payload, path, default, mappings or FIELD_MAPPINGS)
    except KeyError:
        return False
    else:
        return True


class Payload(LookupDict):
    """Class to wrap and access payload data using paths.

    Global payload field names mappings are used by default.

    """

    # Payload entity name
    name = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use global payload field name mappings
        if not DISABLE_FIELD_MAPPINGS:
            self.set_mappings(FIELD_MAPPINGS)

    def set_mappings(self, mappings):
        if not DISABLE_FIELD_MAPPINGS:
            super().set_mappings(mappings)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_defaults({
            'message': 'Unknown error',
            'code': 0,
            'status': '500 Internal Server Error',
            })

    @classmethod
    def new(cls, message=None, code=None, status=None):
        payload = cls()
        if message:
            payload.set('message', message)

        if code:
            payload.set('code', code)

        if status:
            payload.set('status', status)

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
        payload.set('body', request.body or '')
        if request.query:
            payload.set('query', request.query)

        if request.post_data:
            payload.set('post_data', request.post_data)

        if request.headers:
            payload.set('headers', request.headers)

        if files:
            payload.set('files', files)

        return payload


class ServiceCallPayload(Payload):
    """Class definition for service call payloads."""

    name = 'call'

    @classmethod
    def new(cls, service=None, version=None, action=None, params=None):
        payload = cls()
        payload.set('service', service or '')
        payload.set('version', version or '')
        payload.set('action', action or '')
        payload.set('params', params or [])
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_defaults({
            'body': {},
            'files': {},
            'data': {},
            'relations': {},
            'links': {},
            'calls': {},
            'transactions': {},
            'errors': {},
            })

    @classmethod
    def new(cls, version, request_id, origin=None, date_time=None, **kwargs):
        payload = cls()
        payload.set('meta/version', version)
        payload.set('meta/id', request_id)
        payload.set('meta/datetime', date_to_str(date_time or utcnow()))
        payload.set('meta/origin', origin or [])
        payload.set('meta/level', 1)
        if kwargs.get('properties'):
            payload.set('meta/properties', kwargs['properties'])

        return payload


class CommandPayload(Payload):
    """Class definition for command payloads."""

    name = 'command'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_defaults({
            'command/arguments': None,
            })

    @classmethod
    def new(cls, name, scope, args=None):
        payload = cls()
        payload.set('command/name', name)
        payload.set('meta/scope', scope)
        if args:
            payload.set('command/arguments', args)

        return payload


class CommandResultPayload(Payload):
    """Class definition for command result payloads."""

    name = 'command_reply'

    @classmethod
    def new(cls, name, result=None):
        payload = cls()
        payload.set('name', name)
        payload.set('result', result)
        return payload
