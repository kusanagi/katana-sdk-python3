class Component(object):
    """Base KATANA SDK component class."""

    def __init__(self):
        self._runner = None

    def run(self, callback):
        """Run SDK component.

        Callback must be a callable that receives a
        `katana.api.base.Api` argument.

        Calling this method checks command line arguments before
        component server starts.

        :param callback: Callable to handle requests.
        :type callback: A callable.

        """

        if not self._runner:
            # Child classes must create a component runner instance
            raise Exception('No component runner defined')

        self._runner.run(callback)
