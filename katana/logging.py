"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import base64
import logging
import time
import types
import sys

from datetime import datetime

from . import json

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

# Syslog numeric levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
NOTICE = WARNING + 1
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
ALERT = CRITICAL + 1
EMERGENCY = ALERT + 1

# Mappings between Syslog numeric severity levels and python logging levels
SYSLOG_NUMERIC = {
    0: EMERGENCY,
    1: ALERT,
    2: logging.CRITICAL,
    3: logging.ERROR,
    4: NOTICE,
    5: logging.WARNING,
    6: logging.INFO,
    7: logging.DEBUG,
    }


class RequestLogger(object):
    """
    Logger for requests.

    It appends the request ID to all logging messages.

    """

    def __init__(self, rid, name):
        self.rid = rid
        self.__logger = logging.getLogger(name)

    def debug(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.debug(msg, *args, **kw)

    def info(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.info(msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.warning(msg, *args, **kw)

    def error(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.error(msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.critical(msg, *args, **kw)

    def exception(self, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.exception(msg, *args, **kw)

    def log(self, lvl, msg, *args, **kw):
        if self.rid:
            msg += ' |{}|'.format(self.rid)

        self.__logger.log(lvl, msg, *args, **kw)


class KatanaFormatter(logging.Formatter):
    """Default KATANA logging formatter."""

    def formatTime(self, record, *args, **kwargs):
        utc = time.mktime(time.gmtime(record.created)) + (record.created % 1)
        return datetime.fromtimestamp(utc).isoformat()[:-3]


def value_to_log_string(value, max_chars=100000):
    """Convert a value to a string.

    :param value: A value to log.
    :type value: object
    :param max_chars: Optional maximum number of characters to return.
    :type max_chars: int

    :rtype: str

    """

    if value is None:
        output = 'NULL'
    elif isinstance(value, bool):
        output = 'TRUE' if value else 'FALSE'
    elif isinstance(value, str):
        output = value
    elif isinstance(value, bytes):
        # Binary data is logged as base64
        output = base64.b64encode(value).decode('utf8')
    elif isinstance(value, (dict, list, tuple)):
        output = json.serialize(value, prettify=True).decode('utf8')
    elif isinstance(value, types.FunctionType):
        if value.__name__ == '<lambda>':
            output = 'anonymous'
        else:
            output = '[function {}]'.format(value.__name__)
    else:
        output = repr(value)

    return output[:max_chars]


def get_output_buffer():
    """Get buffer interface to send logging output.

    :rtype: io.IOBase

    """

    return sys.stdout


def disable_logging():
    """Disable all logs."""

    logging.disable(sys.maxsize)


def setup_katana_logging(type, name, version, framework, level):
    """Initialize logging defaults for KATANA.

    :param type: Component type.
    :param name: Component name.
    :param version: Component version.
    :param framework: KATANA framework version.
    :param level: Logging level.

    """

    # Add the new logging levels to follow KATANA SDK specs
    logging.addLevelName(NOTICE, 'NOTICE')
    logging.addLevelName(ALERT, 'ALERT')
    logging.addLevelName(EMERGENCY, 'EMERGENCY')

    format = "%(asctime)sZ {} [%(levelname)s] [SDK] %(message)s".format(
        "{} {}/{} ({})".format(type, name, version, framework)
        )

    output = get_output_buffer()

    # Setup root logger
    root = logging.root
    if not root.handlers:
        logging.basicConfig(level=level, stream=output)
        root.setLevel(level)
        root.handlers[0].setFormatter(KatanaFormatter(format))

    # Setup katana logger
    logger = logging.getLogger('katana')
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=output)
        handler.setFormatter(KatanaFormatter(format))
        logger.addHandler(handler)
        logger.propagate = False

    # Setup katana api logger
    logger = logging.getLogger('katana.api')
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=output)
        handler.setFormatter(KatanaFormatter(format))
        logger.addHandler(handler)
        logger.propagate = False

    # Setup other loggers
    logger = logging.getLogger('asyncio')
    logger.setLevel(logging.ERROR)
