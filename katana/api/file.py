"""
Python 3 SDK for the KATANA(tm) Platform (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

import logging
import os
import urllib.request

from http.client import HTTPConnection
from urllib.parse import urlparse

from ..payload import get_path
from ..payload import Payload

LOG = logging.getLogger(__name__)


def file_to_payload(file):
    """Convert a File object to a payload.

    :param file: A File object.
    :type file: `File`

    :rtype: dict

    """

    # http:// or file:// prefix is removed from path in payload data
    return Payload().set_many({
        'path': file.get_path()[7:],
        'mime': file.get_mime(),
        'filename': file.get_filename(),
        'size': file.get_size(),
        'token': file.get_token(),
        })


def payload_to_file(name, payload):
    """Convert payload to a File.

    :param name: File field name.
    :type name: str
    :param payload: A payload object.
    :type payload: dict

    :rtype: `File`

    """

    # All files created from payload data are remote
    return File(
        name,
        'http://{}'.format(get_path(payload, 'path')),
        mime=get_path(payload, 'mime', None),
        filename=get_path(payload, 'filename', None),
        size=get_path(payload, 'size', None),
        token=get_path(payload, 'token', None),
        )


class File(object):
    """File class for API.

    Represents a file received or to be sent to another Service component.

    """

    def __init__(self, name, path, **kwargs):
        if (not path) or path[:4] not in ('file', 'http'):
            raise TypeError('Path must begin with file:// or http://')

        self.__name = name
        self.__path = path
        self.__mime = kwargs.get('mime') or 'text/plain'
        self.__filename = kwargs.get('filename')
        self.__size = kwargs.get('size') or 0
        self.__token = kwargs.get('token') or ''

    def get_name(self):
        """Get parameter name.

        :rtype: str

        """

        return self.__name

    def get_path(self):
        """Get path.

        :rtype: str

        """

        return self.__path

    def get_mime(self):
        """Get mime type.

        :rtype: str.

        """

        return self.__mime

    def get_filename(self):
        """Get file name.

        :rtype: str.

        """

        return self.__filename

    def get_size(self):
        """Get file size.

        :rtype: int.

        """

        return self.__size

    def get_token(self):
        """Get file server token.

        :rtype: str.

        """

        return self.__token

    def exists(self):
        """Check if file exists.

        A request is made to check existence when file
        is located in a remote file server.

        :rtype: bool.

        """

        # Check remote file existence when path is HTTP (otherwise is file://)
        if self.__path[:7] == 'http://':
            # Setup headers for request
            headers = {}
            if self.__token:
                headers['X-Token'] = self.__token

            # Make a HEAD request to check that file exists
            part = urlparse(self.__path)
            try:
                conn = HTTPConnection(part.netloc, timeout=2)
                conn.request('HEAD', part.path, headers=headers)
                response = conn.getresponse()
                exists = response.status == 200
                if not exists:
                    LOG.error(
                        'File server request failed for %s, with error %s %s',
                        self.__path,
                        response.status,
                        response.reason,
                        )
                return exists
            except:
                LOG.exception('File server request failed: %s', self.__path)
                return False
        else:
            # Check file existence locally
            return os.path.isfile(self.__path[7:])

    def read(self):
        """Get file data.

        Returns the file data from the stored path.

        :returns: The file data.
        :rtype: bytes

        """

        # Check if file is a remote file
        if self.__path[:7] == 'http://':
            # Setup headers for request
            headers = {}
            if self.__token:
                headers['X-Token'] = self.__token

            request = urllib.request.Request(self.__path, headers=headers)

            # Read file contents from remote file server
            try:
                with urllib.request.urlopen(request) as file:
                    return file.read()
            except:
                LOG.exception('Unable to read file: %s', self.__path)
        else:
            # Check that file exists locally
            if not os.path.isfile(self.__path[7:]):
                LOG.error('File does not exist: %s', self.__path)
            else:
                # Read local file contents
                try:
                    with open(self.__path[7:], 'rb') as file:
                        return file.read()
                except:
                    LOG.exception('Unable to read file: %s', self.__path)

        return b''

    def copy(self, **kwargs):
        """Create a copy of current object.

        :param name: File parameter name.
        :type name: str
        :param mime: Mime type for the file.
        :type mime: str

        :rtype: `File`

        """

        return self.__class__(
            kwargs.get('name', self.__name),
            self.__path,
            size=self.__size,
            mime=kwargs.get('mime', self.__mime),
            path=self.__path,
            )

    def copy_with_name(self, name):
        return self.copy(name=name)

    def copy_with_mime(self, mime):
        return self.copy(mime=mime)
