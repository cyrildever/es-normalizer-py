"""
Contact data normalization adapted from the Empreinte Sociométrique's normalizers, the Python port of es-normalizer

Every normalizer takes a string and returns the normalized string, or `None` when nothing usable is left.
"""

import re
import unicodedata
from typing import Callable, Optional

from .dictionary import Dictionary, address_dictionary, first_name_dictionary, get_set, title_dictionary

Normalizer = Callable[[str], Optional[str]]


def normalize(data: str, normalizer: Normalizer) -> Optional[str]:
    return normalizer(data)


def uniformize(data: str) -> Optional[str]:
    """
    Upper-cases the passed string without its accents, any run of other characters than letters, digits and dashes becoming a single space
    """
    # The compatibility decomposition spells out superscripts and typographic ligatures, eg. `1ᵉʳ` or `ﬁ`; `º` and `№` would become an `o`
    lowered = data.strip().lower().replace("º", "°").replace("№", "n°")
    normalized = "".join(c for c in unicodedata.normalize("NFKD", lowered) if not "\u0300" <= c <= "\u036f")
    if normalized == "":
        return None
    uniformized = normalized.replace("ß", "ss").replace("ø", "o").replace("œ", "oe").replace("æ", "ae")
    uniformized = re.sub(r"[^a-zA-Z0-9-]+", "-", uniformized)
    uniformized = re.sub(r"-+", "-", uniformized).replace("-", " ").strip().upper()
    return uniformized or None


def Any(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer to use for any kind of data when no specific normalizer exists
    """
    return uniformize(data)


def AddressLine(transform_title: bool = False) -> Normalizer:  # noqa: N802
    """
    Normalizer of an address line, eg. `8, rue Henner` becomes `8 RUE HENNER`; with `transform_title`, a French address
    line 1 gets its title coded, eg. `Monsieur Cyril Dever` becomes `1 CYRIL DEVER`
    """

    def normalizer(data: str) -> Optional[str]:
        uniformized = uniformize(data)
        if uniformized is None:
            return None
        return (title_dictionary if transform_title else address_dictionary).translate_text(uniformized)

    return normalizer


_AL6 = re.compile(r"^((0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[1-8]|98[46-9])([0-9]{3}))(.*)$")


def AddressLine6(use_department_france: bool = True) -> Normalizer:  # noqa: N802
    """
    Normalizer of the French address line 6, the département inserted between the postal code and the town, eg. `75009 75 PARIS`
    """

    def normalizer(data: str) -> Optional[str]:
        line = AddressLine(False)(data)
        if line is None:
            return None
        matches = _AL6.match(line)
        if not matches or not matches.group(1):
            return None
        cp, dpt, city = matches.group(1), matches.group(2), matches.group(4)
        if city.strip().startswith(dpt):
            parts = [cp, city.strip()] if use_department_france else [cp, city.replace(dpt, "", 1).strip()]
        else:
            parts = [cp, dpt, city.strip()] if use_department_france else [cp, city.strip()]
        return " ".join(parts).strip()

    return normalizer


def City(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a town's name, its CEDEX mention removed
    """
    uniformized = uniformize(data)
    if uniformized is None:
        return None
    found = re.sub(r"CDX(\s+[0-9]+)*", "", address_dictionary.translate_text(uniformized), count=1)
    return re.sub(r"\s+", " ", found).strip()


_CP = re.compile(r"^((0[1-9][0-9]|[1-8][0-9]{2})|(9[0-5][0-9])|(2[AB][0-9])|(97[1-6]))[0-9]{2}$")
_CORSE = re.compile(r"^2[AB][0-9]{3}$")


def CodePostalFrance(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a French postal code, a Corsican one written with its département (`2A165`) becoming `20165`
    """
    uniformized = uniformize(data)
    if uniformized is None:
        return None
    words = re.split(r"\s", uniformized)
    candidate = words[0] if len(words) > 1 else uniformized
    if not _CP.search(candidate):
        return None
    return re.sub(r"[AB]", "0", candidate, count=1) if _CORSE.search(candidate) else candidate


_DPT = re.compile(r"^(0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[1-8]|98[46-9])([0-9]*)$")


def DepartementFrance(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer extracting the French département out of a postal code, eg. `2A` out of `20167`
    """
    uniformized = uniformize(data)
    if not uniformized:
        return None
    matches = _DPT.match(uniformized)
    if not matches or not matches.group(1):
        return None
    dpt = matches.group(1)
    if dpt != "20":
        return dpt
    cp = CodePostalFrance(data)
    if cp is None:
        return None
    return "2A" if 19999 < int(cp) < 20200 else "2B"


_EMAIL = re.compile(
    r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f]))"
    r"@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[a-z]{2,}[a-z0-9-]*|([a-z][a-z0-9-]+))|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.?){4})$"
)


