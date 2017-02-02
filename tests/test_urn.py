import pytest

from katana import urn
from katana.errors import KatanaError


def test_protocol_url():
    """
    Check protocol URL generation.

    """

    address = '127.0.0.1:88'
    assert urn.url(urn.HTTP, address) == 'http://{}'.format(address)
    assert urn.url(urn.KTP, address) == 'ktp://{}'.format(address)

    with pytest.raises(KatanaError):
        urn.url('urn:katana:protocol:foo', address)
