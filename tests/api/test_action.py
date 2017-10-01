import pytest

from katana.api.action import Action
from katana.api.action import NoFileServerError
from katana.api.action import parse_params
from katana.api.action import ReturnTypeError
from katana.api.action import UndefinedReturnValueError
from katana.api.file import File
from katana.api.file import file_to_payload
from katana.api.param import Param
from katana.api.param import TYPE_INTEGER
from katana.api.param import TYPE_STRING
from katana.payload import delete_path
from katana.payload import ErrorPayload
from katana.payload import FIELD_MAPPINGS
from katana.payload import get_path
from katana.payload import Payload
from katana.utils import nomap

# Mapped parameter names for payload
PARAM = {
    'name': FIELD_MAPPINGS['name'],
    'value': FIELD_MAPPINGS['value'],
    'type': FIELD_MAPPINGS['type'],
    }


def test_api_parse_params():
    # Falsy value should return empty
    assert parse_params(None) == []
    assert parse_params([]) == []

    # Params must be a list
    with pytest.raises(TypeError):
        assert parse_params(123)

    # Params must be a list of Param instances
    with pytest.raises(TypeError):
        assert parse_params([123])

    # Check that parameters are converted to payload
    assert parse_params([Param('foo', value=1), Param('bar', value=2)]) == [
        {PARAM['name']: 'foo', PARAM['value']: 1, PARAM['type']: TYPE_INTEGER},
        {PARAM['name']: 'bar', PARAM['value']: 2, PARAM['type']: TYPE_INTEGER},
        ]


