
from app.templating import template


def test_templating_positive():
    assert template("key", "this is a <<key>>", "test") == "this is a test"

def test_templating_with_whitespaces():
    assert template("key", "this is a << key >>", "test") == "this is a test"

def test_templating_with_array():
    assert template("key", '["<<key>>"]', "test") == ["test"]

def test_templating_with_array_input():
    assert template("key", ["<<key>>"], "test") == ["test"]
