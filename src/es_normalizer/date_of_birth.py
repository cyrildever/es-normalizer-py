"""
The date of birth normalizer, which reads and writes dates the way moment.js does in its forgiving mode, as es-normalizer relies on it
"""

import calendar
import re
from datetime import date, datetime
from typing import Callable, Optional

FRENCH_DATE = "DD/MM/YYYY"
ISO_DATE = "YYYYMMDD"
Timestamp = "timestamp"
Milliseconds = "timestamp_millis"

_SEPARATORS = re.compile(r"[-:/\s]+")
_TOKENS = re.compile(r"YYYY|YY|MMMM|MMM|MM|M|DD|D|HH|H|SS|S")
_MONTHS = [calendar.month_name[i] for i in range(1, 13)]
_SHORT_MONTHS = [calendar.month_abbr[i] for i in range(1, 13)]
_MONTH_NAME = re.compile("|".join(_MONTHS + _SHORT_MONTHS), re.IGNORECASE)
# What each token matches, searched anywhere in what is left of the input
_PARSE = {
    "YYYY": re.compile(r"\d{1,4}"),
    "YY": re.compile(r"\d\d?"),
    "MMMM": _MONTH_NAME,
    "MMM": _MONTH_NAME,
    "MM": re.compile(r"\d\d?"),
    "M": re.compile(r"\d\d?"),
    "DD": re.compile(r"\d\d?"),
    "D": re.compile(r"\d\d?"),
    "HH": re.compile(r"\d\d?"),
    "H": re.compile(r"\d\d?"),
    "SS": re.compile(r"\d+"),
    "S": re.compile(r"\d+"),
}


def _month_of(name: str) -> int:
    name = name.lower()
    for i, (full, short) in enumerate(zip(_MONTHS, _SHORT_MONTHS), start=1):
        if name == full.lower() or name == short.lower():
            return i
    return 0


def _two_digit_year(value: str) -> int:
    return int(value) + (1900 if int(value) > 68 else 2000)


def _parse(data: str, fmt: str) -> Optional[date]:
    year, month, day = date.today().year, 1, 1
    rest = data
    parsed = False
    for token in _TOKENS.findall(fmt):
        found = _PARSE[token].search(rest)
        if not found:
            continue
        rest = rest[found.end():]
        parsed = True
        value = found.group(0)
        if token == "YYYY":
            # As moment.js: a year of two digits is read as one of `YY`
            year = _two_digit_year(value) if len(value) == 2 else int(value)
        elif token == "YY":
            year = _two_digit_year(value)
        elif token in ("MMMM", "MMM"):
            month = _month_of(value)
        elif token in ("MM", "M"):
            month = int(value)
        elif token in ("DD", "D"):
            day = int(value)
    if not parsed:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _format(d: date, fmt: str) -> str:
    def token(m: re.Match) -> str:
        t = m.group(0)
        return {
            "YYYY": f"{d.year:04d}",
            "YY": f"{d.year % 100:02d}",
            "MMMM": _MONTHS[d.month - 1],
            "MMM": _SHORT_MONTHS[d.month - 1],
            "MM": f"{d.month:02d}",
            "M": str(d.month),
            "DD": f"{d.day:02d}",
            "D": str(d.day),
            "HH": "00",
            "H": "0",
            "SS": "00",
            "S": "0",
        }[t]

    return _TOKENS.sub(token, fmt)


def _leading_int(data: str) -> Optional[int]:
    # As JavaScript's `parseInt`: the leading digits, sign included
    found = re.match(r"\s*([+-]?\d+)", data)
    return int(found.group(1)) if found else None


def DateOfBirth(input_format: str = None, output_format: str = None) -> Callable[[str], Optional[str]]:  # noqa: N802
    """
    Normalizer of a date of birth, read in the input format (ISO by default) and written in the output one (French by
    default), eg. `24/04/2010` read as `DD/MM/YYYY` and written as `ISO_DATE` becomes `20100424`
    """
    inp = ISO_DATE if not input_format else input_format
    out = FRENCH_DATE if not output_format else output_format

    def normalizer(data: str) -> Optional[str]:
        if inp.lower() in (Timestamp, Milliseconds):
            value = _leading_int(data)
            if value is None:
                return None
            d = datetime.fromtimestamp(value if inp.lower() == Timestamp else value / 1000).date()
        else:
            d = _parse(data, _SEPARATORS.sub("-", inp).upper())
        if d is None:
            return None
        written = _format(d, _SEPARATORS.sub("-", out).upper())
        separator = _SEPARATORS.search(out)
        return written if separator is None else written.replace("-", separator.group(0))

    return normalizer
