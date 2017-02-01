import os

import click
import pytest

from katana import payload
from katana.sdk.runner import apply_cli_options
from katana.sdk.runner import ComponentRunner
from katana.sdk.runner import key_value_strings_callback
from katana.utils import EXIT_ERROR
from katana.utils import EXIT_OK
from zmq.error import ZMQError


def test_key_value_strings_callback():
    ctx = None
    param = None

    # Check empty result
    assert key_value_strings_callback(ctx, param, None) == {}

    # Check result for a list of values
    values = ['foo=bar', 'hello=world', 'wacky=value=go']
    assert key_value_strings_callback(ctx, param, values) == {
        'foo': 'bar',
        'hello': 'world',
        'wacky': 'value=go',
        }

    # Check invalid parameter format error
    with pytest.raises(click.BadParameter):
        key_value_strings_callback(ctx, param, ['boom'])


def test_apply_cli_options(mocker, cli):
    class Foo(ComponentRunner):
        pass

    # Create a mock for the run method and apply CLI options decorator
    run = mocker.MagicMock()
    Foo.run = apply_cli_options(run)

    foo = Foo(None, None, 'Foo help text')

    result = cli.invoke(foo.run(), [
        '--name', 'foo',
        '--version', '1.0',
        '--component', 'service',
        '--platform-version', '1.0.0',
        '--socket', '@katana-127-0-0-1-5010-foo',
        '--tcp', '5010',
        '--debug',
        '--disable-compact-names',
        '--quiet',
        '--var', 'foo=bar',
        '--var', 'hello=world',
        ])

    # Running the component should succeed
    assert result.exit_code == 0

    # Check parsed CLI values that were sent as arguments for run
    args, kwargs = run.call_args
    assert args == (foo, )
    assert kwargs == {
        'name': 'foo',
        'version': '1.0',
        'component': 'service',
        'platform_version': '1.0.0',
        'socket': '@katana-127-0-0-1-5010-foo',
        'tcp': 5010,
        'debug': True,
        'disable_compact_names': True,
        'quiet': True,
        'var': {'foo': 'bar', 'hello': 'world'},
        }

    # Check that by removing the TESTING environment component runs
    # but ends with an exit code of 2 because argv does not have
    # valid values.
    exit = mocker.patch('sys.exit')
    del os.environ['TESTING']
    foo.run()
    exit.assert_called_once_with(2)
    os.environ['TESTING'] = '1'


def test_component_runner():
    runner = ComponentRunner(None, None, None)
    # Check that there are CLI argument definitions
    assert len(runner.get_argument_options()) > 0
    # Check callbacks
    callbacks = {'A': lambda action: '', 'B': lambda action: ''}
    runner.set_callbacks(callbacks)
    assert runner.callbacks == callbacks


def test_component_runner_args():
    mandatory_args = {
        'name': 'foo',
        'version': '1.0',
        'component': 'service',
        }
    args = {
        'socket': '@katana-127-0-0-1-4001-foo',
        'tcp': '4001',
        'debug': True,
        'disable_compact_names': True,
        }
    args.update(mandatory_args)

    runner = ComponentRunner(None, None, None)
    runner._args = args
    assert runner.args == args
    assert runner.name == args['name']
    assert runner.socket_name == args['socket']
    assert runner.tcp_port == args['tcp']
    assert runner.version == args['version']
    assert runner.component_type == args['component']
    assert runner.debug
    assert not runner.compact_names

    expected_socket_name = '@katana-service-foo-1-0'
    default_socket_name = runner.get_default_socket_name()
    assert default_socket_name == expected_socket_name

    # Check default values for optional arguments
    runner = ComponentRunner(None, None, None)
    runner._args = mandatory_args
    assert runner.args == mandatory_args
    assert runner.socket_name == runner.get_default_socket_name()
    assert runner.tcp_port is None
    assert not runner.debug
    assert runner.compact_names


