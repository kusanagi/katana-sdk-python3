import pytest

from katana import urn
from katana.api.http.request import HttpRequest
from katana.api.param import Param
from katana.api.param import TYPE_INTEGER
from katana.api.param import TYPE_NULL
from katana.api.request import Request
from katana.api.response import Response
from katana.api.transport import Transport
from katana.schema import SchemaRegistry


def test_api_request():
    SchemaRegistry()

    service_name = 'foo'
    service_version = '1.1'
    action_name = 'bar'
    values = {
        'attributes': {},
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'client_address': '205.81.5.62:7681',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        }

    request = Request(**values)
    assert request.get_gateway_protocol() == values['gateway_protocol']
    assert request.get_gateway_address() == values['gateway_addresses'][1]
    assert request.get_client_address() == values['client_address']
    assert request.get_service_name() == ''
    assert request.get_service_version() == ''
    assert request.get_action_name() == ''
    assert request.get_http_request() is None

    # Check service related setters
    request.set_service_name(service_name)
    request.set_service_version(service_version)
    request.set_action_name(action_name)
    assert request.get_service_name() == service_name
    assert request.get_service_version() == service_version
    assert request.get_action_name() == action_name

    # Check parameters
    assert request.get_params() == []
    assert request.has_param('foo') is False
    param = request.get_param('foo')
    assert isinstance(param, Param)
    assert not param.exists()

    param = Param('foo', value=42)
    assert request.set_param(param) == request
    assert request.has_param('foo')

    # Result is not the same parameter, but is has the same values
    foo_param = request.get_param('foo')
    assert foo_param != param
    assert foo_param.get_name() == param.get_name()
    assert foo_param.get_type() == param.get_type()
    assert foo_param.get_value() == param.get_value()

    params = request.get_params()
    assert len(params) == 1
    foo_param = params[0]
    assert foo_param.get_name() == param.get_name()
    assert foo_param.get_type() == param.get_type()
    assert foo_param.get_value() == param.get_value()


def test_api_request_new_response():
    SchemaRegistry()

    values = {
        'attributes': {},
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'client_address': '205.81.5.62:7681',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        }
    request = Request(**values)

    # Create an HTTP response with default values
    response = request.new_response()
    assert isinstance(response, Response)
    assert response.get_gateway_protocol() == request.get_gateway_protocol()
    assert response.get_gateway_address() == request.get_gateway_address()
    assert isinstance(response.get_transport(), Transport)
    # An HTTP response is created when using HTTP as protocol
    http_response = response.get_http_response()
    assert http_response is not None
    assert http_response.get_status() == '200 OK'

    # Create a response with HTTP status values
    response = request.new_response(418, "I'm a teapot")
    assert isinstance(response, Response)
    http_response = response.get_http_response()
    assert http_response is not None
    assert http_response.get_status() == "418 I'm a teapot"

    # Create a response for other ptotocol
    values['gateway_protocol'] = urn.KTP
    request = Request(**values)
    response = request.new_response()
    assert isinstance(response, Response)
    assert response.get_gateway_protocol() == request.get_gateway_protocol()
    assert response.get_gateway_address() == request.get_gateway_address()
    assert isinstance(response.get_transport(), Transport)
    # Check that no HTTP response was created
    assert response.get_http_response() is None

    # Create an HTTP request with request data
    values['gateway_protocol'] = urn.HTTP
    values['http_request'] = {
        'method': 'GET',
        'url': 'http://foo.com/bar/index/',
        }
    request = Request(**values)
    assert isinstance(request.get_http_request(), HttpRequest)


def test_api_request_new_param():
    SchemaRegistry()

    values = {
        'attributes': {},
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'client_address': '205.81.5.62:7681',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        }
    request = Request(**values)

    # Create a param with default values
    param = request.new_param('foo')
    assert isinstance(param, Param)
    assert param.get_name() == 'foo'
    assert param.exists()
    assert param.get_value() is None
    assert param.get_type() == TYPE_NULL

    # Create a parameter with type and value
    param = request.new_param('foo', value=42, type=TYPE_INTEGER)
    assert isinstance(param, Param)
    assert param.get_name() == 'foo'
    assert param.exists()
    assert param.get_value() == 42
    assert param.get_type() == TYPE_INTEGER

    # Check error when a parameter has inconsisten type and value
    with pytest.raises(TypeError):
        request.new_param('foo', value=True, type=TYPE_INTEGER)
