import re
from pathlib import Path
from typing import Pattern, Any

def format_to_regex(format: str) -> Pattern[str]:
    """Convert a format-string-like template into a regex with named groups.

    Example
    -------
    "atom_id:{atom_id} / group_id={group_id}"
    → r"^atom_id:(?P<atom_id>.+?)\ / group_id=(?P<group_id>.+?)$"
    """
    parts: list[str] = []
    i = 0
    while i < len(format):
        if format[i] == "{":
            j = format.index("}", i)
            field_name = format[i+1:j].strip()
            # grupo no codicioso con nombre
            parts.append(f"(?P<{field_name}>.+?)")
            i = j + 1
        else:
            parts.append(re.escape(format[i]))
            i += 1
    regex = "^" + "".join(parts) + "$"
    return re.compile(regex)


def atom_label_from_format(format: str, context: dict[str, Any]) -> str:
    """Render a string from a template like '{atom_id}-{atom_name}'."""
    return format.format(**context)

def parse_atom_label(format: str, atom_label: str) -> dict[str, str]:
    """Parse a string using the given template and return the captured fields."""
    pattern = format_to_regex(format)
    m = pattern.match(atom_label)
    if not m:
        raise ValueError(f"String {text!r} does not match template {template!r}")
    return m.groupdict()

def parse_list_of_atom_labels(format: str, list_of_atom_labels: list[str]) -> list[dict[str, str]]:
    """Parse many strings with the same template."""
    pattern = format_to_regex(format)
    results: list[dict[str, str]] = []
    for atom_label in list_of_atom_labels:
        m = pattern.match(atom_label)
        if not m:
            raise ValueError(f"String {text!r} does not match template {template!r}")
        results.append(m.groupdict())
    return results
