from katana import urn
from katana.api.response import Response
from katana.api.transport import Transport
from katana.api.http.request import HttpRequest
from katana.api.http.response import HttpResponse
from katana.schema import SchemaRegistry


def test_api_response():
    SchemaRegistry()

    values = {
        'attributes': {},
        'transport': Transport({}),
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        }

    response = Response(**values)
    assert response.get_gateway_protocol() == values['gateway_protocol']
    assert response.get_gateway_address() == values['gateway_addresses'][1]
    assert response.get_transport() == values['transport']
    # By default no HTTP request or response are created
    assert response.get_http_request() is None
    assert response.get_http_response() is None

    # Create a new response with HTTP request and response data
    values['http_request'] = {
        'method': 'GET',
        'url': 'http://foo.com/bar/index/',
        }
    values['http_response'] = {
        'status_code': 200,
        'status_text': 'OK',
        }
    response = Response(**values)
    assert isinstance(response.get_http_request(), HttpRequest)
    assert isinstance(response.get_http_response(), HttpResponse)
