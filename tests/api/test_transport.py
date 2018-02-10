import pytest

from katana.api.file import File
from katana.api.param import Param
from katana.api.transport import TransactionTypeError
from katana.api.transport import Transport
from katana.payload import delete_path


def test_api_transport(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    assert transport.get_request_id() == 'f1b27da9-240b-40e3-99dd-a567e4498ed7'
    assert transport.get_request_timestamp() == '2016-04-12T02:49:05.761'
    assert transport.get_origin_service() == ('users', '1.0.0', 'list')

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


def test_api_transport_data(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    # Get data that exists in transport
    data = transport.get_data()
    assert isinstance(data, list)
    assert len(data) == 2
    data.sort(key=lambda d: d.get_name())

    svc_data = data[0]
    assert svc_data.get_address() == 'http://127.0.0.1:80'
    assert svc_data.get_name() == 'employees'
    assert svc_data.get_version() == '1.1.0'
    svc_data = data[1]
    assert svc_data.get_address() == 'http://127.0.0.1:80'
    assert svc_data.get_name() == 'users'
    assert svc_data.get_version() == '1.0.0'

    actions = svc_data.get_actions()
    assert isinstance(actions, list)
    assert len(data) == 2
    actions.sort(key=lambda a: a.get_name())

    action = actions[0]
    assert action.get_name() == 'list_users'
    assert action.is_collection()
    action_data = action.get_data()
    assert isinstance(action_data, list)
    assert len(action_data) == 1
    assert action_data[0] == [
        {'name': "Foo", 'id': 1},
        {'name': "Mandela", 'id': 2},
        ]
    action = actions[1]
    assert action.get_name() == 'read_users'
    assert not action.is_collection()
    action_data = action.get_data()
    assert isinstance(action_data, list)
    assert len(action_data) == 2
    assert action_data[0] == {'name': "Foo", 'id': 1}
    assert action_data[1] == {'name': "Mandela", 'id': 2}

    # Remove data
    assert delete_path(payload, 'data')
    assert transport.get_data() == []


def test_api_transport_relations(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    # Get relations that exists in transport
    relations = transport.get_relations()
    assert isinstance(relations, list)
    assert len(relations) == 3
    relations.sort(key=lambda r: r.get_name() + r.get_primary_key())

    relation = relations[0]
    assert relation.get_address() == 'http://127.0.0.1:80'
    assert relation.get_name() == 'posts'
    assert relation.get_primary_key() == '1'
    fks = relation.get_foreign_relations()
    assert isinstance(fks, list)
    assert len(fks) == 2
    relation = relations[2]
    assert relation.get_address() == 'http://127.0.0.1:80'
    assert relation.get_name() == 'users'
    assert relation.get_primary_key() == '123'
    fks = relation.get_foreign_relations()
    assert isinstance(fks, list)
    assert len(fks) == 1
    fk = fks[0]
    assert fk.get_address() == 'http://127.0.0.1:80'
    assert fk.get_name() == 'posts'
    assert fk.get_foreign_keys() == ['1', '2']

    # Remove relations
    assert delete_path(payload, 'relations')
    assert transport.get_relations() == []


def test_api_transport_links(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    # Get links that exists in transport
    links = transport.get_links()
    assert isinstance(links, list)
    assert len(links) == 1
    link = links[0]
    assert link.get_address() == 'http://127.0.0.1:80'
    assert link.get_name() == 'users'
    assert link.get_link() == 'self'
    assert link.get_uri() == 'http://api.example.com/v1/users/123'

    # Remove links
    assert delete_path(payload, 'links')
    assert transport.get_links() == []


def test_api_transport_calls(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    calls = transport.get_calls()
    assert isinstance(calls, list)
    assert len(calls) == 3
    calls.sort(key=lambda c: c.get_name() + c.get_action())

    call = calls[0]
    assert call.get_name() == 'foo'
    assert call.get_version() == '1.0.0'
    assert call.get_action() == 'read'
    callee = call.get_callee()
    assert callee.get_duration() == 1120
    assert callee.get_name() == 'bar'
    assert callee.get_version() == '1.0.0'
    assert callee.get_action() == 'list'
    assert callee.get_address() == ''
    assert not callee.is_remote()
    assert callee.get_params() == []
    call = calls[2]
    assert call.get_name() == 'users'
    assert call.get_version() == '1.0.0'
    assert call.get_action() == 'update'
    callee = call.get_callee()
    assert callee.get_duration() == 1200
    assert callee.get_name() == 'comments'
    assert callee.get_version() == '1.1.0'
    assert callee.get_action() == 'list'
    assert callee.get_address() == 'ktp://87.65.43.21:4321'
    assert callee.is_remote()
    params = callee.get_params()
    assert isinstance(params, list)
    assert len(params) == 1
    assert isinstance(params[0], Param)

    # Remove all calls
    assert delete_path(payload, 'calls')
    assert transport.get_calls() == []


def test_api_transport_transactions(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    # Check that an exception is raised for invalid transation types
    with pytest.raises(TransactionTypeError):
        transport.get_transactions('foo')

    transactions = transport.get_transactions('commit')
    assert isinstance(transactions, list)
    assert len(transactions) == 1
    transactions = transport.get_transactions('rollback')
    assert isinstance(transactions, list)
    assert len(transactions) == 1
    transactions = transport.get_transactions('complete')
    assert isinstance(transactions, list)
    assert len(transactions) == 2
    transactions.sort(key=lambda t: t.get_name())

    tr = transactions[0]
    assert tr.get_type() == 'complete'
    assert tr.get_name() == 'foo'
    assert tr.get_version() == '1.0.0'
    assert tr.get_callee_action() == 'bar'
    assert tr.get_caller_action() == 'cleanup'
    assert tr.get_params() == []
    tr = transactions[1]
    assert tr.get_type() == 'complete'
    assert tr.get_name() == 'users'
    assert tr.get_version() == '1.0.0'
    assert tr.get_callee_action() == 'create'
    assert tr.get_caller_action() == 'cleanup'
    params = tr.get_params()
    assert isinstance(params, list)
    assert len(params) == 1
    assert isinstance(params[0], Param)

    # Remove transactions
    assert delete_path(payload, 'transactions')
    assert transport.get_transactions('commit') == []


def test_api_transport_errors(read_json):
    transport = Transport(read_json('transport.json'))
    payload = transport._Transport__transport

    errors = transport.get_errors()
    assert isinstance(errors, list)
    assert len(errors) == 1
    error = errors[0]
    assert error.get_address() == 'http://127.0.0.1:80'
    assert error.get_name() == 'users'
    assert error.get_version() == '1.0.0'
    assert error.get_message() == 'The user does not exist'
    assert error.get_code() == 9
    assert error.get_status() == '404 Not Found'

    # Remove errors
    assert delete_path(payload, 'errors')
    assert transport.get_errors() == []
