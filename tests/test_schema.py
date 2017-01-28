import pytest

from katana import schema
from katana import utils
from katana.errors import KatanaError


def test_schema_registry():
    # Error is raised when registry is not initialized
    with pytest.raises(KatanaError):
        schema.get_schema_registry()

    # Create the singleton
    registry = schema.SchemaRegistry()

    assert schema.get_schema_registry() == registry

    # Check empty value validation
    assert registry.is_empty(utils.EMPTY)
    # Empty string is not THE empty value
    assert registry.is_empty('') is False

    expected = 'RESULT'

    # Initially registry has no mappings
    assert registry.has_mappings is False
    registry.update_registry({'data': {'field': expected}})
    assert registry.has_mappings

    # Check paths
    assert registry.path_exists('data/field')
    assert registry.path_exists('missing/path') is False

    # Get value from registry
    assert registry.get('data/field') == expected
    assert registry.get('data|field', delimiter='|') == expected

    # Try to get value from missing path without default
    with pytest.raises(KeyError):
        registry.get('missing/path')

    # ... and with a default
    assert registry.get('missing/path', default='DEFAULT') == 'DEFAULT'
