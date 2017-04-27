"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

import asyncio
import json
import os
import re
import signal
import socket

from datetime import datetime
from binascii import crc32
from uuid import uuid4

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+00:00"

IPC_RE = re.compile(r'[^a-zA-Z0-9]{1,}')

LOCALHOSTS = ('localhost', '127.0.0.1', '127.0.1.1')

# Default path delimiter
DELIMITER = '/'

# CLI exit status codes
EXIT_OK = os.EX_OK
EXIT_ERROR = 1

# Marker object for empty values
EMPTY = object()

# Make `utcnow` global so it can be imported
utcnow = datetime.utcnow


def uuid():
    """Generate a UUID4.

    :rtype: String.

    """

    return str(uuid4())


def tcp(*args):
    """Create a tcp connection string.

    Function can have a single argument with the full address, or
    2 arguments where first is the address and second is the port.

    :rtype: str.

    """

    if len(args) == 2:
        address = '{}:{}'.format(*args)
    else:
        address = args[0]

    return "tcp://{}".format(address)


def ipc(*args):
    """Create an ipc connection string.

    :rtype: str.

    """

    name = IPC_RE.sub('-', '-'.join(args))
    return 'ipc://@katana-{}'.format(name)


def guess_channel(local, remote):
    """Guess connection channel to use to connect to a remote host.

    Function guesses what channel to use to connect from a local host
    to remote host. Unix socket channel is used when remote host is in
    the same IP, or TCP otherwise.

    :param local: IP address for local host (may include port).
    :type local: str.
    :param remote: IP address and port for remote host.
    :type remote: str.

    :returns: Channel to connect to remote host.
    :rtype: str.

    """

    remote_host = remote.split(':')[0]
    if remote_host in LOCALHOSTS:
        return ipc(remote)

    local_host = local.split(':')[0]
    return ipc(remote) if remote_host == local_host else tcp(remote)


def guess_channel_to_remote(remote):
    """Guess connection channel to use to connect to a remote host.

    Function guesses what channel to use to connect from a local host
    to remote host. Unix socket channel is used when remote host is in
    the same IP, or TCP otherwise.

    All local IP are used to check if remote host can be reached using
    Unix sockets.

    :param remote: IP address and port for remote host.
    :type remote: str.

    :returns: Channel to connect to remote host.
    :rtype: str.

    """

    remote_host = remote.split(':')[0]
    if remote_host in LOCALHOSTS:
        return ipc(remote)

    # Check if remote matches a local IP
    for local_host in socket.gethostbyname_ex(socket.gethostname())[2]:
        if remote_host == local_host:
            return ipc(remote)

    # By default TCP will be used
    return tcp(remote)


def str_to_date(value):
    """Convert a string date to a datetime object.

    :param value: String with a date value.
    :rtype: Datetime object or None.

    """

    if value:
        return datetime.strptime(value, DATE_FORMAT)


def date_to_str(datetime):
    """Convert a datetime object to string.

    :param value: Datetime object.
    :rtype: String or None.

    """

    if datetime:
        return datetime.strftime(DATE_FORMAT)


def nomap(value):
    """Disable name mapping in paths for a value.

    This is used to avoid mapping path item names.

    This just adds a '!' as value prefix.

    :rtype: str

    """

    return '!{}'.format(value)


def get_path(item, path, default=EMPTY, mappings=None, delimiter=DELIMITER):
    """Get dictionary value by path.

    Path can countain the name for a single or for many keys. In case
    a of many keys, path must separate each key name with a '/'.

    Example path: 'key_name/another/last'.

    KeyError is raised when no default value is given.

    By default global payload field mappings are used to traverse keys.

    :param item: A dictionaty like object.
    :type item: dict
    :param path: Path to a value.
    :type path: str
    :param default: Default value to return when value is not found.
    :type default: object
    :param mappings: Optional field name mappings.
    :type mappings: dict
    :param delimiter: Optional path delimiter.
    :type delimiter: str

    :raises: `KeyError`

    :returns: The value for the given path.
    :rtype: object

    """

    try:
        for part in path.split(delimiter):
            # Skip mappings for names starting with "!"
            if part and part[0] == '!':
                name = part[1:]
            else:
                name = part
                # When path name is not available get its mapping
                if mappings and (name not in item):
                    name = mappings.get(part, part)

            item = item[name]
    except KeyError:
        if default != EMPTY:
            return default
        else:
            raise

    return item


