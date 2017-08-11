import pytest

from katana.api import base
from katana.api.schema.service import ServiceSchema
from katana.errors import KatanaError
from katana.schema import get_schema_registry
from katana.schema import SchemaRegistry


def test_api_base(mocker):
    SchemaRegistry()

    values = {
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        }

    component = mocker.MagicMock()
    api = base.Api(component, **values)

    # Check defaults
    assert not api.is_debug()
    assert not api.has_variable('foo')
    assert api.get_variables() == {}

    # Check values
    assert api.get_framework_version() == values['framework_version']
    assert api.get_path() == values['path']
    assert api.get_name() == values['name']
    assert api.get_version() == values['version']

    # Prepare component and check that is properly called
    resource_name = 'foo'
    expected_resource = 'RESOURCE'
    component.has_resource.return_value = True
    component.get_resource.return_value = expected_resource
    assert api.has_resource(resource_name)
    component.has_resource.assert_called(resource_name)
    assert api.get_resource(resource_name) == expected_resource
    component.get_resource.assert_called(resource_name)

    # Check other values that were defaults
    variables = {'foo': 'bar'}
    api = base.Api(component, variables=variables, debug=True, **values)
    assert api.is_debug()
    assert api.has_variable('foo')
    assert api.get_variables() == variables
    assert api.get_variable('foo') == variables['foo']


def test_api_base_get_services(registry):
    api = base.Api(**{
        'component': None,
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    # Get services is empty when there are no service mappings
    assert api.get_services() == []

    # Add data to registry
    svc_name = 'foo'
    svc_version = '1.0.0'
    registry.update_registry({svc_name: {svc_version: {}}})

    # Get services must return service name and version
    assert api.get_services() == [{'name': svc_name, 'version': svc_version}]


def test_api_base_get_service_schema(mocker):
    mocker.patch('katana.schema.SchemaRegistry')

    # Get the mocked SchemaRegistry
    registry = get_schema_registry()

    api = base.Api(**{
        'component': None,
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    svc_name = 'foo'
    svc_version = '1.0.0'
    path = '{}/{}'.format(svc_name, svc_version)
    payload = {'foo': 'bar'}

    # Check error for empty schemas
    registry.get.return_value = None
    with pytest.raises(base.ApiError):
        api.get_service_schema(svc_name, svc_version)

    # Check that schema registry get was called with proper service path
    registry.get.assert_called(path, None)

    # Check getting a service schema
    init = mocker.patch(
        'katana.api.schema.service.ServiceSchema.__init__',
        return_value=None,
        )
    registry.get = mocker.MagicMock(return_value=payload)
    svc_schema = api.get_service_schema(svc_name, svc_version)
    assert isinstance(svc_schema, ServiceSchema)
    registry.get.assert_called(path, None)
    init.assert_called(svc_name, svc_version, payload)

    # Check getting a service schema using a wildcard version
    expected_version = '1.0.0'
    resolve = mocker.patch('katana.versions.VersionString.resolve')
    resolve.return_value = expected_version
    svc_schema = api.get_service_schema(svc_name, '*.*.*')
    assert isinstance(svc_schema, ServiceSchema)
    init.assert_called(svc_name, expected_version, payload)

    # Check unresolved wildcard versions (resolve should raise KatanaError)
    resolve.side_effect = KatanaError
    with pytest.raises(KatanaError):
        api.get_service_schema(svc_name, '*.*.*')


def test_api_base_log(mocker, logs):
    SchemaRegistry()

    values = {
        'component': None,
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        }

    log_message = 'Test log message'
    api = base.Api(**values)
    # When debug is false no logging is done
    assert not api.is_debug()
    api.log(log_message)
    out = logs.getvalue()
    # There should be no ouput at all
    assert len(out) == 0

    # Create an instance with debug on
    api = base.Api(debug=True, **values)
    assert api.is_debug()
    api.log(log_message)
    out = logs.getvalue()
    assert out.rstrip() == log_message
