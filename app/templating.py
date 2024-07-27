import re


PLACEHOLDER_START = "<<"
PLACEHOLDER_END = ">>"

def template(key: str, value: str, replace_with: str) -> str:
    cleaned_value = re.sub(f"{PLACEHOLDER_START}\\s", PLACEHOLDER_START, value)
    cleaned_value = re.sub(f"\\s{PLACEHOLDER_END}", PLACEHOLDER_END, cleaned_value)

    return cleaned_value.replace(f"{PLACEHOLDER_START}{key}{PLACEHOLDER_END}", replace_with)
