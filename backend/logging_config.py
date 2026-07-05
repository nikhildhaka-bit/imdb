import logging
import sys

from config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # httpx logs every outgoing request at INFO — too noisy once our own code is at INFO too.
    logging.getLogger("httpx").setLevel(logging.WARNING)
