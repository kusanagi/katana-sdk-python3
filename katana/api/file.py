from ..payload import get_path
from ..payload import Payload


def file_to_payload(file):
    """Convert a File object to a payload.

    :param file: A File object.
    :type file: `File`

    :rtype: dict

    """

    return Payload().set_many({
        'name': file.get_name(),
        'path': file.get_path(),
        'mime': file.get_mime(),
        'filename': file.get_filename(),
        'size': file.get_size(),
        'exists': file.exists(),
        })


def payload_to_file(payload):
    """Convert payload to a File.

    :param payload: A payload object.
    :type payload: dict

    :rtype: `File`

    """

    return File(
        get_path(payload, 'name'),
        get_path(payload, 'path'),
        mime=get_path(payload, 'mime', None),
        filename=get_path(payload, 'filename', None),
        size=get_path(payload, 'size', None),
        exists=get_path(payload, 'exists', False),
        )


class File(object):
    """File class for API.

    Represents a file received or to be sent to another Service component.

    """

    def __init__(self, name, path, **kwargs):
        if path[:4] not in ('file', 'http'):
            raise TypeError('Path must begin with file:// or http://')

        self.__name = name
        self.__path = path
        self.__mime = kwargs.get('mime') or 'text/plain'
        self.__filename = kwargs.get('filename')
        self.__size = kwargs.get('size') or 0
        self.__exists = kwargs.get('exists', False)

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

    def exists(self):
        """Check if file exists.

        :rtype: bool.

        """

        # TODO: When path starts with http check remote existance
        return self.__exists

    def read(self):
        """Get file data.

        Returns the file data from the stored path.

        :returns: The file data.
        :rtype: bytes

        """

        # TODO: Download file from path using HTTP protocol or read locally.
        # TODO: We might want to have a `read_chunk(chunk_size)` for big files.
        # TODO: We need a token value here, either as property or argument.
        raise NotImplementedError()

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
