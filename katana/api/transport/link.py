"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class Link(object):
    """Represents a link object in the Transport."""

    def __init__(self, address, service, ref, uri):
        self.__address = address
        self.__service = service
        self.__ref = ref
        self.__uri = uri

    def get_address(self):
        """
        Get the Gateway address of the Service.

        :rtype: str

        """

        return self.__address

    def get_name(self):
        """
        Get the name of the Service.

        :rtype: str

        """

        return self.__service

    def get_link(self):
        """
        Get the link reference.

        :rtype: str

        """

        return self.__ref

    def get_uri(self):
        """
        Get the URI for the link.

        :rtype: str

        """

        return self.__uri
