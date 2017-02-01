import os

import pytest

from katana.api.file import File
from katana.api.file import file_to_payload
from katana.api.file import payload_to_file
from katana.payload import FIELD_MAPPINGS


def test_file_to_payload():
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


def test_payload_to_file():
    values = {
        'path': 'http://127.0.0.1:8080/ANBDKAD23142421',
        'mime': 'application/json',
        'filename': 'file.json',
        'size': '600',
        'token': 'secret',
        }
    payload = {FIELD_MAPPINGS[name]: value for name, value in values.items()}

    file = payload_to_file('foo', payload)
    assert file is not None
    assert file.get_name() == 'foo'

    # Check that file contains payload values
    for name, value in values.items():
        getter = getattr(file, 'get_{}'.format(name), None)
        assert getter is not None
        assert getter() == value


def test_file(data_path):
    # Empty name is invalid
    with pytest.raises(TypeError):
        File('  ', 'file:///tmp/foo.json')

    # HTTP file path with no token is invalid
    with pytest.raises(TypeError):
        File('foo', 'http://127.0.0.1:8080/ANBDKAD23142421')

    # ... with token should work
    try:
        file = File('foo', 'http://127.0.0.1:8080/ANBDKAD23142421', token='xx')
    except:
        pytest.fail('Creation of HTTP file with token failed')
    else:
        # ... but file does not exist
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


def test_file_copy(data_path):
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