def set_path(item, path, value, mappings=None, delimiter=DELIMITER):
    original_item = item
    parts = path.split(delimiter)
    last_part_index = len(parts) - 1
    for index, part in enumerate(parts):
        # Skip mappings for names starting with "!"
        if part and part[0] == '!':
            name = part[1:]
        else:
            name = mappings.get(part, part) if mappings else part

        # Current part is the last item in path
        if index == last_part_index:
            item[name] = value
            break

        if name not in item:
            item[name] = {}
            item = item[name]
        elif isinstance(item[name], dict):
            # Only keep traversing dictionaries
            item = item[name]
        else:
            raise TypeError(part)

    return original_item


def delete_path(item, path, mappings=None, delimiter=DELIMITER):
    try:
        name, *path = path.split(delimiter, 1)
        # Skip mappings for names starting with "!"
        if name and name[0] == '!':
            name = name[1:]
        else:
            # When path name is not in item get its mapping
            if mappings and (name not in item):
                name = mappings.get(name, name)

        # Delete inner path items
        if path:
            # Stop when inner item delete failed
            if not delete_path(item[name], path[0], mappings=mappings):
                return False

            # Delete current path when it is empty
            if not item[name]:
                del item[name]
        else:
            # Item is removed when is the last in the path
            del item[name]
    except KeyError:
        return False

    return True


def merge(from_value, to_value, mappings=None, lists=False):
    """Merge two dictionaries.

    When mappings are given fields names are checked also using their
    mapped names, and merged values are saved using mapped field names.

    :param from_value: Dictionary containing values to merge.
    :type from_value: dict
    :param to_value: Dictionary to merge values into.
    :type to_value: dict
    :param mappings: Field name mappings.
    :type mappings: dict
    :param lists: Optional flag for merging list values.
    :type lists: bool

    :returns: The dictionary where values were merged.
    :rtype: dict

    """

    for key, value in from_value.items():
        # Check if key exists in destination dict and get mapped
        # key name when full name does not exist in destination.
        if (key not in to_value) and mappings:
            # When mapped name exists use it
            name = mappings.get(key, key)
        else:
            # Use dictionary key as name
            name = key

        # When field is not available in destination
        # dict add the value from the original dict.
        if name not in to_value:
            # Use mapped name, when available, to save value
            # if name == key and mappings:
            #     name = mappings.get(name, name)

            # Add new value to destination and continue with next value
            to_value[name] = value
        elif isinstance(value, dict):
            # Field exists in destination and is dict, then merge dict values
            merge(value, to_value[name], mappings=mappings, lists=lists)
        elif lists:
            if isinstance(value, list) and isinstance(to_value[name], list):
                # Field exists in destination and is a list, then extend it
                to_value[name].extend(value)

    return to_value


