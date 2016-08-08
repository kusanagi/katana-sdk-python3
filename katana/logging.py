import logging

from datetime import datetime


class KatanaFormatter(logging.Formatter):
    """Default KATANA logging formatter."""

    def formatTime(self, record, *args, **kwargs):
        return datetime.fromtimestamp(record.created).isoformat()[:-3]


def setup_katana_logging(level=logging.INFO):
    """Initialize logging defaults for KATANA.

    :param level: Logging level. Default: INFO.

    """

    format = "%(asctime)sZ [%(levelname)s] %(message)s"

    # Setup root logger
    if not logging.root.handlers:
        logging.basicConfig(level=level)
        logging.root.setLevel(level)
        logging.root.handlers[0].setFormatter(
            KatanaFormatter(format),
            )

    # Setup katana logger
    logger = logging.getLogger('katana')
    logger.setLevel(level)
