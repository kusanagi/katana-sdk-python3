"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
import http.client
import logging
import mimetypes
import os
import urllib.request

from urllib.parse import urlparse

from ..payload import get_path
from ..payload import Payload

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"

LOG = logging.getLogger(__name__)


def file_to_payload(file):
    """Convert a File object to a payload.

    :param file: A File object.
    :type file: `File`

    :rtype: Payload

    """

    return Payload().set_many({
        'name': file.get_name(),
        'path': file.get_path(),
        'mime': file.get_mime(),
        'filename': file.get_filename(),
        'size': file.get_size(),
        'token': file.get_token(),
        })


def payload_to_file(payload):
    """Convert payload to a File.

    :param payload: A payload object.
    :type payload: dict

    :rtype: `File`

    """

    # All files created from payload data are remote
    return File(
        get_path(payload, 'name'),
        get_path(payload, 'path'),
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
        # Validate and set file name
        if not (name or '').strip():
            raise TypeError('Invalid file name')
        else:
            self.__name = name

        # Validate and set file path
        path = (path or '').strip()
        protocol = path[:7]
        if path and protocol not in ('file://', 'http://'):
            self.__path = 'file://{}'.format(path)
            protocol = 'file://'
        else:
            self.__path = path

        # Set mime type, or guess it from path
        self.__mime = kwargs.get('mime')
        if not self.__mime:
            self.__mime = mimetypes.guess_type(path)[0] or 'text/plain'

        # Set file name, or get it from path
        self.__filename = kwargs.get('filename') or os.path.basename(path)

        # Set file size
        self.__size = kwargs.get('size')
        if self.__size is None:
            if protocol == 'file://':
                try:
                    # Get file size from file
                    self.__size = os.path.getsize(self.__path[7:])
                except OSError:
                    self.__size = 0
            else:
                self.__size = 0

        # Token is required for remote file paths
        self.__token = kwargs.get('token') or ''
        if protocol == 'http://' and not self.__token:
            raise TypeError('Token is required for remote file paths')

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

        if not self.__path:
            return False

        # Check remote file existence when path is HTTP (otherwise is file://)
        if self.__path[:7] == 'http://':
            # Setup headers for request
            headers = {}
            if self.__token:
                headers['X-Token'] = self.__token

            # Make a HEAD request to check that file exists
            part = urlparse(self.__path)
            try:
                conn = http.client.HTTPConnection(part.netloc, timeout=2)
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

    def is_local(self):
        """Check if file is a local file.

        :rtype: bool

        """

        return self.__path[:7] == 'file://'

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
            )

    def copy_with_name(self, name):
        return self.copy(name=name)

    def copy_with_mime(self, mime):
        return self.copy(mime=mime)
