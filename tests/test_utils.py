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


def test_get_path_with_mappings():
    get_path = utils.get_path

    expected = 'RESULT'

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


def test_set_path_with_mappings():
    set_path = utils.set_path

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


def test_delete_path():
    delete_path = utils.delete_path

    # When path does not esists function returns false
    assert delete_path({}, 'foo/bar') is False

    item = {'foo': {'bar': 1}}
    assert delete_path(item, 'foo/bar')
    assert item == {}

    item = {'foo': {'bar': 1, 'keep': 2}}
    assert delete_path(item, 'foo/bar')
    assert item == {'foo': {'keep': 2}}

    item = {'foo': {'bar': 1}}
    assert delete_path(item, 'foo|bar', delimiter='|')
    assert item == {}

    item = {'foo': {'bar': 1, 'keep': 2}}
    assert delete_path(item, 'foo|bar', delimiter='|')
    assert item == {'foo': {'keep': 2}}


def test_delete_path_with_mappings():
    delete_path = utils.delete_path

    # Field mappings
    mp = {'foo': 'f', 'bar': 'b'}

    item = {'f': {'b': 1}}
    assert delete_path(item, 'foo/bar', mappings=mp)
    assert item == {}

    item = {'f': {'b': 1, 'keep': 2}}
    assert delete_path(item, 'foo/bar', mappings=mp)
    assert item == {'f': {'keep': 2}}

    item = {'f': {'b': 1}}
    assert delete_path(item, 'foo|bar', mappings=mp, delimiter='|')
    assert item == {}

    item = {'f': {'b': 1, 'keep': 2}}
    assert delete_path(item, 'foo|bar', mappings=mp, delimiter='|')
    assert item == {'f': {'keep': 2}}

    # Check removal with a key that is not mapped
    path = 'foo/{}'.format(utils.nomap('bar'))

    item = {'f': {'bar': 1}}
    assert delete_path(item, path, mappings=mp)
    assert item == {}

    # Delete fails here because 'bar' does not exist as key
    item = {'f': {'b': 1}}
    assert delete_path(item, path, mappings=mp) is False
    assert item == {'f': {'b': 1}}


def test_merge():
    merge = utils.merge

    item1 = {'a': {'b': [1, 2], 'd': False}, 'x': [0]}
    item2 = {'a': {'b': [3, 4], 'd': True}, 'x': [1]}

    # Merge but don't extend "leaf" values that are lists
    assert merge(item2, item1) == {
        'a': {
            'b': [1, 2],  # List is not extended/merged
            'd': False,  # Existing items are not overwriten
            },
        'x': [0],  # List is not extended/merged
        }

    # Merge but don't extend "leaf" values that are lists
    item1 = {'a': {'b': [1, 2]}, 'x': [0]}
    assert merge(item2, item1, lists=True) == {
        'a': {
            'b': [1, 2, 3, 4],  # List contains elements from both items
            'd': True,
            },
        'x': [0, 1],  # List contains elements from both items
        }


def test_merge_with_mappings():
    merge = utils.merge

    # Field mappings
    mp = {'AA': 'a', 'BB': 'b', 'DD': 'd', 'XX': 'x'}

    # After merging values will be short names
    item1 = {'a': {'b': [1, 2], 'd': False}, 'x': [0]}
    item2 = {'AA': {'BB': [3, 4], 'DD': True}, 'XX': [1]}

    # Merge but don't extend "leaf" values that are lists
    assert merge(item2, item1, mappings=mp) == {
        'a': {
            'b': [1, 2],
            'd': False,
            },
        'x': [0],
        }

    # Merge but don't extend "leaf" values that are lists
    item1 = {'a': {'b': [1, 2]}, 'x': [0]}
    assert merge(item2, item1, mappings=mp, lists=True) == {
        'a': {
            'b': [1, 2, 3, 4],
            'd': True,
            },
        'x': [0, 1],
        }


