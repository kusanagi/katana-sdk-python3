from katana.api.http.request import HttpRequest
from katana.api.file import File
from katana.api.file import payload_to_file
from katana.utils import MultiDict


def test_api_http_request():
    method = 'GET'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    assert request.is_method('DELETE') is False
    assert request.is_method(method)
    assert request.get_method() == method

    assert request.get_url() == url
    assert request.get_url_scheme() == 'http'
    assert request.get_url_host() == 'foo.com'
    assert request.get_url_path() == '/bar/index'  # Final "/" is removed

    assert request.get_protocol_version() == '1.1'
    assert request.is_protocol_version('1.1')
    assert request.is_protocol_version('2.0') is False

    # Create a new request with a protocol version
    request = HttpRequest(method, url, protocol_version='2.0')
    assert request.get_protocol_version() == '2.0'
    assert request.is_protocol_version('2.0')
    assert request.is_protocol_version('1.1') is False


def test_api_http_request_query():
    method = 'GET'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    # By default there are no query params
    assert request.has_query_param('a') is False
    assert request.get_query_param('a') == ''
    assert request.get_query_param('a', default='B') == 'B'
    assert request.get_query_param_array('a') == []
    assert request.get_query_param_array('a', default=['B']) == ['B']
    assert request.get_query_params() == {}
    assert request.get_query_params_array() == {}

    # Create a request with query params
    expected = 1
    query = MultiDict({'a': expected, 'b': 2})
    request = HttpRequest(method, url, query=query)
    assert request.has_query_param('a')
    assert request.get_query_param('a') == expected
    assert request.get_query_param('a', default='B') == expected
    assert request.get_query_param_array('a') == [expected]
    assert request.get_query_param_array('a', default=['B']) == [expected]
    assert request.get_query_params() == {'a': expected, 'b': 2}
    assert request.get_query_params_array() == query


def test_api_http_request_post():
    method = 'POST'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    # By default there are no query params
    assert request.has_post_param('a') is False
    assert request.get_post_param('a') == ''
    assert request.get_post_param('a', default='B') == 'B'
    assert request.get_post_param_array('a') == []
    assert request.get_post_param_array('a', default=['B']) == ['B']
    assert request.get_post_params() == {}
    assert request.get_post_params_array() == {}

    # Create a request with query params
    expected = 1
    post = MultiDict({'a': expected, 'b': 2})
    request = HttpRequest(method, url, post_data=post)
    assert request.has_post_param('a')
    assert request.get_post_param('a') == expected
    assert request.get_post_param('a', default='B') == expected
    assert request.get_post_param_array('a') == [expected]
    assert request.get_post_param_array('a', default=['B']) == [expected]
    assert request.get_post_params() == {'a': expected, 'b': 2}
    assert request.get_post_params_array() == post


def test_api_http_request_headers():
    method = 'GET'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    # By default there are no headers
    assert request.has_header('X-Type') is False
    assert request.get_header('X-Type') == ''
    assert request.get_headers() == {}

    # Create a request with headers
    expected = 'RESULT'
    expected2 = 'RESULT-2'
    headers = MultiDict([('X-Type', expected), ('X-Type', expected2)])
    request = HttpRequest(method, url, headers=headers)
    assert request.has_header('X-Type')
    assert request.has_header('X-TYPE')
    assert request.get_header('X-Missing') == ''
    assert request.get_header('X-Missing', default='DEFAULT') == 'DEFAULT'
    assert request.get_header('X-Type') == expected  # Gets first item
    assert request.get_header_array('X-Type') == [expected, expected2]
    assert request.get_headers() == {'X-TYPE': expected}
    assert request.get_headers_array() == {'X-TYPE': [expected, expected2]}


def test_api_http_request_body():
    method = 'POST'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    # By default body is empty
    assert request.has_body() is False
    assert request.get_body() == ''

    # Create a request with a body
    expected = 'CONTENT'
    request = HttpRequest(method, url, body=expected)
    assert request.has_body()
    assert request.get_body() == expected


def test_api_http_request_files():
    method = 'POST'
    url = 'http://foo.com/bar/index/'
    request = HttpRequest(method, url)

    # By default there are no files
    assert request.has_file('test') is False
    assert list(request.get_files()) == []

    # When file does not exist return an empty file object
    file = request.get_file('test')
    assert isinstance(file, File)
    assert file.get_name() == 'test'
    assert file.get_path() == ''

    # Create a request with a file
    file = payload_to_file('test', {
        'path': '/files',
        'mime': 'application/json',
        'filename': 'test.json',
        'size': '100',
        })
    request = HttpRequest(method, url, files=MultiDict([('test', file)]))
    assert request.has_file('test')
    assert request.get_file('test') == file
    assert list(request.get_files()) == [file]
