from katana.sdk.service import get_component
from katana.sdk.service import Service


def test_service_component():
    # Check service component singleton creation
    assert get_component() is None
    service = Service()
    assert get_component() == service

    def action_callback():
        pass

    assert service._callbacks == {}

    # Set an action callback
    action_name = 'foo'
    assert action_name not in service._callbacks
    service.action(action_name, action_callback)
    assert action_name in service._callbacks
    assert service._callbacks[action_name] == action_callback
