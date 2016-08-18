from ..process import ComponentProcess

from .worker import MiddlewareWorker


class MiddlewareProcess(ComponentProcess):
    """Middleware child process class."""

    worker_factory = MiddlewareWorker
