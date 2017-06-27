import pytest

from katana.schema import get_schema_registry
from katana.sdk.component import Component
from katana.sdk.component import ComponentError


def test_component():
    Component.instance = None
    component = Component()
    assert not component.has_resource('dummy')

    # Setting a resource with a callback that return None should fail
    with pytest.raises(ComponentError):
        component.set_resource('dummy', lambda component: None)

    # Getting an invalid resource should fail
    with pytest.raises(ComponentError):
        component.get_resource('dummy')

    # Set a resource
    expected = 'RESULT'
    component.set_resource('dummy', lambda component: expected)
    assert component.has_resource('dummy')
    assert component.get_resource('dummy') == expected

    # Check callback registration
    assert component.startup(lambda: 'foo') == component
    assert component.shutdown(lambda: 'foo') == component
    assert component.error(lambda: 'foo') == component


def test_component_run(mocker):
    Component.instance = None
    component = Component()
    # Runner is defined by sub clases, when is not define component must fail
    with pytest.raises(Exception):
        component.run()

    runner = mocker.MagicMock()
    callbacks = {'foo': lambda: None}

    # Assign a runner and callbacks to the component
    component._runner = runner
    component._callbacks = callbacks
    component.run()
    # Check that runner was run, and callbacks were assigned
    runner.run.assert_called()
    runner.set_callbacks.assert_called_once_with(callbacks)
    # A schema registry singleton must be created on run
    assert get_schema_registry() is not None
    # When there are no special callbacks no set_*_callback should be called
    runner.set_startup_callback.assert_not_called()
    runner.set_shutdown_callback.assert_not_called()
    runner.set_error_callback.assert_not_called()

    # Set callbacks for component and check that they are setted in the runner
    def startup_callback():
        pass

    def shutdown_callback():
        pass

    def error_callback():
        pass

    runner = mocker.MagicMock()
    component._runner = runner
    component.startup(startup_callback)
    component.shutdown(shutdown_callback)
    component.error(error_callback)
    component.run()
    runner.set_startup_callback.assert_called_once_with(startup_callback)
    runner.set_shutdown_callback.assert_called_once_with(shutdown_callback)
    runner.set_error_callback.assert_called_once_with(error_callback)


def test_component_log(logs):
    Component.instance = None
    expected = 'Test log message'
    Component().log(expected)
    out = logs.getvalue()
    # Output without line break should match
    assert out.rstrip() == expected
