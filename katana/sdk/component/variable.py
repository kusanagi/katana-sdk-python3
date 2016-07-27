from ..utils import EMPTY


class Variable(object):
    """Variable class definition."""

    def __init__(self, name, value=EMPTY):
        self.name = name
        self.value = value

    def is_empty(self):
        return self.value == EMPTY
