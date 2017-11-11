import sys

from katana.api.schema.param import ParamSchema
from katana.api.schema.param import HttpParamSchema
from katana.payload import Payload


def test_api_schema_param(read_json):
    # Check param schema defaults
    schema = ParamSchema('foo', {})
    assert schema.get_name() == 'foo'
    assert schema.get_type() == 'string'
    assert schema.get_format() == ''
    assert schema.get_array_format() == 'csv'
    assert schema.get_pattern() == ''
    assert not schema.allow_empty()
    assert not schema.has_default_value()
    assert schema.get_default_value() is None
    assert not schema.is_required()
    assert schema.get_items() == {}
    assert schema.get_max() == sys.maxsize
    assert not schema.is_exclusive_max()
    assert schema.get_min() == -sys.maxsize - 1
    assert not schema.is_exclusive_min()
    assert schema.get_max_length() == -1
    assert schema.get_min_length() == -1
    assert schema.get_max_items() == -1
    assert schema.get_min_items() == -1
    assert not schema.has_unique_items()
    assert schema.get_enum() == []
    assert schema.get_multiple_of() == -1

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpParamSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_input() == 'query'
    assert http_schema.get_param() == schema.get_name()

    # Create a payload with param schema data
    payload = Payload(read_json('schema-param'))

    # Check param schema with values
    schema = ParamSchema('foo', payload)
    assert schema.get_name() == 'foo'
    assert schema.get_type() == payload.get('type')
    assert schema.get_format() == payload.get('format')
    assert schema.get_array_format() == payload.get('array_format')
    assert schema.get_pattern() == payload.get('pattern')
    assert schema.allow_empty()
    assert schema.has_default_value()
    assert schema.get_default_value() == payload.get('default_value')
    assert schema.is_required()
    assert schema.get_items() == payload.get('items')
    assert schema.get_max() == payload.get('max')
    assert schema.is_exclusive_max()
    assert schema.get_min() == payload.get('min')
    assert schema.is_exclusive_min()
    assert schema.get_max_length() == payload.get('max_length')
    assert schema.get_min_length() == payload.get('min_length')
    assert schema.get_max_items() == payload.get('max_items')
    assert schema.get_min_items() == payload.get('min_items')
    assert schema.has_unique_items()
    assert schema.get_enum() == payload.get('enum')
    assert schema.get_multiple_of() == payload.get('multiple_of')

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpParamSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_input() == payload.get('http/input')
    assert http_schema.get_param() == payload.get('http/param')
