"""Text normalization and keyboard layout fixing (EN <-> RU)."""

_EN = "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
_RU = "йцукенгшщзхъфывапролджэячсмитьбю.ё"

_EN_TO_RU = dict(zip(_EN, _RU))
_RU_TO_EN = dict(zip(_RU, _EN))


def normalize(text: str) -> str:
    """Casefold, ё -> е, collapse whitespace."""
    text = text.casefold().replace("ё", "е")
    return " ".join(text.split())


def _is_cyrillic(ch: str) -> bool:
    return "а" <= ch <= "я" or ch == "ё"


def switch_layout(text: str) -> str:
    """Flip the keyboard layout: 'ghbdtn' -> 'привет' and vice versa
    ('руддщ' -> 'hello').

    The direction is detected automatically from the dominant alphabet
    of the input.
    """
    lowered = text.casefold()
    cyr = sum(_is_cyrillic(c) for c in lowered)
    lat = sum("a" <= c <= "z" for c in lowered)
    table = _RU_TO_EN if cyr > lat else _EN_TO_RU
    return "".join(table.get(c, c) for c in lowered)