# TODO: Use Cython for lookup dict ? It is used all the time.
class LookupDict(dict):
    """Dictionary class that allows field value setting and lookup by path.

    It also supports key name mappings when a mappings dictionary is assigned.

    This class reimplements `get` and `set` methods to use paths instead of
    simple key names like a standard dictionary. Single key names can be used
    though.

    """

    def __init__(self, *args, **kwargs):
        self.__mappings = {}
        self.__defaults = {}
        super().__init__(*args, **kwargs)

    @staticmethod
    def is_empty(value):
        """Check if a value is the empty value.

        :rtype: bool

        """

        return value is EMPTY

    def path_exists(self, path, delimiter=DELIMITER):
        """Check if a path is available.

        :param path: Path to a value.
        :type path: str
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :rtype: bool

        """

        try:
            self.get(path, delimiter=delimiter)
        except KeyError:
            return False
        else:
            return True

    def set_mappings(self, mappings):
        """Set key name mappings.

        :param mappings: Key name mappings.
        :type mappings: dict.

        """

        self.__mappings = mappings

    def set_defaults(self, defaults):
        """Set default values to use during get calls.

        :param mappings: Key name mappings.
        :type mappings: dict.

        """

        self.__defaults = defaults

    def get(self, path, default=EMPTY, delimiter=DELIMITER):
        """Get value by key path.

        Path can countain the name for a single or for many keys. In case
        a of many keys, path must separate each key name with a '/'.

        Example path: 'key_name/another/last'.

        KeyError is raised when no default value is given.

        :param path: Path to a value.
        :type path: str.
        :param default: Default value to return when value is not found.
        :type default: object
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: KeyError.

        :returns: The value for the given path.

        """

        if default == EMPTY:
            default = self.__defaults.get(path, EMPTY)

        return get_path(self, path, default, self.__mappings, delimiter)

    def get_many(self, *paths, delimiter=DELIMITER):
        """Get multiple values by key path.

        KeyError is raised when no default value is given.
        Default values can be assigned using `set_defaults`.

        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: KeyError.

        :returns: The values for the given path.
        :rtype: list

        """

        result = []
        for path in paths:
            result.append(self.get(path, delimiter=delimiter))

        return result

    def set(self, path, value, delimiter=DELIMITER):
        """Set value by key path.

        Path traversing is only done for dictionary like values.
        TypeError is raised for a key when a non traversable value is found.

        When a key name does not exists a new dictionary is created for that
        key name that it is used for traversing the other key names, so many
        dictionaries are created inside one another to complete the given path.

        When a mapping is assigned it is used to reverse key names in path to
        the original mapped key name.

        Example path: 'key_name/another/last'.

        :param path: Path to a value.
        :type path: str.
        :param value: Value to set in the give path.
        :type value: object
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: TypeError.

        :returns: Current instance.
        :rtype: `LookupDict`

        """

        set_path(self, path, value, self.__mappings, delimiter)
        return self

    def set_many(self, values, delimiter=DELIMITER):
        """Set set multiple values by key path.

        :param values: A dictionary with paths and values.
        :type values: dict
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: TypeError.

        :returns: Current instance.
        :rtype: `LookupDict`

        """

        for path, value in values.items():
            self.set(path, value, delimiter=delimiter)

        return self

    def push(self, path, value, delimiter=DELIMITER):
        """Push value by key path.

        Path traversing is only done for dictionary like values.
        TypeError is raised for a key when a non traversable value is found.

        When a key name does not exists a new dictionary is created for that
        key name that it is used for traversing the other key names, so many
        dictionaries are created inside one another to complete the given path.

        When the final key is found is is expected to be a list where the value
        will be appended. TypeError is raised when final key is not a list.
        A new list is created when last key does not exists.

        When a mapping is assigned it is used to reverse key names in path to
        the original mapped key name.

        Example path: 'key_name/another/last'.

        :param path: Path to a value.
        :type path: str
        :param value: Value to set in the give path.
        :type value: object
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: TypeError

        :returns: Current instance.
        :rtype: `LookupDict`

        """

        item = self
        parts = path.split(delimiter)
        last_part_index = len(parts) - 1
        for index, part in enumerate(parts):
            # Skip mappings for names starting with "!"
            if part and part[0] == '!':
                name = part[1:]
            else:
                name = self.__mappings.get(part, part)

            # Current part is the last item in path
            if index == last_part_index:
                if name not in item:
                    # When last key does not exists create a list
                    item[name] = []
                elif not isinstance(item[name], list):
                    # When last key exists it must be a list
                    raise TypeError(name)

                item[name].append(value)
                break

            if name not in item:
                item[name] = {}
                item = item[name]
            elif isinstance(item[name], dict):
                # Only keep traversing dictionaries
                item = item[name]
            else:
                raise TypeError(part)

        return self

    def merge(self, path, value, delimiter=DELIMITER):
        """Merge a dictionary value into a location.

        Value must be a dictionary. Location given by path must
        contain a dictionary where to merge the dictionary value.

        :param path: Path to a value.
        :type path: str
        :param value: Value to set in the give path.
        :type value: object
        :param delimiter: Optional path delimiter.
        :type delimiter: str

        :raises: `TypeError`

        :returns: Current instance.
        :rtype: `LookupDict`

        """

        if not isinstance(value, dict):
            raise TypeError('Merge value is not a dict')

        if self.path_exists(path, delimiter=delimiter):
            item = self.get(path, delimiter=delimiter)
            if not isinstance(item, dict):
                raise TypeError('Value in path "{}" is not dict'.format(path))
        else:
            item = {}
            self.set(path, item, delimiter=delimiter)

        merge(value, item, mappings=self.__mappings, lists=True)
        return self