def test_api_action(read_json, registry):
    transport = Payload(read_json('transport.json'))
    params = [
        {PARAM['name']: 'foo', PARAM['value']: 1, PARAM['type']: TYPE_INTEGER},
        {PARAM['name']: 'bar', PARAM['value']: 2, PARAM['type']: TYPE_INTEGER},
        ]
    action = Action(**{
        'action': 'test',
        'params': params,
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    assert action.get_action_name() == 'test'

    # Check request origin
    assert not action.is_origin()
    transport.set('meta/origin', ['dummy', '1.0', 'test'])
    assert action.is_origin()

    # Check setting of transport properties
    assert action.set_property('name', 'value') == action
    properties = transport.get('meta/properties', default=None)
    assert isinstance(properties, dict)
    assert properties.get('name') == 'value'

    # Property values must be strings
    with pytest.raises(TypeError):
        action.set_property('other', 1)


def test_api_action_params(read_json, registry):
    transport = Payload(read_json('transport.json'))
    params = [
        {PARAM['name']: 'foo', PARAM['value']: 1, PARAM['type']: TYPE_INTEGER},
        {PARAM['name']: 'bar', PARAM['value']: 2, PARAM['type']: TYPE_INTEGER},
        ]
    action = Action(**{
        'action': 'test',
        'params': params,
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    # Check action parameters
    assert action.has_param('foo')
    assert not action.has_param('missing')
    param = action.get_param('foo')
    assert isinstance(param, Param)
    assert param.exists()
    assert param.get_name() == 'foo'
    assert param.get_value() == 1
    assert param.get_type() == TYPE_INTEGER
    # Get a param that does not exist
    param = action.get_param('missing')
    assert isinstance(param, Param)
    assert not param.exists()
    assert param.get_name() == 'missing'
    assert param.get_value() == ''
    assert param.get_type() == TYPE_STRING

    # Get all parameters
    params = action.get_params()
    assert isinstance(params, list)
    assert len(params) == 2
    for param in params:
        assert param.exists()
        assert param.get_name() in ('foo', 'bar')
        assert param.get_value() in (1, 2)
        assert param.get_type() == TYPE_INTEGER

    # Clear all params and check result
    action._Action__params = {}
    params = action.get_params()
    assert isinstance(params, list)
    assert len(params) == 0

    # Check param creation
    param = action.new_param('foo', value=1, type=TYPE_INTEGER)
    assert isinstance(params, list)
    assert param.exists()
    assert param.get_name() == 'foo'
    assert param.get_value() == 1
    assert param.get_type() == TYPE_INTEGER
    # Check type guessing
    param = action.new_param('foo', value='bar')
    assert isinstance(params, list)
    assert param.get_name() == 'foo'
    assert param.get_value() == 'bar'
    assert param.get_type() == TYPE_STRING
    # Check handling of wrong type
    with pytest.raises(TypeError):
        action.new_param('foo', value='bar', type=TYPE_INTEGER)


def test_api_action_files(read_json, registry):
    transport = Payload(read_json('transport.json'))
    service_name = 'users'
    service_version = '1.0.0'
    action_name = 'create'

    action = Action(**{
        'action': action_name,
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    assert action.has_file('avatar')

    # Get a file that is not available
    assert not action.has_file('missing')
    file = action.get_file('missing')
    assert isinstance(file, File)
    assert file.get_name() == 'missing'
    assert file.get_path() == ''
    assert not file.exists()

    # Get an existing file
    assert action.has_file('document')
    file = action.get_file('document')
    assert isinstance(file, File)
    assert file.get_name() == 'document'
    assert file.get_mime() == 'application/pdf'

    # Get all files
    files = action.get_files()
    assert isinstance(files, list)
    assert len(files) == 2
    for file in files:
        assert file.get_name() in ('avatar', 'document')
        assert file.get_mime() in ('application/pdf', 'image/jpeg')

    # Clear all files and check result
    action._Action__files = {}
    files = action.get_files()
    assert isinstance(files, list)
    assert len(files) == 0

    # Check file creation
    file = action.new_file('foo', path='/tmp/file.ext')
    assert isinstance(file, File)
    assert file.get_name() == 'foo'


def test_api_action_download(read_json, registry):
    service_name = 'dummy'
    service_version = '1.0'
    transport = Payload(read_json('transport.json'))
    action = Action(**{
        'action': 'test',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    # Download accepts only a File instance
    with pytest.raises(TypeError):
        action.set_download('')

    # Create a new file and set is as download
    file = action.new_file('foo', path='/tmp/file.ext')
    transport.set('body', '')
    assert transport.get('body') == ''
    action.set_download(file)
    assert transport.get('body') == file_to_payload(file)

    # Clear download
    transport.set('body', '')
    assert transport.get('body') == ''

    # Check that registry does not have mappings
    assert not registry.has_mappings
    # Set file server mappings to False and try to set a download
    registry.update_registry({
        service_name: {service_version: {'files': False}}
        })
    with pytest.raises(NoFileServerError):
        action.set_download(file)


def test_api_action_data(read_json, registry):
    transport = Payload(read_json('transport.json'))
    address = transport.get('meta/gateway')[1]
    service_name = 'users'
    service_version = '1.0.0'
    action_name = 'create'
    data_path = '|'.join([
        'data',
        address,
        nomap(service_name),
        service_version,
        nomap(action_name),
        ])
    action = Action(**{
        'action': action_name,
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    # Clear transport data
    assert FIELD_MAPPINGS['data'] in transport
    del transport[FIELD_MAPPINGS['data']]
    assert FIELD_MAPPINGS['data'] not in transport
    assert not transport.path_exists(data_path, delimiter='|')

    # Set a transport entity
    entity = {'foo': 'bar'}
    assert action.set_entity(entity) == action
    assert transport.path_exists(data_path, delimiter='|')
    assert transport.get(data_path, delimiter='|') == [entity]
    # Set another entity
    assert action.set_entity(entity) == action
    assert transport.get(data_path, delimiter='|') == [entity, entity]

    # Check that entity can only be a dictionary
    with pytest.raises(TypeError):
        action.set_entity(1)

    # Clear transport data
    assert FIELD_MAPPINGS['data'] in transport
    del transport[FIELD_MAPPINGS['data']]
    assert FIELD_MAPPINGS['data'] not in transport
    assert not transport.path_exists(data_path, delimiter='|')

    # Set a transport collection
    collection = [{'foo': 1}, {'bar': 2}]
    assert action.set_collection(collection) == action
    assert transport.path_exists(data_path, delimiter='|')
    assert transport.get(data_path, delimiter='|') == [collection]
    # Set another collection
    assert action.set_collection(collection) == action
    assert transport.get(data_path, delimiter='|') == [collection, collection]

    # Check that collection can only be list
    with pytest.raises(TypeError):
        action.set_collection(1)

    # Items in a collection can only be dict
    with pytest.raises(TypeError):
        action.set_collection([1])


def test_api_action_relate(read_json, registry):
    transport = Payload(read_json('transport.json'))
    address = transport.get('meta/gateway')[1]
    service_name = 'foo'
    pk = '1'
    rel_path_tpl = '|'.join([
        'relations',
        address,
        nomap(service_name),
        nomap(pk),
        '{}',  # Placeholder for address
        service_name,
        ])
    action = Action(**{
        'action': 'bar',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    # Clear transport relations
    assert FIELD_MAPPINGS['relations'] in transport
    del transport[FIELD_MAPPINGS['relations']]
    assert FIELD_MAPPINGS['relations'] not in transport

    # Format relations path for local relations
    rel_path = rel_path_tpl.format(address)

    # Check relate one
    assert transport.get(rel_path, default='NO', delimiter='|') == 'NO'
    assert action.relate_one(pk, service_name, '321') == action
    assert transport.get(rel_path, delimiter='|') == '321'

    # Clear transport relations
    del transport[FIELD_MAPPINGS['relations']]

    # Check relate many
    fkeys = ['321', '123']
    assert transport.get(rel_path, default='NO', delimiter='|') == 'NO'
    assert action.relate_many(pk, service_name, fkeys) == action
    assert transport.get(rel_path, delimiter='|') == fkeys

    # Check that relate many fails when a list os not given
    with pytest.raises(TypeError):
        action.relate_many(pk, service_name, 1)

    # Clear transport relations
    del transport[FIELD_MAPPINGS['relations']]

    # Format relations path for remote relations
    remote = 'ktp://87.65.43.21:4321'
    rel_path = rel_path_tpl.format(remote)

    # Check relate one remote
    assert transport.get(rel_path, default='NO', delimiter='|') == 'NO'
    assert action.relate_one_remote(pk, remote, service_name, '321') == action
    assert transport.get(rel_path, delimiter='|') == '321'

    # Clear transport relations
    del transport[FIELD_MAPPINGS['relations']]

    # Check relate many
    assert transport.get(rel_path, default='NO', delimiter='|') == 'NO'
    assert action.relate_many_remote(pk, remote, service_name, fkeys) == action
    assert transport.get(rel_path, delimiter='|') == fkeys

    # Check that relate many fails when a list os not given
    with pytest.raises(TypeError):
        action.relate_many_remote(pk, remote, service_name, 1)


def test_api_action_links(read_json, registry):
    transport = Payload(read_json('transport.json'))
    address = transport.get('meta/gateway')[1]
    service_name = 'foo'
    link_name = 'self'
    links_path = '|'.join([
        'links',
        address,
        nomap(service_name),
        nomap(link_name),
        ])
    action = Action(**{
        'action': 'bar',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    # Clear transport links
    assert FIELD_MAPPINGS['links'] in transport
    del transport[FIELD_MAPPINGS['links']]
    assert FIELD_MAPPINGS['links'] not in transport
    assert not transport.path_exists(links_path, delimiter='|')

    # Set a link
    uri = 'http://api.example.com/v1/users/123'
    assert action.set_link(link_name, uri) == action
    assert transport.path_exists(links_path, delimiter='|')
    assert transport.get(links_path, delimiter='|') == uri


def test_api_action_transactions(read_json, registry):
    transport = Payload(read_json('transport.json'))
    service_name = 'foo'
    service_version = '1.0'
    service_action = 'foo'
    params = [Param('dummy', value=123)]
    action = Action(**{
        'action': service_action,
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    # Clear transport transactions
    assert transport.path_exists('transactions')
    del transport[FIELD_MAPPINGS['transactions']]
    assert not transport.path_exists('transactions')

    tr_params = [{
        PARAM['name']: 'dummy',
        PARAM['value']: 123,
        PARAM['type']: TYPE_INTEGER
        }]
    actions = ('action-1', 'action-2')

    cases = {
        'commit': action.commit,
        'rollback': action.rollback,
        'complete': action.complete,
        }

    # Check all transaction types
    for type, register in cases.items():
        # Register 2 transaction actions for current type
        for name in actions:
            assert register(name, params=params) == action

        path = 'transactions/{}'.format(type)
        assert transport.path_exists(path)
        transactions = transport.get(path)
        assert isinstance(transactions, list)
        for tr in transactions:
            assert isinstance(tr, dict)
            assert get_path(tr, 'name', default='NO') == service_name
            assert get_path(tr, 'version', default='NO') == service_version
            assert get_path(tr, 'action', default='NO') in actions
            assert get_path(tr, 'caller', default='NO') == action.get_action_name()
            assert get_path(tr, 'params', default='NO') == tr_params


def test_api_action_return_value(read_json, registry):
    service_name = 'foo'
    service_version = '1.0'
    transport = Payload(read_json('transport.json'))
    return_value = Payload()
    action_args = {
        'action': 'foo',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        'return_value': return_value,
        }

    # By default return value is set when no schema is available
    action = Action(**action_args)
    assert action.set_return(1) == action
    assert return_value.get('return') == 1

    # Check that registry does not have mappings
    assert not registry.has_mappings
    # Add an empty test action to mappings
    mappings = Payload(read_json('schema-service.json'))
    registry.update_registry({service_name: {service_version: mappings}})

    # Set return when mappings contain a return definition for the action
    action = Action(**action_args)
    assert action.set_return(1) == action
    assert action_args['return_value'].get('return') == 1

    # Set an invalid return value type
    with pytest.raises(ReturnTypeError):
        action.set_return('fail')

    # Set a return value when no return definition exists for the action
    assert mappings.path_exists('actions/foo/return')
    delete_path(mappings, 'actions/foo/return')
    assert not mappings.path_exists('actions/foo/return')
    action = Action(**action_args)
    with pytest.raises(UndefinedReturnValueError):
        action.set_return(1)


def test_api_action_defer_call(read_json, registry):
    service_name = 'foo'
    service_version = '1.0'

    # Check that registry does not have mappings
    assert not registry.has_mappings
    # Add an empty test action to mappings
    registry.update_registry({
        service_name: {
            service_version: {
                FIELD_MAPPINGS['files']: True,
                FIELD_MAPPINGS['actions']: {'test': {}},
                },
            },
        })

    transport = Payload(read_json('transport.json'))
    calls_path = 'calls/{}/{}'.format(nomap(service_name), service_version)
    action = Action(**{
        'action': 'test',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    # Clear transport calls
    assert transport.path_exists('calls')
    del transport[FIELD_MAPPINGS['calls']]
    assert not transport.path_exists('calls')

    # Prepare call arguments
    params = [Param('dummy', value=123)]
    c_name = 'foo'
    c_version = '1.1'
    c_action = 'bar'
    c_params = [{
        PARAM['name']: 'dummy',
        PARAM['value']: 123,
        PARAM['type']: TYPE_INTEGER
        }]

    # Make a call
    assert action.defer_call(c_name, c_version, c_action, params=params) == action
    assert transport.path_exists(calls_path)
    calls = transport.get(calls_path)
    assert isinstance(calls, list)
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, dict)
    assert get_path(call, 'name', default='NO') == c_name
    assert get_path(call, 'version', default='NO') == c_version
    assert get_path(call, 'action', default='NO') == c_action
    assert get_path(call, 'caller', default='NO') == action.get_action_name()
    assert get_path(call, 'params', default='NO') == c_params

    # Make a call and add files
    files_path = '|'.join([
        'files',
        transport.get('meta/gateway')[1],
        nomap(c_name),
        c_version,
        nomap(c_action),
        ])
    files = [action.new_file('download', '/tmp/file.ext')]
    assert action.defer_call(c_name, c_version, c_action, files=files) == action
    tr_files = transport.get(files_path, delimiter='|')
    assert isinstance(tr_files, list)
    assert len(tr_files) == 1
    assert tr_files[0] == {
        FIELD_MAPPINGS['name']: 'download',
        FIELD_MAPPINGS['token']: '',
        FIELD_MAPPINGS['filename']: 'file.ext',
        FIELD_MAPPINGS['size']: 0,
        FIELD_MAPPINGS['mime']: 'text/plain',
        FIELD_MAPPINGS['path']: 'file:///tmp/file.ext',
        }

    # Set file server mappings to False and try to call with local files
    registry.update_registry({
        service_name: {
            service_version: {
                FIELD_MAPPINGS['files']: False,
                FIELD_MAPPINGS['actions']: {'test': {}},
                },
            },
        })

    # TODO: Figure out why existing action does not see new mappungs.
    #       Action should read the mapping values from previous statement.
    action = Action(**{
        'action': 'test',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    with pytest.raises(NoFileServerError):
        action.defer_call(c_name, c_version, c_action, files=files)


def test_api_action_call_remote(read_json, registry):
    service_name = 'foo'
    service_version = '1.0'

    # Check that registry does not have mappings
    assert not registry.has_mappings
    # Add an empty test action to mappings
    registry.update_registry({
        service_name: {
            service_version: {
                FIELD_MAPPINGS['files']: True,
                FIELD_MAPPINGS['actions']: {'test': {}},
                },
            },
        })

    transport = Payload(read_json('transport.json'))
    calls_path = 'calls/{}/{}'.format(nomap(service_name), service_version)
    action = Action(**{
        'action': 'test',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    # Clear transport calls
    assert transport.path_exists('calls')
    del transport[FIELD_MAPPINGS['calls']]
    assert not transport.path_exists('calls')

    # Prepare call arguments
    params = [Param('dummy', value=123)]
    c_addr = '87.65.43.21:4321'
    c_name = 'foo'
    c_version = '1.1'
    c_action = 'bar'
    c_params = [{
        PARAM['name']: 'dummy',
        PARAM['value']: 123,
        PARAM['type']: TYPE_INTEGER
        }]

    # Make a remotr call
    kwargs = {
        'address': c_addr,
        'service': c_name,
        'version': c_version,
        'action': c_action,
        'params': params,
        'timeout': 2.0,
        }
    assert action.remote_call(**kwargs) == action
    assert transport.path_exists(calls_path)
    calls = transport.get(calls_path)
    assert isinstance(calls, list)
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, dict)
    assert get_path(call, 'gateway', default='NO') == 'ktp://{}'.format(c_addr)
    assert get_path(call, 'name', default='NO') == c_name
    assert get_path(call, 'version', default='NO') == c_version
    assert get_path(call, 'action', default='NO') == c_action
    assert get_path(call, 'params', default='NO') == c_params

    # Make a call and add files
    files_path = '|'.join([
        'files',
        transport.get('meta/gateway')[1],
        nomap(c_name),
        c_version,
        nomap(c_action),
        ])
    kwargs['files'] = [action.new_file('download', '/tmp/file.ext')]
    assert action.remote_call(**kwargs) == action
    tr_files = transport.get(files_path, delimiter='|')
    assert isinstance(tr_files, list)
    assert len(tr_files) == 1
    assert tr_files[0] == {
        FIELD_MAPPINGS['name']: 'download',
        FIELD_MAPPINGS['token']: '',
        FIELD_MAPPINGS['filename']: 'file.ext',
        FIELD_MAPPINGS['size']: 0,
        FIELD_MAPPINGS['mime']: 'text/plain',
        FIELD_MAPPINGS['path']: 'file:///tmp/file.ext',
        }

    # Set file server mappings to False and try to call with local files
    registry.update_registry({
        service_name: {
            service_version: {
                FIELD_MAPPINGS['files']: False,
                FIELD_MAPPINGS['actions']: {'test': {}},
                },
            },
        })

    # TODO: Figure out why existing action does not see new mappungs.
    #       Action should read the mapping values from previous statement.
    action = Action(**{
        'action': 'test',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': service_version,
        'framework_version': '1.0.0',
        })

    with pytest.raises(NoFileServerError):
        action.remote_call(**kwargs)


def test_api_action_errors(read_json, registry):
    transport = Payload(read_json('transport.json'))
    address = transport.get('meta/gateway')[1]
    service_name = 'foo'
    service_version = '1.0'
    errors_path = '|'.join([
        'errors',
        address,
        nomap(service_name),
        service_version,
        ])
    action = Action(**{
        'action': 'bar',
        'params': [],
        'transport': transport,
        'component': None,
        'path': '/path/to/file.py',
        'name': service_name,
        'version': '1.0',
        'framework_version': '1.0.0',
        })

    # Clear transport errors
    assert FIELD_MAPPINGS['errors'] in transport
    del transport[FIELD_MAPPINGS['errors']]
    assert FIELD_MAPPINGS['errors'] not in transport
    assert not transport.path_exists(errors_path, delimiter='|')

    # Set an error
    msg = 'Error message'
    code = 99
    status = '500 Internal Server Error'
    assert action.error(msg, code=code, status=status) == action
    assert transport.path_exists(errors_path, delimiter='|')
    errors = transport.get(errors_path, delimiter='|')
    assert isinstance(errors, list)
    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, ErrorPayload)
    assert error.get('message') == msg
    assert error.get('code') == code
    assert error.get('status') == status

    # Add a second error
    assert action.error(msg, code=code, status=status) == action
    errors = transport.get(errors_path, delimiter='|')
    assert isinstance(errors, list)
    assert len(errors) == 2
    for error in errors:
        assert isinstance(error, ErrorPayload)
