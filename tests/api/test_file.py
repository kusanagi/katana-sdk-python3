import os

import pytest

from katana.api.file import File
from katana.api.file import file_to_payload
from katana.api.file import payload_to_file
from katana.payload import FIELD_MAPPINGS


def test_api_file_to_payload():
    empty = object()
    values = {
        'path': 'http://127.0.0.1:8080/ANBDKAD23142421',
        'mime': 'application/json',
        'filename': 'file.json',
        'size': '600',
        'token': 'secret',
        }
    payload = file_to_payload(File('foo', **values))
    assert payload is not None

    # Check that payload contains file values
    for name, value in values.items():
        assert payload.get(name, default=empty) == value


def test_api_payload_to_file():
    values = {
        'name': 'foo',
        'path': 'http://127.0.0.1:8080/ANBDKAD23142421',
        'mime': 'application/json',
        'filename': 'file.json',
        'size': '600',
        'token': 'secret',
        }
    payload = {FIELD_MAPPINGS[name]: value for name, value in values.items()}

    file = payload_to_file(payload)
    assert file is not None
    assert file.get_name() == 'foo'

    # Check that file contains payload values
    for name, value in values.items():
        getter = getattr(file, 'get_{}'.format(name), None)
        assert getter is not None
        assert getter() == value


def test_api_file(data_path, mocker):
    # Empty name is invalid
    with pytest.raises(TypeError):
        File('  ', 'file:///tmp/foo.json')

    # HTTP file path with no token is invalid
    with pytest.raises(TypeError):
        File('foo', 'http://127.0.0.1:8080/ANBDKAD23142421')

    # Patch HTTP connection object and make al request "200 OK"
    response = mocker.MagicMock(status=200, reason='OK')
    connection = mocker.MagicMock()
    connection.getresponse.return_value = response
    mocker.patch('http.client.HTTPConnection', return_value=connection)

    # ... with token should work
    try:
        file = File('foo', 'http://127.0.0.1:8080/ANBDKAD23142421', token='xx')
    except:
        pytest.fail('Creation of HTTP file with token failed')
    else:
        assert file.exists()

    # Check HTTP file missing
    response.status = 404
    response.reason = 'Not found'
    assert not file.exists()

    # Check result when connection to remote HTTP file server fails
    connection.request.side_effect = Exception
    assert not file.exists()

    # Check remote file read
    request = mocker.MagicMock()
    request.read.return_value = b'CONTENT'
    reader = mocker.MagicMock()
    reader.__enter__.return_value = request
    reader.__exit__.return_value = False
    mocker.patch('urllib.request.urlopen', return_value=reader)
    assert file.read() == b'CONTENT'

    # Check error during remote file read
    request.read.side_effect = Exception
    assert file.read() == b''

    # A file with empty path should not exist
    file = File('foo', '')
    assert not file.exists()

    # Check creation of a local file
    local_file = os.path.join(data_path, 'foo.json')
    file = File('foo', local_file)
    assert file.get_name() == 'foo'
    assert file.is_local()
    assert file.exists()
    # Check extracted file values
    assert file.get_mime() == 'application/json'
    assert file.get_filename() == 'foo.json'
    assert file.get_size() == 54

    # Read file contents
    with open(local_file, 'rb') as test_file:
        assert file.read() == test_file.read()

    # Read should return empty when file path is not a file
    mocker.patch('os.path.isfile', return_value=False)
    assert file.read() == b''

    # Try to read a file that does not exist
    mocker.patch('os.path.isfile', return_value=True)
    file = File('foo', 'does-not-exist')
    assert file.read() == b''

    # Check file creation where size can't be getted
    mocker.patch('os.path.getsize', side_effect=OSError)
    file = File('foo', local_file)
    assert file.get_size() == 0


def test_api_file_copy(data_path):
    file = File('foo', os.path.join(data_path, 'foo.json'))

    # Check generic file copy
    clon = file.copy()
    assert isinstance(clon, File)
    assert clon != file
    assert clon.get_name() == file.get_name()
    assert clon.get_path() == file.get_path()
    assert clon.get_size() == file.get_size()
    assert clon.get_mime() == file.get_mime()

    # Check copy with methods
    clon = file.copy_with_name('clon')
    assert isinstance(clon, File)
    assert clon != file
    assert clon.get_name() == 'clon'
    assert clon.get_name() != file.get_name()
    assert clon.get_path() == file.get_path()
    assert clon.get_size() == file.get_size()
    assert clon.get_mime() == file.get_mime()

    clon = file.copy_with_mime('text/plain')
    assert isinstance(clon, File)
    assert clon != file
    assert clon.get_mime() == 'text/plain'
    assert clon.get_mime() != file.get_mime()
    assert clon.get_name() == file.get_name()
    assert clon.get_path() == file.get_path()
    assert clon.get_size() == file.get_size()
