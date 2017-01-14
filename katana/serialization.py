"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

import datetime
import decimal

import msgpack

from . import utils
from .payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


def encode(obj):
    """Handle packing for custom types."""

    if isinstance(obj, decimal.Decimal):
        # Note: Use str instead of float
        # to avoid dealing with presition
        return {'__type__': 'decimal', 'value': str(obj)}
    elif isinstance(obj, datetime.datetime):
        return {'__type__': 'datetime', 'value': utils.date_to_str(obj)}
    elif isinstance(obj, datetime.date):
        return {'__type__': 'date', 'value': obj.strftime('%Y-%m-%d')}
    elif hasattr(obj, '__serialize__'):
        return obj.__serialize__()

    raise TypeError('{} is not serializable'.format(repr(obj)))


def decode(data):
    """Handle unpacking for custom types."""

    if isinstance(data, dict) and '__type__' in data:
        data_type = data['__type__']
        if data_type == 'decimal':
            return decimal.Decimal(data['value'])
        elif data_type == 'datetime':
            return utils.str_to_date(data['value'])
        elif data_type == 'date':
            return datetime.datetime.strptime(data['value'], '%Y-%m-%d')

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
