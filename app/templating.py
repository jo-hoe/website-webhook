import re


start = "<<"
end = ">>"

def template(key: str, value: str, replace_with: str) -> str:
    cleaned_value = re.sub(f"{start}\s", start, value)
    cleaned_value = re.sub(f"\s{end}", end, cleaned_value)

    return cleaned_value.replace(f"{start}{key}{end}", replace_with)
