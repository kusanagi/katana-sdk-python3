from ..utils import EMPTY


class Property(object):
    """User land property class definition."""

    def __init__(self, name, value=EMPTY):
        self.name = name
        self.value = value

    def is_empty(self):
        return self.value == EMPTY
