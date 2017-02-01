from datetime import datetime

import pytest
import katana.payload as payload_module

from katana.payload import delete_path
from katana.payload import get_path
from katana.payload import path_exists
from katana.payload import Payload
from katana.payload import set_path


def test_payload():
    payload = Payload({'d': {'v': 1}})

    # Give payload an entity name
    payload.name = 'test'
    # Entity is a new payload
    assert payload != payload.entity()
    # Check that entity name does not exist in payload data before creating it
    assert not path_exists(payload, 'test')
    payload = payload.entity()
    payload.name = 'test'
    assert payload.is_entity
    assert path_exists(payload, 'test')
    # Undo entity to have data without entity name
    payload = payload.entity(undo=True)
    payload.name = 'test'
    assert not payload.is_entity
    assert not path_exists(payload, 'test')
    # When there is no entity name and undo is not called it must return self
    payload.name = None
    assert payload.entity() == payload


def test_payload_mappings():
    # Check disabling mappings (by default mappings are enabled)
    assert not payload_module.DISABLE_FIELD_MAPPINGS
    # Create a payload that contains an unmapped name "abc"
    payload = Payload({'d': {'abc': True}})
    # Naturally "new_mapping" does not exists
    assert not payload.path_exists('data/new_mapping')
    # ... and the unmapped field does
    assert payload.path_exists('data/abc')

    # Add mappings for current fields
    payload.set_mappings({'data': 'd', 'new_mapping': 'abc'})
    # Now "abc" can be accessed using mapped or unmapped name
    assert payload.path_exists('data/new_mapping')
    assert payload.path_exists('data/abc')

    # Disable mappings
    payload_module.DISABLE_FIELD_MAPPINGS = True
    assert payload_module.DISABLE_FIELD_MAPPINGS

    # Create a payload wit mappings disabled
    payload = Payload({'d': {'abc': True}})
    payload.set_mappings({'data': 'd', 'new_mapping': 'abc'})
    assert not payload.path_exists('data/new_mapping')
    assert not payload.path_exists('data/abc')
    # Fields can only be traversed by real payload key name
    assert payload.path_exists('d/abc')
    # Restore flag to default value
    payload_module.DISABLE_FIELD_MAPPINGS = False


def test_payload_get_path():
    expected = 'RESULT'
    payload = Payload({'d': {'v': expected}})

    assert get_path(payload, 'data/value') == expected
    assert get_path(payload, 'data|value', delimiter='|') == expected
    assert get_path(payload, 'data/missing', default='DEFAULT') == 'DEFAULT'

    with pytest.raises(KeyError):
        get_path(payload, 'data/missing')


def test_payload_set_path():
    expected = 'RESULT'
    payload = Payload({'d': {'v': 1}})

    assert not path_exists(payload, 'data/missing')
    assert set_path(payload, 'data/missing', expected) == payload
    assert get_path(payload, 'data/missing', default='B') == expected


def test_payload_delete_path():
    payload = Payload({'d': {'v': 1}})

    # Delete using a simple name as path
    assert path_exists(payload, 'data')
    assert delete_path(payload, 'data')
    assert not path_exists(payload, 'data')
    assert not delete_path(payload, 'data')

    # Delete using a path
    set_path(payload, 'data/value', 1)
    assert path_exists(payload, 'data/value')
    assert delete_path(payload, 'data/value')
    assert not path_exists(payload, 'data/value')
    assert not delete_path(payload, 'data/value')

    # Delete using a different delimiter
    set_path(payload, 'data/value', 1)
    assert path_exists(payload, 'data/value')
    assert delete_path(payload, 'data|value', delimiter='|')
    assert not path_exists(payload, 'data/value')
    assert not delete_path(payload, 'data/value')


def test_payload_path_exists():
    payload = Payload({'d': {'v': 1}})

    assert path_exists(payload, 'data')
    assert path_exists(payload, 'data/value')
    assert path_exists(payload, 'data|value', delimiter='|')
    assert not path_exists(payload, 'data/missing')


def test_error_payload():
    ErrorPayload = payload_module.ErrorPayload

    fields = {
        'message': 'Error message',
        'code': 99,
        'status': "418 I'm a teapot",
        }
    payload = ErrorPayload.new(**fields)
    for name, value in fields.items():
        assert payload.get(name) == value


def test_meta_payload():
    MetaPayload = payload_module.MetaPayload

    fields = {
        'version': '1.0.0',
        'id': 'KJNKDD987342',
        'protocol': 'http',
        'gateway': [],
        'client': '127.0.0.1:89098',
        }
    payload = MetaPayload.new(**fields)
    for name, value in fields.items():
        assert payload.get(name) == value

    assert payload.path_exists('datetime')
    assert isinstance(payload.get('datetime'), str)


