"""String similarity algorithms. All return a float in the range [0.0, 1.0].

If rapidfuzz is installed, Levenshtein and Jaro-Winkler come from it (faster).
Otherwise a pure-Python fallback is used.
"""

from typing import Callable

try:  # optional acceleration
    from rapidfuzz.distance import JaroWinkler as _RFJaroWinkler
    from rapidfuzz.distance import Levenshtein as _RFLevenshtein

    HAS_RAPIDFUZZ = True
except ImportError:  # pragma: no cover - depends on the environment
    HAS_RAPIDFUZZ = False


def _levenshtein_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def levenshtein(a: str, b: str) -> float:
    """1 - (edit distance / length of the longer string)."""
    if HAS_RAPIDFUZZ:
        return float(_RFLevenshtein.normalized_similarity(a, b))
    if not a and not b:
        return 1.0
    return 1.0 - _levenshtein_distance(a, b) / max(len(a), len(b))


def _jaro(a: str, b: str) -> float:
    if a == b:
        return 1.0
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    window = max(max(la, lb) // 2 - 1, 0)
    a_hit, b_hit = [False] * la, [False] * lb
    matches = 0
    for i, ca in enumerate(a):
        for j in range(max(0, i - window), min(i + window + 1, lb)):
            if not b_hit[j] and b[j] == ca:
                a_hit[i] = b_hit[j] = True
                matches += 1
                break
    if not matches:
        return 0.0
    transpositions = k = 0
    for i in range(la):
        if a_hit[i]:
            while not b_hit[k]:
                k += 1
            transpositions += a[i] != b[k]
            k += 1
    transpositions //= 2
    return (matches / la + matches / lb + (matches - transpositions) / matches) / 3


def jaro_winkler(a: str, b: str) -> float:
    """Jaro-Winkler: rewards a matching prefix. Great for names and short words."""
    if HAS_RAPIDFUZZ:
        return float(_RFJaroWinkler.similarity(a, b))
    jaro = _jaro(a, b)
    if jaro <= 0.7:
        return jaro
    prefix = 0
    for ca, cb in zip(a[:4], b[:4]):
        if ca != cb:
            break
        prefix += 1
    return jaro + prefix * 0.1 * (1.0 - jaro)


def _trigrams(s: str) -> set[str]:
    s = f"  {s} "
    return {s[i : i + 3] for i in range(len(s) - 2)}


def trigram(a: str, b: str) -> float:
    """Dice coefficient over character trigrams. Good for long strings and
    word reordering.
    """
    if a == b:
        return 1.0
    ta, tb = _trigrams(a), _trigrams(b)
    return 2 * len(ta & tb) / (len(ta) + len(tb))


METHODS: dict[str, Callable[[str, str], float]] = {
    "levenshtein": levenshtein,
    "jaro": jaro_winkler,
    "trigram": trigram,
}
