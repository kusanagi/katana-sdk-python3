from katana.api.http.response import HttpResponse


def test_api_http_response_protocol():
    response = HttpResponse(200, 'OK')

    # Check default protocol
    assert response.get_protocol_version() == '1.1'
    response.set_protocol_version(None)
    assert response.get_protocol_version() == '1.1'

    # Set a new protocol version
    response.set_protocol_version('2.0')
    assert response.get_protocol_version() == '2.0'

    assert response.is_protocol_version('1.1') is False
    assert response.is_protocol_version('2.0')

    # Create a response with a protocol version
    response = HttpResponse(200, 'OK', protocol_version='2.0')
    assert response.get_protocol_version() == '2.0'


def test_api_http_response_status():
    response = HttpResponse(200, 'OK')
    assert response.is_status('200 OK')
    assert response.get_status() == '200 OK'
    assert response.get_status_code() == 200
    assert response.get_status_text() == 'OK'

    response.set_status(500, 'Internal Server Error')
    assert response.is_status('500 Internal Server Error')
    assert response.get_status() == '500 Internal Server Error'
    assert response.get_status_code() == 500
    assert response.get_status_text() == 'Internal Server Error'


def test_api_http_response_headers():
    response = HttpResponse(200, 'OK')

    # By default there are no headers
    assert response.has_header('X-Type') is False
    assert response.get_header('X-Type') == ''
    assert response.get_headers() == {}

    # Set a new header
    expected = 'RESULT'
    assert response.set_header('X-Type', expected) == response
    assert response.has_header('X-Type')
    assert response.get_header('X-Type') == expected
    assert response.get_headers() == {'X-Type': [expected]}

    # Duplicate a header
    expected2 = 'RESULT-2'
    response.set_header('X-Type', expected2)
    assert response.has_header('X-Type')
    assert response.get_header('X-Type') == expected  # Gets first item
    assert response.get_headers() == {'X-Type': [expected, expected2]}

    # Create a response with headers
    response = HttpResponse(200, 'OK', headers={'X-Type': expected})
    assert response.has_header('X-Type')
    assert response.get_header('X-Type') == expected
    assert response.get_headers() == {'X-Type': [expected]}


def test_api_http_response_body():
    response = HttpResponse(200, 'OK')

    # By default body is empty
    assert response.get_body() == ''
    assert response.has_body() is False

    # Set a content for the response body
    expected = 'CONTENT'
    assert response.set_body(content=expected) == response
    assert response.get_body() == expected
    assert response.has_body()

    # Create a response with body
    response = HttpResponse(200, 'OK', body=expected)
    assert response.set_body(content=expected) == response
    assert response.get_body() == expected
    assert response.has_body()
