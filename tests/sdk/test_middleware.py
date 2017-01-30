from katana.sdk.middleware import get_component
from katana.sdk.middleware import Middleware


def test_middleware_component():
    # Check middleware component singleton creation
    assert get_component() is None
    middleware = Middleware()
    assert get_component() == middleware

    def request_callback():
        pass

    def response_callback():
        pass

    assert middleware._callbacks == {}

    # Set request callback
    assert 'request' not in middleware._callbacks
    middleware.request(request_callback)
    assert 'request' in middleware._callbacks
    assert middleware._callbacks['request'] == request_callback

    # Set response callback
    assert 'response' not in middleware._callbacks
    middleware.response(response_callback)
    assert 'response' in middleware._callbacks
    assert middleware._callbacks['response'] == response_callback
