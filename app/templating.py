import re
import ast
from typing import Any


PLACEHOLDER_START = "<<"
PLACEHOLDER_END = ">>"

# Matches strings that look like Python literals (lists, dicts, numbers, booleans, None, or quoted strings)
_literal_regex = re.compile(
    r"^\s*(\[.*\]|\{.*\}|'[^']*'|\"[^\"]*\"|\d+(\.\d+)?|True|False|None)\s*$", re.DOTALL)


def template(key: str, value: Any, replace_with: str) -> Any:
    """
    Recursively replaces all occurrences of the placeholder <<key>> in the given value with replace_with.
    If the result looks like a Python literal (e.g., number, list, dict), it tries to convert it to the actual type.
    Works for strings and lists of strings. Other types are returned unchanged.
    """
    # If value is a list, process each element recursively
    if isinstance(value, list):
        return [template(key, v, replace_with) for v in value]

    # Only process strings; return other types unchanged
    if not isinstance(value, str):
        return value

    # Build a regex to match the placeholder with optional whitespace
    placeholder_pattern = re.compile(
        rf"{re.escape(PLACEHOLDER_START)}\s*{re.escape(key)}\s*{re.escape(PLACEHOLDER_END)}"
    )

    # Replace all occurrences of the placeholder in the string
    replaced_value = placeholder_pattern.sub(replace_with, value)

    # If the replaced value looks like a Python literal, try to parse it
    if _literal_regex.match(replaced_value) and replaced_value.strip():
        try:
            return ast.literal_eval(replaced_value)
        except Exception:
            # If parsing fails, just return the string
            pass
    return replaced_value
