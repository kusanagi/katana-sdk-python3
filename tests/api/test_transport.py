import pytest

from katana.api.file import File
from katana.api.transport import Transport
from katana.payload import delete_path
from katana.payload import get_path


def test_api_transport(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    assert transport.get_request_id() == 'f1b27da9-240b-40e3-99dd-a567e4498ed7'
    assert transport.get_request_timestamp() == '2016-04-12T02:49:05.761'
    assert transport.get_origin_service() == ['users', '1.0.0', 'list']

    # Default value must be a string
    with pytest.raises(TypeError):
        transport.get_property('missing', default=False)

    # Use default because property does not exist
    assert transport.get_property('missing', default='OK') == 'OK'
    # Get an existing property
    assert transport.get_property('foo') == 'bar'
    # Get all properties
    assert transport.get_properties() == {'foo': 'bar'}
    # Try to get all propertes when there is none
    assert delete_path(payload, 'meta/properties')
    assert transport.get_properties() == {}

    # Check download
    assert transport.has_download()
    file = transport.get_download()
    assert isinstance(file, File)
    assert file.get_name() == 'download'
    assert file.get_path() == 'file:///tmp/document.pdf'
    assert file.get_filename() == 'document.pdf'
    assert file.get_size() == 1234567890
    assert file.get_mime() == 'application/pdf'

    # Remove download from body
    assert delete_path(payload, 'body')
    assert not transport.has_download()
    assert transport.get_download() is None

    # Get data that exists in transport
    data = transport.get_data(
        address='http://127.0.0.1:80',
        service='users',
        version='1.0.0',
        )
    assert isinstance(data, dict)
    assert 'read_users' in data
    assert data['read_users'] == [
        {'name': 'Foo', 'id': 1},
        {'name': 'Mandela', 'id': 2}
        ]
    # Remove data
    assert delete_path(payload, 'data')
    assert transport.get_data() == {}

    # Get relations that exists in transport
    relations = transport.get_relations(address='http://127.0.0.1:80')
    assert isinstance(relations, dict)
    assert 'users' in relations
    assert relations['users'] == {
        '123': {
            'http://127.0.0.1:80': {
                'posts': ['1', '2'],
                },
            },
        }
    # Remove relations
    assert delete_path(payload, 'relations')
    assert transport.get_relations() == {}

    # Get links that exists in transport
    links = transport.get_links(address='http://127.0.0.1:80')
    assert 'users' in links
    assert links['users'] == {
        'self': 'http://api.example.com/v1/users/123',
        }
    # Remove links
    assert delete_path(payload, 'links')
    assert transport.get_links() == {}

    # Get local calls
    local_calls = transport.get_calls(service='users')
    assert isinstance(local_calls, dict)
    assert 'users' in local_calls
    assert '1.0.0' in local_calls['users']
    assert isinstance(local_calls['users']['1.0.0'], list)
    # There should be a local and remote call
    assert len(local_calls['users']['1.0.0']) == 2

    # Get remote calls
    remote_calls = transport.get_calls(
        address='ktp://87.65.43.21:4321',
        service='users',
        )
    assert isinstance(remote_calls, dict)
    assert 'users' in remote_calls
    assert '1.0.0' in remote_calls['users']
    assert isinstance(remote_calls['users']['1.0.0'], list)
    # There should be only the remote call
    assert len(remote_calls['users']['1.0.0']) == 1

    # Remove all calls
    assert delete_path(payload, 'calls')
    assert transport.get_calls() == {}
    assert transport.get_calls(address='ktp://87.65.43.21:4321') == {}
    assert transport.get_calls(service='users') == {}

    # Get transactions
    transactions = transport.get_transactions()
    assert isinstance(transactions, dict)
    assert len(transactions) == 3

    # Get transactions for a service
    transactions = transport.get_transactions(service='foo')
    assert isinstance(transactions, dict)
    assert len(transactions) == 1

    # Remove transactions
    assert delete_path(payload, 'transactions')
    assert transport.get_transactions() == {}

    # Get errors
    errors = transport.get_errors(address='http://127.0.0.1:80')
    assert isinstance(errors, dict)
    assert 'users' in errors
    assert '1.0.0' in errors['users']
    assert isinstance(errors['users']['1.0.0'], list)
    # There should be only one error
    assert len(errors['users']['1.0.0']) == 1
    error = errors['users']['1.0.0'][0]
    assert isinstance(error, dict)
    assert get_path(error, 'message') == 'The user does not exist'
    assert get_path(error, 'code') == 9
    assert get_path(error, 'status') == '404 Not Found'

    # Remove errors
    assert delete_path(payload, 'errors')
    assert transport.get_errors() == {}
