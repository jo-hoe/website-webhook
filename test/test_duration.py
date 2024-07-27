
from datetime import timedelta
from app.duration import parse_duration


def test_parse_duration():
    assert parse_duration("2ms") == timedelta(
        milliseconds=2), "parse_duration failed"
    assert parse_duration("4s") == timedelta(
        seconds=4), "parse_duration failed"
    assert parse_duration("8m") == timedelta(
        minutes=8), "parse_duration failed"
    assert parse_duration("16h") == timedelta(
        hours=16), "parse_duration failed"
    assert parse_duration("32d") == timedelta(
        days=32), "parse_duration failed"
