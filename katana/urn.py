from .errors import KatanaError


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
