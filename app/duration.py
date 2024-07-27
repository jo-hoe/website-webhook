

from datetime import timedelta
import re


def parse_duration(duration_string: str) -> timedelta:
    # Define the regex pattern for matching duration components
    # This pattern now matches the entire string to ensure no invalid characters
    pattern = r'^(\d+[smhd])+$'

    if not re.match(pattern, duration_string):
        raise ValueError(f"Invalid duration format: {duration_string}")

    # Pattern for individual components
    component_pattern = r'(\d+)([smhd])'

    # Define a mapping of units to their timedelta arguments
    unit_mapping = {
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days'
    }

    # Find all matches in the duration string
    matches = re.findall(component_pattern, duration_string)

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
