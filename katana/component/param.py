import logging

from .. import json

LOG = logging.getLogger(__name__)

TYPE_CLASSES = {
    'boolean': bool,
    'integer': int,
    'float': float,
    'array': list,
    'object': dict,
    'string': str,
    }

TYPE_NULL = 'null'
TYPE_BOOLEAN = 'boolean'
TYPE_INTEGER = 'integer'
TYPE_FLOAT = 'float'
TYPE_ARRAY = 'array'
TYPE_OBJECT = 'object'
TYPE_STRING = 'string'


class Param(object):

    def __init__(self, location, name, **kwargs):
        self.__value = kwargs.get('value') or ''
        self.location = location
        self.name = name
        self.type = kwargs.get('datatype') or TYPE_STRING
        self.exists = kwargs.get('exists', False)

    @property
    def value(self):
        error_msg = 'Param "{}" value is not a {}'.format(self.name, self.type)
        try:
            value = self.__value
            if self.type == 'string':
                value = '"{}"'.format(value)

            value = json.deserialize(value)
        except:
            LOG.error('Param "%s" is not %s: %s', self.name, self.type, value)
            raise TypeError(error_msg)

        if not isinstance(value, TYPE_CLASSES[self.type]):
            raise TypeError(error_msg)

        return value

    @property
    def value_raw(self):
        return self.__value

    @classmethod
    def resolve_type(cls, value):
        """Converts native types to schema types.

        :param value: The value to analyze.
        :type value: mixed.

        :rtype: str.

        """

        if value is None:
            return TYPE_NULL

        value_class = value.__class__
        if value_class == bytes:
            return TYPE_STRING
        elif value_class in (tuple, set):
            return TYPE_ARRAY

        for type_name, cls in TYPE_CLASSES.items():
            if value_class == cls:
                return type_name

        return TYPE_OBJECT
