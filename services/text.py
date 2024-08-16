import re

def convert_to_superscript(text, sources):
    # Superscript digits in HTML
    superscript_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

    # Regex pattern to find lists of numbers within square brackets
    pattern = re.compile(r'\[(\d+(?:,\s*\d+)*)\]')

    def replace_with_superscript(match):
        # Extract the matched number list
        numbers = match.group(1).translate(superscript_map)
        
        # Get the corresponding source URL for the current match
        if replace_with_superscript.counter - 1 < len(sources):
            url = sources[replace_with_superscript.counter - 1]
            replace_with_superscript.counter += 1
        else:
            url = '#'

        # Return the clickable superscript
        return f"<a href='{url}'><sup>{numbers}</sup></a>"

    # Initialize a counter to track the number of matches
    replace_with_superscript.counter = 1

    # Substitute all occurrences in the text
    return pattern.sub(replace_with_superscript, text)
