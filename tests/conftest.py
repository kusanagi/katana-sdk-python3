import io
import json
import logging
import os

import click.testing
import pytest

from katana.logging import setup_katana_logging
from katana.schema import SchemaRegistry


@pytest.fixture(scope='session')
def data_path(request):
    """
    Fixture to add full path to test data directory.

    """

    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='session')
def read_json(data_path):
    """
    Fixture to add JSON loading support to tests.

    """

    def deserialize(name):
        if not name[-4:] == 'json':
            name += '.json'

        with open(os.path.join(data_path, name), 'r') as file:
            return json.load(file)

    return deserialize


@pytest.fixture(scope='function')
def registry(request):
    """
    Fixture to add schema registry support to tests.

    """

    def cleanup():
        SchemaRegistry.instance = None

    request.addfinalizer(cleanup)
    return SchemaRegistry()


@pytest.fixture(scope='function')
def cli(request):
    """
    Fixture to add CLI runner support to tests.

    """

    def cleanup():
        del os.environ['TESTING']

    request.addfinalizer(cleanup)
    os.environ['TESTING'] = '1'
    return click.testing.CliRunner()


@pytest.fixture(scope='function')
def logs(request, mocker):
    """
    Fixture to add logging output support to tests.

    """

    output = io.StringIO()

    def cleanup():
        # Remove root handlers to release sys.stdout
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

        # Cleanup katana logger handlers too
        logging.getLogger('katana').handlers = []
        logging.getLogger('katana.api').handlers = []

        output.close()

    request.addfinalizer(cleanup)
    mocker.patch('katana.logging.get_output_buffer', return_value=output)
    setup_katana_logging()
    return output
