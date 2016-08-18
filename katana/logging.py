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

    format = "%(asctime)sZ [%(levelname)s] [SDK] %(message)s"

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
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(KatanaFormatter(format))
        logger.addHandler(handler)
        logger.propagate = False
