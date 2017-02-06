import sys

from katana.api.schema.file import FileSchema
from katana.api.schema.file import HttpFileSchema
from katana.payload import Payload


def test_api_schema_file(read_json):
    # Check file schema defaults
    schema = FileSchema('foo', {})
    assert schema.get_name() == 'foo'
    assert schema.get_mime() == 'text/plain'
    assert not schema.is_required()
    assert schema.get_max() == sys.maxsize
    assert not schema.is_exclusive_max()
    assert schema.get_min() == 0
    assert not schema.is_exclusive_min()

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpFileSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_param() == schema.get_name()

    # Create a payload with file schema data
    payload = Payload(read_json('schema-file'))

    # Check file schema with values
    schema = FileSchema('foo', payload)
    assert schema.get_name() == 'foo'
    assert schema.get_mime() == payload.get('mime')
    assert schema.is_required()
    assert schema.get_max() == payload.get('max')
    assert schema.is_exclusive_max()
    assert schema.get_min() == payload.get('min')
    assert schema.is_exclusive_min()

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpFileSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_param() == payload.get('http/param')
