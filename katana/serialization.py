"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

import datetime
import decimal
import time

import msgpack

from . import utils
from .payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


def encode(obj):
    """Handle packing for custom types."""

    if isinstance(obj, decimal.Decimal):
        return ['type', 'decimal', str(obj).split('.')]
    elif isinstance(obj, datetime.datetime):
        return ['type', 'datetime', utils.date_to_str(obj)]
    elif isinstance(obj, datetime.date):
        return ['type', 'datetime', obj.strftime('%Y-%m-%d')]
    elif isinstance(obj, time.struct_time):
        return ['type', 'time', time.strftime('%H:%M', obj)]
    elif hasattr(obj, '__serialize__'):
        return obj.__serialize__()

    raise TypeError('{} is not serializable'.format(repr(obj)))


def decode(data):
    """Handle unpacking for custom types."""

    if isinstance(data, list) and len(data) == 3 and data[0] == 'type':
        data_type = data[1]
        try:
            if data_type == 'decimal':
                return decimal.Decimal('.'.join(data[2]))
            elif data_type == 'datetime':
                return utils.str_to_date(data[2])
            elif data_type == 'date':
                return datetime.datetime.strptime(data[2], '%Y-%m-%d')
            elif data_type == 'time':
                # Use time as a string "HH:MM"
                return data[2]
        except:
            # Don't fail when there are inconsistent data values.
            # Invalid values will be null.
            return

    return data


def pack(data):
    """Pack python data to a binary stream.

    :param data: A python object to pack.

    :rtype: bytes.

    """

    return msgpack.packb(
        data,
        default=encode,
        encoding='utf-8',
        use_bin_type=True,
        )


def unpack(stream):
    """Pack python data to a binary stream.

    :param stream: bytes.

    :rtype: The unpacked python object.

    """

    return msgpack.unpackb(stream, object_hook=decode, encoding='utf-8')


def stream_to_payload(stream):
    """Convert a packed stream to a payload.

    :param stream: Packed payload stream.
    :type stream: bytes

    :raises: TypeError

    :rtype: Payload

    """

    try:
        return Payload(unpack(stream))
    except TypeError:
        raise TypeError('Invalid payload')
    except Exception:
        raise TypeError('Invalid payload stream')
