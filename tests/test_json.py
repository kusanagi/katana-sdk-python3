import datetime
import decimal

import pytest

from katana import json


def test_encoder():
    # Create a class that supports serialization
    class Serializable(object):
        def __serialize__(self):
            return {'__type__': 'object', 'value': 'OK'}

    cases = (
        (decimal.Decimal('123.321'),
         '123.321'),
        (datetime.date(2017, 1, 27),
         '2017-01-27'),
        (datetime.datetime(2017, 1, 27, 20, 12, 8, 952811),
         '2017-01-27T20:12:08.952811+00:00'),
        (b'value',
         'value'),
        (Serializable(),
         {'__type__': 'object', 'value': 'OK'}),
        )

    encoder = json.Encoder()

    for value, expected in cases:
        assert encoder.default(value) == expected

    # Unknown objects should raise an error
    with pytest.raises(TypeError):
        encoder.default(object())


def test_deserialize():
    cases = (
        ('"text"', 'text'),
        ('{"foo": "bar"}', {'foo': 'bar'}),
    )

    for value, expected in cases:
        assert json.deserialize(value) == expected


def test_serialize():
    cases = (
        ('text', b'"text"'),
        ({'foo': 'bar'}, b'{"foo":"bar"}'),
        ([1, 2, 3], b'[1,2,3]'),
    )

    # Check results without prettyfication
    for value, expected in cases:
        assert json.serialize(value) == expected


def test_serialize_pretty():
    cases = (
        ('text', b'"text"'),
        ({'foo': 'bar'}, b'{\n  "foo": "bar"\n}'),
        ([1, 2, 3], b'[\n  1,\n  2,\n  3\n]'),
    )

    # Check results with prettyfication
    for value, expected in cases:
        assert json.serialize(value, prettify=True) == expected
