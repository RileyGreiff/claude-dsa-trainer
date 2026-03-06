"""Text normalization helpers for answer comparison."""

import re


def normalize_text(text):
    """Lowercase and strip whitespace for general text comparison."""
    return text.strip().lower()


def normalize_code_fragment(code):
    """Collapse all whitespace to single spaces and strip, for code comparison."""
    return re.sub(r"\s+", " ", code.strip()).lower()


def normalize_complexity(text):
    """Normalize big-O notation: strip spaces inside parens, lowercase.

    Examples:
        'O( n log n )' -> 'o(nlogn)'
        'O(N^2)'       -> 'o(n^2)'
    """
    text = text.strip().lower()
    # Remove spaces inside parentheses
    text = re.sub(r"\s+", "", text)
    return text