def test_http_request_payload():
    HttpRequestPayload = payload_module.HttpRequestPayload

    class HttpRequest(object):
        version = '1.1'
        method = 'GET'
        url = 'http://foo.com/bar/index/'
        body = 'CONTENT'
        query = None
        post_data = None
        headers = None

    request = HttpRequest()

    # Check default values
    payload = HttpRequestPayload.new(request)
    assert payload.get('version', default=None) == request.version
    assert payload.get('method', default=None) == request.method
    assert payload.get('url', default=None) == request.url
    assert payload.get('body', default=None) == request.body
    # Optional values are not present by default
    assert not payload.path_exists('query')
    assert not payload.path_exists('post_data')
    assert not payload.path_exists('headers')
    assert not payload.path_exists('files')

    # Add all optional values to request
    request.query = {'foo': 'bar'}
    request.post_data = {'post_foo': 'post_bar'}
    request.headers = {'X-Type': '1'}
    files = [{'name': 'file'}]
    # .. and create a new payload
    payload = HttpRequestPayload.new(request, files=files)
    # Check optional values
    assert payload.get('query', default=None) == request.query
    assert payload.get('post_data', default=None) == request.post_data
    assert payload.get('headers', default=None) == request.headers
    assert payload.get('files', default=None) == files


def test_service_call_payload():
    ServiceCallPayload = payload_module.ServiceCallPayload

    fields = {
        'service': 'test',
        'version': '1.0.0',
        'action': 'foo',
        'params': [],
        }
    payload = ServiceCallPayload.new(**fields)
    for name, value in fields.items():
        assert payload.get(name) == value

    # Check defaults
    defaults = {
        'service': '',
        'version': '',
        'action': '',
        'params': [],
        }
    payload = ServiceCallPayload.new()
    for name, value in defaults.items():
        assert payload.get(name) == value


def test_response_payload():
    ResponsePayload = payload_module.ResponsePayload

    fields = {
        'version': '2.0',
        'status': "418 I'm a teapot",
        'body': 'CONTENTS',
        'headers': {'X-Type': 1},
        }
    payload = ResponsePayload.new(**fields)
    for name, value in fields.items():
        assert payload.get(name) == value

    # Check defaults
    defaults = {
        'version': '1.1',
        'status': "200 OK",
        'body': '',
        }
    payload = ResponsePayload.new()
    for name, value in defaults.items():
        assert payload.get(name) == value

    # By default headers are not added
    assert not payload.path_exists('headers')


def test_transport_payload():
    TransportPayload = payload_module.TransportPayload

    val = {
        'version': '1.0.0',
        'id': 'KJNKDD987342',
        'origin': [],
        'gateway': [],
        'properties': {'foo': 'bar'},
        }
    payload = TransportPayload.new(
        val['version'],
        val['id'],
        origin=val['origin'],
        date_time=datetime(2017, 1, 27, 20, 12, 8, 952811),
        gateway=val['gateway'],
        properties=val['properties'],
        )
    assert payload.get('meta/version') == val['version']
    assert payload.get('meta/id') == val['id']
    assert payload.get('meta/origin') == val['origin']
    assert payload.get('meta/gateway') == val['gateway']
    assert payload.get('meta/properties') == val['properties']
    assert payload.get('meta/datetime') == '2017-01-27T20:12:08.952811+00:00'

    # Level is initialized automatically as 1
    assert payload.get('meta/level', default=None) == 1

    # Check defaults for other fields
    fields = (
        'body', 'files', 'data', 'relations', 'links', 'calls',
        'transactions', 'errors'
        )
    for name in fields:
        assert payload.path_exists(name)
        # All these fields are empty by default
        assert payload.get(name) == {}

    # Check default values for meta
    payload = TransportPayload.new(val['version'], val['id'])
    assert payload.get('meta/origin', default='NONE') == []
    assert payload.get('meta/gateway', default='NONE') is None
    assert isinstance(payload.get('meta/datetime'), str)
    # When no properties are given field does not exist
    assert not payload.path_exists('meta/properties')


def test_command_payload():
    CommandPayload = payload_module.CommandPayload

    command = 'command'
    scope = 'gateway'
    args = {'foo': 'var'}
    payload = CommandPayload.new(command, scope, args=args)
    assert payload.get('meta/scope') == scope
    assert payload.get('command/name') == command
    assert payload.get('command/arguments') == args

    # Check defaults
    payload = CommandPayload.new(command, scope)
    assert payload.path_exists('command/arguments')
    assert payload.get('command/arguments') is None


def test_command_result_payload():
    CommandResultPayload = payload_module.CommandResultPayload

    fields = {
        'name': 'command',
        'result': 'Result string',
        }
    payload = CommandResultPayload.new(**fields)
    for name, value in fields.items():
        assert payload.get(name) == value

    # Check default values
    payload = CommandResultPayload.new('command')
    assert payload.path_exists('result')
    assert payload.get('result') is None
