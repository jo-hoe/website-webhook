

from datetime import timedelta
import re


def parse_duration(duration_string: str) -> timedelta:
    # Define the regex pattern for matching duration components
    pattern = r'(\d+)(ms|s|m|h|d)'

    # Define a mapping of units to their timedelta arguments
    unit_mapping = {
        'ms': 'milliseconds',
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days'
    }

    # Find all matches in the duration string
    matches = re.findall(pattern, duration_string)

    # Initialize a timedelta object
    duration = timedelta()

    # Process each match
    for value, unit in matches:
        # Convert value to int and get the corresponding timedelta argument
        value = int(value)
        delta_arg = unit_mapping.get(unit)

        if delta_arg:
            # Add to the duration
            duration += timedelta(**{delta_arg: value})
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    return duration