def test_lookup_dict():
    LookupDict = utils.LookupDict

    # Check that a value is THE empty value
    assert LookupDict.is_empty(utils.EMPTY)

    # An empty string is NOT the empty value
    assert LookupDict.is_empty('') is False

    expected = 'RESULT'
    expected2 = 'RESULT-2'

    # Define values to create lookup dictionaries
    values = {'foo': {'bar': expected, 'other': expected2}}

    lookup = LookupDict(values)

    # Check different paths
    assert lookup.path_exists('foo/bar')
    assert lookup.path_exists('foo/missing') is False
    assert lookup.path_exists('foo|bar', delimiter='|')
    assert lookup.path_exists('foo|missing', delimiter='|') is False

    # Get a path that does not exists without a default
    with pytest.raises(KeyError):
        lookup.get('foo/missing')

    # Now try with a default setted
    assert lookup.path_exists('foo/missing') is False
    lookup.set_defaults({'foo/missing': 1})
    assert lookup.path_exists('foo/missing')
    assert lookup.get('foo/missing') == 1

    # Get a single value
    assert lookup.get('foo/missing', 'DEFAULT') == 'DEFAULT'
    assert lookup.get('foo/bar') == expected
    assert lookup.get('foo|bar', delimiter='|') == expected

    # Get multiple values
    multi = [expected, expected2]
    assert lookup.get_many('foo/bar', 'foo/other') == multi
    assert lookup.get_many('foo|bar', 'foo|other', delimiter='|') == multi
    # When there is a missing path fail
    with pytest.raises(KeyError):
        lookup.get_many('foo/bar', 'other/missing')

    # Set some new value
    assert lookup.path_exists('new/path') is False
    lookup.set('new/path', 'value')
    assert lookup.path_exists('new/path')
    assert lookup.get('new/path', None) == 'value'

    # Set multiple new values
    assert lookup.path_exists('multi/path') is False
    assert lookup.path_exists('multi/path2') is False
    lookup.set_many({
        'multi/path': 1,
        'multi/path2': 2,
        })
    assert lookup.path_exists('multi/path')
    assert lookup.path_exists('multi/path2')
    assert lookup.get_many('multi/path', 'multi/path2') == [1, 2]

    # Create a new lookup
    lookup = LookupDict({})

    # Push a value to a non existing path
    assert lookup.path_exists('multi/path') is False
    lookup.push('multi/path', 1)
    assert lookup.path_exists('multi/path')
    assert lookup.get('multi/path') == [1]

    # Push another item to an existing path
    lookup.push('multi/path', 2)
    assert lookup.path_exists('multi/path')
    assert lookup.get('multi/path') == [1, 2]
    # .. also push using a delimiter
    lookup.push('multi|path', 3, delimiter='|')
    assert lookup.get('multi|path', delimiter='|') == [1, 2, 3]

    # Is not possible to push to an existing value that is not a list
    lookup.set('new/path', 1)
    with pytest.raises(TypeError):
        lookup.push('new/path', 2)


def test_lookup_dict_with_mappings():
    LookupDict = utils.LookupDict

    expected = 'RESULT'
    expected2 = 'RESULT-2'

    # Define values to create lookup dictionaries
    values = {'f': {'b': expected, 'o': expected2}}

    lookup = LookupDict(values)
    # Use mappings
    lookup.set_mappings({
        'bar': 'b',
        'foo': 'f',
        'muli': 'm',
        'new': 'n',
        'other': 'o',
        'path': 'p',
        'path2': 'P',
        })

    # Check different paths
    assert lookup.path_exists('foo/bar')
    assert lookup.path_exists('foo/missing') is False
    assert lookup.path_exists('foo|bar', delimiter='|')
    assert lookup.path_exists('foo|missing', delimiter='|') is False

    # Get a path that does not exists without a default
    with pytest.raises(KeyError):
        lookup.get('foo/missing')

    # Get a single value
    assert lookup.get('foo/missing', 'DEFAULT') == 'DEFAULT'
    assert lookup.get('foo/bar') == expected
    assert lookup.get('foo|bar', delimiter='|') == expected

    # Get multiple values
    multi = [expected, expected2]
    assert lookup.get_many('foo/bar', 'foo/other') == multi
    assert lookup.get_many('foo|bar', 'foo|other', delimiter='|') == multi
    # When there is a missing path fail
    with pytest.raises(KeyError):
        lookup.get_many('foo/bar', 'foo/missing')

    # Set some new value
    assert lookup.path_exists('new/path') is False
    lookup.set('new/path', 'value')
    assert lookup.path_exists('new/path')
    assert lookup.get('new/path', None) == 'value'

    # Set multiple new values
    assert lookup.path_exists('multi/path') is False
    assert lookup.path_exists('multi/path2') is False
    lookup.set_many({
        'multi/path': 1,
        'multi/path2': 2,
        })
    assert lookup.path_exists('multi/path')
    assert lookup.path_exists('multi/path2')
    assert lookup.get_many('multi/path', 'multi/path2') == [1, 2]

    # Create a new lookup
    lookup = LookupDict({})

    # Push a value to a non existing path
    assert lookup.path_exists('multi/path') is False
    lookup.push('multi/path', 1)
    assert lookup.path_exists('multi/path')
    assert lookup.get('multi/path') == [1]

    # Push another item to an existing path
    lookup.push('multi/path', 2)
    assert lookup.path_exists('multi/path')
    assert lookup.get('multi/path') == [1, 2]
    # .. also push using a delimiter
    lookup.push('multi|path', 3, delimiter='|')
    assert lookup.get('multi|path', delimiter='|') == [1, 2, 3]

    # Is not possible to push to an existing value that is not a list
    lookup.set('new/path', 1)
    with pytest.raises(TypeError):
        lookup.push('new/path', 2)