def Email(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer validating an e-mail address and lower-casing it
    """
    processed = data.strip().lower()
    if len(processed) > 255 or not _EMAIL.search(processed):
        return None
    return processed


def FirstName(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a first name, through a French dictionary of first names, eg. `J Louis` becomes `JEAN LOUIS`
    """
    uniformized = uniformize(data)
    return None if uniformized is None else first_name_dictionary.translate_word(uniformized)


_MOBILE = re.compile(r"^(((00)?(33))|0)?([0]?)([0-9])([0-9]{2})([0-9]{3})([0-9]{3})$")


def Mobile(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a French mobile phone number in the international format, eg. `+33 (0) 623 456 789`
    """
    uniformized = uniformize(data)
    if uniformized is None:
        return None
    m = _MOBILE.match(re.sub(r"\s", "", uniformized))
    if not m:
        return None
    if not (m.group(7) and m.group(8) and m.group(9)) or (m.group(7) + m.group(8) + m.group(9)).endswith("00000000"):
        return None
    if not ((m.group(6) and m.group(6) == "6") or m.group(6) == "7"):
        return None
    international = f"+{m.group(4)}" if m.group(4) else "+33"
    prefix = f"({m.group(5)})" if m.group(5) else "(0)"
    return " ".join([international, prefix, m.group(6) + m.group(7), m.group(8), m.group(9)])


_PHONE = re.compile(r"^(((00)?(33)|0?(262)|0?(590)|0?(594)|0?(596))([^1-9]*)|0)?([^0-9]*)([0-9]{3})([0-9]{3})([0-9]{3})$")


def PhoneNumber(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a French phone or fax number in the international format, eg. `+33 (0) 123 456 789`
    """
    uniformized = uniformize(data)
    if uniformized is None:
        return None
    m = _PHONE.match(re.sub(r"\s", "", uniformized))
    if not m:
        return None
    if not (m.group(11) and m.group(12) and m.group(13)) or (m.group(11) + m.group(12) + m.group(13)).endswith("00000000"):
        return None
    international = f"+{m.group(4)}" if m.group(4) else "+33"
    prefix = f"({m.group(9)})" if m.group(9) else "(0)"
    return " ".join([international, prefix, m.group(11), m.group(12), m.group(13)])


_STREET_NUMBER = re.compile(r"^([0-9]*)\s*(.*)$")


def StreetNumber(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a street number, eg. `1bis` or `1 bis` becomes `1B`
    """
    m = _STREET_NUMBER.match(data.strip())
    if not m:
        return None
    if not m.group(2):
        return m.group(1)
    uniformized = uniformize(m.group(2))
    if uniformized is None:
        return None
    return m.group(1) + address_dictionary.translate_text(uniformized).split(" ")[0]


_CODE_F, _CODE_M, _CODE_U = "2", "1", "0"


def Title(data: str) -> Optional[str]:  # noqa: N802
    """
    Normalizer of a title into a code: 1 for gentlemen, 2 for ladies, 0 when undefined or unknown
    """
    translated = uniformize(data)
    if translated is None:
        return None
    if translated in ("H", "M"):
        return _CODE_M
    if translated == "F":
        return _CODE_F
    if translated == "U":
        return _CODE_U
    found = re.findall(r"[0-9]+", title_dictionary.translate_text(translated))
    if not found:
        return None
    return found[0] if len(found) == 1 else _CODE_U


from .date_of_birth import FRENCH_DATE, ISO_DATE, DateOfBirth, Milliseconds, Timestamp  # noqa: E402

__all__ = [
    "Dictionary", "get_set", "normalize", "uniformize", "Any", "AddressLine", "AddressLine6", "City", "CodePostalFrance",
    "DateOfBirth", "DepartementFrance", "Email", "FirstName", "Mobile", "PhoneNumber", "StreetNumber", "Title",
    "FRENCH_DATE", "ISO_DATE", "Timestamp", "Milliseconds",
]
