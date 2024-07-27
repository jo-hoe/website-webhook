
from datetime import timedelta

import pytest
from app.duration import parse_duration


def test_parse_duration():
    assert parse_duration("4s") == timedelta(
        seconds=4), "parse_duration failed"
    assert parse_duration("8m") == timedelta(
        minutes=8), "parse_duration failed"
    assert parse_duration("16h") == timedelta(
        hours=16), "parse_duration failed"
    assert parse_duration("32d") == timedelta(
        days=32), "parse_duration failed"


def test_parse_duration_error():
    with pytest.raises(ValueError):
        parse_duration("2ms")