def test_lookup_dict_merge():
    LookupDict = utils.LookupDict

    lookup = LookupDict()
    lookup.set('foo/bar', {'a': {'b': [1, 2], 'd': False}, 'x': [0]})

    # Merge values into the lookup dictionary
    values = {'a': {'b': [3, 4], 'd': True}, 'x': [1]}
    assert lookup.merge('foo/bar', values) == lookup
    assert lookup.path_exists('foo/bar')
    assert lookup.get('foo/bar') == {
        'a': {
            'b': [1, 2, 3, 4],  # List contains elements from both items
            'd': False,  # Existing items are not overwriten
            },
        'x': [0, 1],  # List contains elements from both items
        }

    # When item in path is not a dictionary don't merge
    lookup.set('foo/other', 1)
    with pytest.raises(TypeError):
        lookup.merge('foo/other', {})


def test_lookup_dict_merge_with_mappings():
    LookupDict = utils.LookupDict

    lookup = LookupDict()
    lookup.set_mappings({
        'AA': 'a',
        'BB': 'b',
        'bar': 'B',
        'DD': 'd',
        'foo': 'f',
        'XX': 'x',
        'other': 'o',
        })
    lookup.set('foo/bar', {'a': {'b': [1, 2], 'd': False}, 'x': [0]})

    # Merge values into the lookup dictionary
    values = {'AA': {'BB': [3, 4], 'DD': True}, 'XX': [1]}
    assert lookup.merge('foo/bar', values) == lookup
    assert lookup.path_exists('foo/bar')
    assert lookup.get('foo/bar') == {
        'a': {
            'b': [1, 2, 3, 4],  # List contains elements from both items
            'd': False,  # Existing items are not overwriten
            },
        'x': [0, 1],  # List contains elements from both items
        }

    # When item in path is not a dictionary don't merge
    lookup.set('foo/other', 1)
    with pytest.raises(TypeError):
        lookup.merge('foo/other', {})


def test_multi_dict():
    multi = utils.MultiDict()
    assert multi == {}

    # Get a non existing item without and with default
    assert multi.getone('missing') is None
    assert multi.getone('missing', 'DEFAULT') == 'DEFAULT'

    # When setting a new item it is saved as a list
    multi['item'] = 1
    assert isinstance(multi['item'], list)
    assert multi['item'] == [1]
    assert multi.getone('item') == 1

    # Set a value for an existing key
    multi['item'] = 2
    assert multi['item'] == [1, 2]
    assert multi.getone('item') == 1  # This gets the first item in list

    # Get all items splitted in tuples. Values will be strings.
    multi['single'] = 3
    items = multi.multi_items()
    assert sorted(items) == [
        ('item', '1'),
        ('item', '2'),
        ('single', '3'),
        ]

    # Create a multi dict from a list of tuples
    assert utils.MultiDict(items) == {
        'item': ['1', '2'],
        'single': ['3'],
        }

    # Create a multi dict from a dicitonary
    assert utils.MultiDict({'item': 1, 'single': 2}) == {
        'item': [1],
        'single': [2],
        }


def test_singleton():
    # Define a test singleton class
    class TestSingleton(object, metaclass=utils.Singleton):
        pass

    singleton = TestSingleton()
    assert hasattr(singleton, 'instance')
    assert singleton.instance == singleton

    same = TestSingleton()
    # Check that same and singleton are the same instance
    assert singleton.instance == same
    assert same.instance == singleton


def test_dict_crc():
    # Check CRC32 value
    crc = utils.dict_crc({'a': 123, 'test': ['ok'], 'value': False})
    assert isinstance(crc, str)
    assert len(crc) == 9

    # Create a new CRC for the same dictionary
    value = {'a': 123, 'test': ['ok'], 'value': False}
    assert utils.dict_crc(value) == crc

    # Change dictionary and CRC must be different
    value['a'] = 1234
    assert utils.dict_crc(value) != crc


def test_safe_cast():
    # Successfull cast
    assert utils.safe_cast('1', int) == 1

    # Cast that fails
    assert utils.safe_cast('A', float) is None

    # Cast that fails with default
    assert utils.safe_cast('A', float, default=2.2) == 2.2
