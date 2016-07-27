import asyncio
import os
import sys

from datetime import datetime
from uuid import uuid4

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+00:00"

LOCALHOST = '127.0.0.1'

# CLI exit status codes
EXIT_OK = os.EX_OK
EXIT_ERROR = 1

# Marker object for empty values
EMPTY = object()

# Make `utcnow` global so it can be imported
utcnow = datetime.utcnow


def print_error(text):
    """Print an error message to stderr.

    :type text: str.

    """

    print(text, file=sys.stderr)


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

    args = [arg.replace('.', '-').replace(':', '-') for arg in args]
    return "ipc://@kusanagi-{}".format('-'.join(args))


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

    local = local.split(':')[0]
    return ipc(remote) if remote.startswith(local) else tcp(remote)


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


class LookupDict(dict):
    """Dictionary class that allows field value setting and lookup by path.

    It also supports key name mappings when a mappings dictionary is assigned.

    This class reimplements `get` and `set` methods to use paths instead of
    simple key names like a standard dictionary. Single key names can be used
    though.

    """

    def __init__(self, *args, **kwargs):
        self.__mappings = {}
        super().__init__(*args, **kwargs)

    def path_exists(self, path):
        """Check if a path is available.

        :rtype: bool.

        """

        default = object()
        return self.get(path, default=default) != default

    def set_mappings(self, mappings):
        """Set key name mappings.

        :param mappings: Key name mappings.
        :type mappings: dict.

        """

        self.__mappings = mappings

    def get(self, path, default=EMPTY):
        """Get value by key path.

        Path can countain the name for a single or for many keys. In case
        a of many keys, path must separate each key name with a '/'.

        Example path: 'key_name/another/last'.

        KeyError is raised when no default value is given.

        :param path: Path to a value.
        :type path: str.
        :param default: Default value to return when value is not found.

        :raises: KeyError.

        :returns: The value for the given path.

        """

        item = self
        try:
            for part in path.split('/'):
                name = part
                # When path name is not available get its mapping
                if name not in item:
                    name = self.__mappings.get(part, part)

                item = item[name]
        except KeyError:
            if default != EMPTY:
                return default
            else:
                raise

        return item

    def set(self, path, value):
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

        :raises: TypeError.

        """

        item = self
        parts = path.split('/')
        last_part_index = len(parts) - 1
        for index, part in enumerate(parts):
            name = self.__mappings.get(part, part)
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

    def set_many(self, values):
        """Set set multiple values by key path.

        :param values: A dictionary with paths and values.
        :type values: dict.

        :raises: TypeError.

        """

        for path, value in values.items():
            self.set(path, value)


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


def install_uvevent_loop():
    """Install uvloop as default event loop when available.

    See: http://magic.io/blog/uvloop-blazing-fast-python-networking/

    """
    try:
        import uvloop
    except ImportError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
