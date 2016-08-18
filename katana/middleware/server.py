from ..server import ComponentServer

from .process import MiddlewareProcess


class MiddlewareServer(ComponentServer):
    """Server class for middleware component."""

    process_factory = MiddlewareProcess
