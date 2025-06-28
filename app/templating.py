import re
import ast
from typing import Any


PLACEHOLDER_START = "<<"
PLACEHOLDER_END = ">>"

_literal_regex = re.compile(
    r"^\s*(\[.*\]|\{.*\}|'.*'|\".*\"|\d+(\.\d+)?|True|False|None)\s*$", re.DOTALL)


def template(key: str, value: Any, replace_with: str) -> Any:
    # Recursively process lists
    if isinstance(value, list):
        return [template(key, v, replace_with) for v in value]
    # Only process if value is a string
    if not isinstance(value, str):
        return value
    # Replace placeholders with or without whitespace
    pattern = re.compile(
        rf"{re.escape(PLACEHOLDER_START)}\s*{re.escape(key)}\s*{re.escape(PLACEHOLDER_END)}")
    replaced = pattern.sub(replace_with, value)
    # Only parse as literal if it looks like a literal and is not empty or whitespace
    if _literal_regex.match(replaced) and replaced.strip():
        try:
            return ast.literal_eval(replaced)
        except Exception:
            pass  # fallback to string if parsing fails
    return replaced
