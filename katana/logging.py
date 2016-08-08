import logging

from datetime import datetime


class KatanaFormatter(logging.Formatter):
    """Default KATANA logging formatter."""

    log_template = "{timestamp}Z [{level}] {message}"

    def format(self, record):
        return self.log_template.format(
            level=record.levelname,
            message=(record.msg % record.args),
            timestamp=datetime.fromtimestamp(record.created).isoformat()[:-3],
            )


def setup_katana_logging(level=logging.INFO):
    """Initialize logging defaults for KATANA.

    :param level: Logging level. Default: INFO.

    """

    logger = logging.getLogger('katana')
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(KatanaFormatter())
        logger.addHandler(handler)
