from ..server import ComponentServer

from .process import ServiceProcess


class ServiceServer(ComponentServer):
    """Server class for service component."""

    process_factory = ServiceProcess
