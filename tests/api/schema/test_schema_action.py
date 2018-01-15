import pytest

from katana.api.schema.action import ActionSchema
from katana.api.schema.action import ActionSchemaError
from katana.api.schema.action import HttpActionSchema
from katana.api.schema.file import FileSchema
from katana.api.schema.param import ParamSchema
from katana.payload import Payload


def test_api_schema_action_defaults():
    action = ActionSchema('foo', {})

    assert action.get_name() == 'foo'
    assert not action.is_deprecated()
    assert not action.is_collection()
    assert action.get_entity_path() == ''
    assert action.get_path_delimiter() == '/'
    assert action.resolve_entity({}) == {}
    assert not action.has_entity_definition()
    assert action.get_entity() == {}
    assert not action.has_relations()
    assert action.get_relations() == []
    assert not action.has_call('foo')
    assert not action.has_calls()
    assert action.get_calls() == []
    assert not action.has_defer_call('foo')
    assert not action.has_defer_calls()
    assert action.get_defer_calls() == []
    assert not action.has_remote_call('ktp://87.65.43.21:4321')
    assert not action.has_remote_calls()
    assert action.get_remote_calls() == []
    assert not action.has_return()
    assert action.get_return_type() == ''
    assert action.get_tags() == []
    assert not action.has_tag('foo')
    assert action.get_params() == []
    assert not action.has_param('foo')

    with pytest.raises(ActionSchemaError):
        action.get_param_schema('foo')

    assert action.get_files() == []
    assert not action.has_file('foo')

    with pytest.raises(ActionSchemaError):
        action.get_file_schema('foo')

    http_schema = action.get_http_schema()
    assert isinstance(http_schema, HttpActionSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_method() == 'get'
    assert http_schema.get_path() == ''
    assert http_schema.get_input() == 'query'
    assert http_schema.get_body() == 'text/plain'


def test_api_schema_action(read_json):
    # Get schema info for 'foo' action
    payload = Payload(read_json('schema-service'))
    assert payload.path_exists('actions/foo')
    payload = payload.get('actions/foo')
    assert isinstance(payload, dict)
    payload = Payload(payload)

    action = ActionSchema('foo', payload)

    assert action.get_name() == 'foo'
    assert action.is_deprecated()
    assert action.is_collection()
    assert action.get_entity_path() == payload.get('entity_path')
    assert action.get_path_delimiter() == payload.get('path_delimiter')
    assert action.resolve_entity({'foo': {'bar': 'OK'}}) == 'OK'
    # Resolve an invalid entity
    with pytest.raises(ActionSchemaError):
        action.resolve_entity({'foo': {'MISSING': 'OK'}})

    # Check entity schema related methods
    assert action.has_entity_definition()
    entity = action.get_entity()
    assert isinstance(entity, dict)
    assert len(entity) == 3
    assert sorted(entity.keys()) == ['field', 'fields', 'validate']

    # Check return value
    assert action.has_return()
    assert action.get_return_type() == payload.get('return/type')

    # Check tags
    tags = action.get_tags()
    assert len(tags) == 2
    for tag in ['foo', 'bar']:
        assert tag in tags

    # Check relations
    assert action.has_relations()
    assert sorted(action.get_relations()) == [
        ['many', 'posts'],
        ['one', 'accounts'],
        ]

    # Check runtime calls
    assert action.has_calls()
    assert sorted(action.get_calls()) == [
        ['bar', '1.1', 'dummy'],
        ['foo', '1.0', 'dummy'],
        ]
    assert action.has_call('foo', '1.0', 'dummy')
    # Check invalid local call arguments
    assert not action.has_call('MISSING')
    assert not action.has_call('foo', 'MISSING')
    assert not action.has_call('foo', '1.0', 'MISSING')

    # Check deferred calls
    assert action.has_defer_calls()
    assert sorted(action.get_defer_calls()) == [
        ['bar', '1.1', 'dummy'],
        ['foo', '1.0', 'dummy'],
        ]
    assert action.has_defer_call('foo', '1.0', 'dummy')
    # Check invalid local call arguments
    assert not action.has_defer_call('MISSING')
    assert not action.has_defer_call('foo', 'MISSING')
    assert not action.has_defer_call('foo', '1.0', 'MISSING')

    # Check files
    assert action.has_file('upload')
    assert action.get_files() == ['upload']

    # Check params
    assert action.has_param('value')
    assert action.get_params() == ['value']

    # Check remote calls
    assert action.has_remote_calls()
    remote = 'ktp://87.65.43.21:4321'
    remote_calls = [[remote, 'foo', '1.0', 'dummy']]
    assert sorted(action.get_remote_calls()) == remote_calls
    assert action.has_remote_call(*remote_calls[0])
    # Check invalid remote call arguments
    assert not action.has_remote_call('MISSING')
    assert not action.has_remote_call(remote, 'MISSING')
    assert not action.has_remote_call(remote, 'foo', 'MISSING')
    assert not action.has_remote_call(remote, 'foo', '1.0', 'MISSING')

    # Check HTTP schema
    http_schema = action.get_http_schema()
    assert isinstance(http_schema, HttpActionSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_method() == payload.get('http/method')
    assert http_schema.get_path() == payload.get('http/path')
    assert http_schema.get_input() == payload.get('http/input')
    assert http_schema.get_body().split(',') == payload.get('http/body')

    # Check file schema
    file_schema = action.get_file_schema('upload')
    assert isinstance(file_schema, FileSchema)

    # Check param schema
    param_schema = action.get_param_schema('value')
    assert isinstance(param_schema, ParamSchema)