class MultiDict(dict):
    """Dictionary where all values are list.

    This is used to allow multiple values for the same key.

    """

    def __init__(self, mappings=None):
        super().__init__()
        if mappings:
            self._set_mappings(mappings)

    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)

    def _set_mappings(self, mappings):
        if isinstance(mappings, dict):
            mappings = mappings.items()

        for key, value in mappings:
            if isinstance(value, list):
                self.setdefault(key, value)
            else:
                self[key] = value

    def getone(self, key, default=None):
        if key not in self:
            return default

        return self[key][0]

    def multi_items(self):
        """Get a list of tuples with all items in dictionary.

        The difference between this method and `items()` is that this
        one will split values inside lists as independent single items.

        :rtype: list.

        """

        items = []
        for name, values in self.items():
            items.extend((name, str(value)) for value in values)

        return items


class Singleton(type):
    """Metaclass to make a class definition a singleton.

    The class definition using this will contain a class property
    called `instance` with the only instance allowed for that class.

    Instance is, of course, only created the first time the class is called.

    """

    def __init__(cls, name, bases, classdict):
        super(Singleton, cls).__init__(name, bases, classdict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kw)

        return cls.instance


class RunContext(object):
    """Handles graceful async process termination.

    All keyword arguments passed to context during creation are used as
    properties for the context object. Aditionally context contains a
    'loop' property with the main event loop.

    On run context hooks to SIGTERM and SIGINT signals to handle graceful
    process termination when process is killed or when CTRL-C is pressed
    if process is run from console.

    Async callbacks can be registered to perform application cleanup tasks.
    These callbacks are executed right after termination signal is received.
    Callback must be a coroutine that receives a single 'context' argument
    with an instance of this class.

    """

    def __init__(self, loop, **kwargs):
        self.__dict__.update(kwargs)
        self.__terminate = False
        self.__cleaned = False
        self.__callbacks = []
        self.tasks = []
        self.loop = loop

    def hook_signals(self):
        self.loop.add_signal_handler(signal.SIGTERM, self.terminate)
        self.loop.add_signal_handler(signal.SIGINT, self.terminate)

    def terminate(self, *args, **kwargs):
        self.__terminate = True

    def register_callback(self, callback):
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError('Callback is not a coroutine function')

        # Append callback as a task
        self.__callbacks.append(callback(self))

    @asyncio.coroutine
    def cleanup(self):
        if self.__cleaned:  # pragma: no cover
            return

        # Execute all registered callbacks
        if self.__callbacks:
            yield from asyncio.wait(self.__callbacks, timeout=1.5)

        self.__cleaned = True

        # Finish all pending tasks
        yield from self.finish_pending_tasks()

    @asyncio.coroutine
    def finish_pending_tasks(self):
        """Finish all tasks that are still running.

        When an exception is found it is raised after all tasks are finished.
        Only the first exception that is found is raised.

        """

        if not self.tasks:  # pragma: no cover
            return

        exc = None
        for task in self.tasks:
            if task.done():
                # When an exception is found save it
                if task.exception() and not exc:
                    exc = task.exception()
                else:
                    # This task is finished, continue with next one
                    continue  # pragma: no cover

            task.cancel()

        # Wait for all task to finish
        yield from asyncio.wait(self.tasks, timeout=2)

        # When an exception is found raise it
        if exc:
            raise exc

    def check_tasks_exceptions(self):
        """Check for task exceptions.

        Run context terminates when an exception is found.

        """

        all_done = True

        for task in self.tasks:
            if not task.done():
                all_done = False
                continue

            # Task is done, check for exceptions
            if task.exception():
                self.__terminate = True
                break

        # Stop run context when there are no more tasks running
        if all_done:
            self.__terminate = True

    @asyncio.coroutine
    def run(self):
        """Hook to termination signals and run until terminate is called."""

        self.__cleaned = False
        self.hook_signals()
        while not self.__terminate:
            yield from asyncio.sleep(0.2)
            self.check_tasks_exceptions()

        yield from self.cleanup()


def install_uvevent_loop():  # pragma: no cover
    """Install uvloop as default event loop when available.

    See: http://magic.io/blog/uvloop-blazing-fast-python-networking/

    """
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def dict_crc(dict):
    """Create a CRC for a dictionary like object.

    :param dict: Dictionary to use for CRC generation.
    :type dict: dict

    :rtype: str

    """

    return str(crc32(json.dumps(dict, sort_keys=True).encode('utf8')))


def safe_cast(value, cast_func, default=None):
    """Cast a value to another type.

    When casting fails return a default value, or None by default.

    :returns: The casted value or None.

    """

    try:
        return cast_func(value)
    except:
        return default
