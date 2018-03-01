"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

from katana.errors import KatanaError

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"

# Protocols
HTTP = 'urn:katana:protocol:http'
KTP = 'urn:katana:protocol:ktp'


def url(protocol, address):
    """Create a URL for a protocol.

    :param protocol: URN for a protocol.
    :type protocol: str
    :param address: An IP address. It can include a port.
    :type address: str

    :raises: KatanaError

    :rtype: str

    """

    if protocol == HTTP:
        return 'http://{}'.format(address)
    elif protocol == KTP:
        return 'ktp://{}'.format(address)
    else:
        raise KatanaError('Unknown protocol: {}'.format(protocol))
