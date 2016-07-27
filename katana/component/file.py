class File(object):

    def __init__(self, name, filename, **kwargs):
        self.name = name
        self.filename = filename
        self.size = kwargs.get('size') or 0
        self.mime = kwargs.get('mime') or 'text/plain'
        self.path = kwargs.get('path')
        self.exists = kwargs.get('exists', False)

    def read(self):
        """Get file data.

        Returns the file data from the stored path.

        :returns: The file data.
        :rtype: bytes.

        """

        # TODO: Download file from path using HTTP protocol
        raise NotImplementedError()
