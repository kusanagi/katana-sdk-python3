import io
import logging
import os

import click.testing
import pytest

from katana.logging import setup_katana_logging


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
