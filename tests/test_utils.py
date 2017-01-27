from datetime import datetime

import pytest

from katana import utils


def test_uuid_generation():
    uuid = utils.uuid()
    assert isinstance(uuid, str)
    assert len(uuid) == 36
    assert len(uuid.split('-')) == 5


def test_tcp_channel_string_generation():
    expected = 'tcp://10.1.1.2:8888'
    assert utils.tcp('10.1.1.2', '8888') == expected
    assert utils.tcp('10.1.1.2:8888') == expected


def test_ipc_channel_string_generation():
    expected = 'ipc://@katana-test-service-name'

    # Check that arguments are joined properly with a '-'
    assert utils.ipc('test', 'service', 'name') == expected
    assert utils.ipc('test-service', 'name') == expected
    assert utils.ipc('test-service-name') == expected

    # Check that invalid characters are replaced by '-'
    assert utils.ipc('test-@service-#name') == expected
    assert utils.ipc('test.service_name') == expected


def test_guess_channel():
    guess_channel = utils.guess_channel

    # For localhost IP/name use IPC
    for host in utils.LOCALHOSTS:
        remote = '{}:8080'.format(host)
        # Local address does not matter in this case
        assert guess_channel(None, remote) == utils.ipc(remote)

    local = '10.1.1.2:7070'

    # Use IPC for local addresses
    remote = '{}:8080'.format(local.split(':')[0])
    assert guess_channel(local, remote) == utils.ipc(remote)

    # Use TCP for non local addresses
    remote = '10.2.1.10:8080'
    assert guess_channel(local, remote) == utils.tcp(remote)


def test_guess_channel_to_remote(mocker):
    guess_channel_to_remote = utils.guess_channel_to_remote

    # For localhost IP/name use IPC
    for remote in utils.LOCALHOSTS:
        assert guess_channel_to_remote(remote) == utils.ipc(remote)

    mocker.patch(
        'socket.gethostbyname_ex',
        return_value=(None, None, ['10.1.1.2', '20.2.2.2']),
        )

    # Use IPC for local addresses
    remote = '10.1.1.2:8080'
    assert guess_channel_to_remote(remote) == utils.ipc(remote)

    # Use TCP for non local addresses
    remote = '10.2.1.10:8080'
    assert guess_channel_to_remote(remote) == utils.tcp(remote)


def test_str_to_date():
    # When a falsy value is sent it returns None
    assert utils.str_to_date('') is None
    assert utils.str_to_date(None) is None

    date = datetime(2017, 1, 27, 20, 12, 8, 952811)
    assert utils.str_to_date('2017-01-27T20:12:08.952811+00:00') == date


def test_date_to_str():
    # When a falsy value is sent it returns None
    assert utils.date_to_str('') is None
    assert utils.date_to_str(None) is None

    date = datetime(2017, 1, 27, 20, 12, 8, 952811)
    assert utils.date_to_str(date) == '2017-01-27T20:12:08.952811+00:00'


def test_nomap():
    assert utils.nomap('foo').startswith('!')


def test_get_path():
    get_path = utils.get_path

    # Create a simple value for defaults
    default = object()

    # Check path resolution without mappings
    assert get_path({}, 'foo/bar', default) == default
    assert get_path({}, 'foo|bar', default, delimiter='|') == default
    # No default raises exception
    with pytest.raises(KeyError):
        get_path({}, 'foo/bar')

    expected = 'RESULT'
    # Item to be used for path resolution
    item = {'foo': {'bar': expected}}

    assert get_path(item, 'foo') == item['foo']
    assert get_path(item, 'foo/bar') == expected
    assert get_path(item, 'foo|bar', delimiter='|') == expected
    # No default raises exception
    with pytest.raises(KeyError):
        get_path(item, 'invalid/path')

    # Field mappings
    mp = {'foo': 'f', 'bar': 'b'}
    # Item to be used for path resolution
    item = {'f': {'b': expected}}

    # Check path resolution with mappings
    assert get_path(item, 'foo', mappings=mp) == item['f']
    assert get_path(item, 'foo/bar', mappings=mp) == expected
    assert get_path(item, 'f', mappings=mp) == item['f']
    assert get_path(item, 'f/b', mappings=mp) == expected
    assert get_path(item, 'foo|bar', mappings=mp, delimiter='|') == expected
    assert get_path(item, 'f|b', mappings=mp, delimiter='|') == expected


def test_set_path():
    set_path = utils.set_path

    # Create a simple value for defaults
    default = object()

    # Try a simple path value
    item = {}
    assert utils.get_path(item, 'foo', default=default) == default
    set_path(item, 'foo', 1)
    assert utils.get_path(item, 'foo', default=default) == 1

    # Try a path value without delimiter
    item = {}
    assert utils.get_path(item, 'foo/bar', default=default) == default
    set_path(item, 'foo/bar', 1)
    assert utils.get_path(item, 'foo/bar', default=default) == 1

    # Try a path value with delimiter
    item = {}
    assert utils.get_path(item, 'foo|bar', default=default) == default
    set_path(item, 'foo|bar', 1, delimiter='|')
    assert utils.get_path(item, 'foo|bar', default=default, delimiter='|') == 1

    # Field mappings
    mp = {'foo': 'f', 'bar': 'b'}

    # Check set path using field name mappings
    item = {}
    set_path(item, 'foo/bar', 1, mappings=mp)
    assert item == {'f': {'b': 1}}

    # Check using nomap to avoid short name for 'bar'
    item = {}
    path = 'foo/{}'.format(utils.nomap('bar'))
    set_path(item, path, 1, mappings=mp)
    assert item == {'f': {'bar': 1}}