def test_component_run(mocker, cli):
    mocker.patch('asyncio.set_event_loop')

    exit = mocker.patch('os._exit')
    loop = mocker.patch('zmq.asyncio.ZMQEventLoop')

    def error_callback():
        pass

    callbacks = {'A': lambda action: '', 'B': lambda action: ''}
    server = mocker.MagicMock()
    ServerCls = mocker.MagicMock(return_value=server)
    socket = '@katana-127-0-0-1-5010-foo'
    cli_args = [
        '--name', 'foo',
        '--version', '1.0',
        '--component', 'service',
        '--platform-version', '1.0.0',
        '--socket', socket,
        '--debug',
        '--disable-compact-names',
        '--quiet',
        '--var', 'foo=bar',
        '--var', 'hello=world',
        ]

    # Create a component runner and run it
    runner = ComponentRunner(None, ServerCls, None)
    runner.set_callbacks(callbacks)
    runner.set_error_callback(error_callback)
    result = cli.invoke(runner.run(), cli_args)
    # Running the component should succeed
    assert result.exit_code == 0

    # Check that compact names were disabled
    assert payload.DISABLE_FIELD_MAPPINGS

    # Check server creation arguments
    args, kwargs = ServerCls.call_args
    assert args == ('ipc://{}'.format(socket), callbacks, {
        'name': 'foo',
        'version': '1.0',
        'component': 'service',
        'platform_version': '1.0.0',
        'socket': socket,
        'tcp': None,
        'debug': True,
        'disable_compact_names': True,
        'quiet': True,
        'var': {'foo': 'bar', 'hello': 'world'},
        })
    assert 'debug' in kwargs
    assert kwargs['debug']
    assert 'source_file' in kwargs
    assert len(kwargs['source_file']) > 0
    assert kwargs.get('error_callback') == error_callback

    # Check that server listen was called
    server.listen.assert_called_once()

    # Check that loop was run
    loop.run_until_complete.assert_called_once()
    loop.close.assert_called_once()

    # Check normal exit
    exit.assert_called_once_with(EXIT_OK)


def test_component_run_errors(mocker, cli):
    side_effects = (ZMQError, ZMQError(98), Exception)
    loop = mocker.MagicMock()
    loop.run_until_complete.side_effect = side_effects

    mocker.patch('asyncio.set_event_loop')
    mocker.patch('zmq.asyncio.ZMQEventLoop', return_value=loop)

    exit = mocker.patch('os._exit')

    ServerCls = mocker.MagicMock()
    socket = '@katana-127-0-0-1-5010-foo'
    cli_args = [
        '--name', 'foo',
        '--version', '1.0',
        '--component', 'service',
        '--platform-version', '1.0.0',
        '--socket', socket,
        '--debug',
        '--disable-compact-names',
        '--quiet',
        '--var', 'foo=bar',
        '--var', 'hello=world',
        ]

    # Run component twice to check ZMQError and Exception cases
    for _ in range(len(side_effects)):
        # Create a component runner and run it
        runner = ComponentRunner(None, ServerCls, None)
        result = cli.invoke(runner.run(), cli_args)

        # Running the component should succeed
        assert result.exit_code == 0

        # Check exit with error
        exit.assert_called_with(EXIT_ERROR)


def test_component_run_callbacks(mocker, cli):
    loop = mocker.MagicMock()

    mocker.patch('asyncio.set_event_loop')
    mocker.patch('zmq.asyncio.ZMQEventLoop', return_value=loop)

    exit = mocker.patch('os._exit')

    # Define values to be used in component runner
    startup_callback = mocker.MagicMock()
    shutdown_callback = mocker.MagicMock()
    component = object()
    ServerCls = mocker.MagicMock()
    cli_args = [
        '--name', 'foo',
        '--version', '1.0',
        '--component', 'service',
        '--platform-version', '1.0.0',
        '--tcp', '5000',
        ]

    # Create the component runner and assign callbacks
    runner = ComponentRunner(component, ServerCls, None)
    runner.set_startup_callback(startup_callback)
    runner.set_shutdown_callback(shutdown_callback)

    result = cli.invoke(runner.run(), cli_args)
    # Running the component should succeed
    assert result.exit_code == 0

    # Check that callbacks were called
    startup_callback.assert_called_once_with(component)
    shutdown_callback.assert_called_once_with(component)

    # Check normal exit
    exit.assert_called_once_with(EXIT_OK)

    # Check startup callback errors
    startup_callback.side_effect = Exception
    result = cli.invoke(runner.run(), cli_args)
    # Running the component should succeed
    assert result.exit_code == 0
    # Check error exit
    exit.assert_called_with(EXIT_ERROR)

    # Check shutdown callback errors
    startup_callback.side_effect = None
    shutdown_callback.side_effect = Exception
    result = cli.invoke(runner.run(), cli_args)
    # Running the component should succeed
    assert result.exit_code == 0
    # Check error exit
    exit.assert_called_with(EXIT_ERROR)
