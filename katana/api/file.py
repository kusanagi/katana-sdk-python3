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

        # TODO: Download file from path using HTTP protocol or read locally
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
