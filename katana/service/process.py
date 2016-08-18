from ..process import ComponentProcess

from .worker import ServiceWorker


class ServiceProcess(ComponentProcess):
    """Service child process class."""

    worker_factory = ServiceWorker
