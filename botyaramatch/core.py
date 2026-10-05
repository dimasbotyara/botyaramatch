"""Public API of botyaramatch."""

from collections.abc import Callable, Iterable
from typing import Optional

from .algorithms import METHODS
from .normalize import normalize as _normalize
from .normalize import switch_layout


def _get_method(method: str) -> Callable[[str, str], float]:
    try:
        return METHODS[method]
    except KeyError:
        raise ValueError(
            f"Unknown method {method!r}. Available: {', '.join(sorted(METHODS))}"
        ) from None


def score(a: str, b: str, method: str = "levenshtein", normalize: bool = True) -> float:
    """Similarity between two strings as a float in [0.0, 1.0]."""
    func = _get_method(method)
    if normalize:
        a, b = _normalize(a), _normalize(b)
    return func(a, b)


def closest_n(
    query: str,
    choices: Iterable[str],
    n: int = 3,
    method: str = "levenshtein",
    threshold: float = 0.0,
    normalize: bool = True,
    layout_fix: bool = False,
) -> list[tuple[str, float]]:
    """Top-n closest matches as [(choice, score), ...], sorted descending.

    threshold  - drop candidates scoring below this value (0.0-1.0)
    layout_fix - also try the query in the opposite keyboard layout
                 ('ghbdtn' -> 'привет')
    """
    func = _get_method(method)
    prep: Callable[[str], str] = _normalize if normalize else (lambda s: s)

    queries = [prep(query)]
    if layout_fix:
        queries.append(prep(switch_layout(query)))

    scored: list[tuple[str, float]] = []
    for choice in choices:
        c = prep(choice)
        best = max(func(q, c) for q in queries)
        if best >= threshold:
            scored.append((choice, best))

    scored.sort(key=lambda pair: pair[1], reverse=True)  # stable sort
    return scored[:n]


def closest(
    query: str,
    choices: Iterable[str],
    default: Optional[str] = None,
    **kwargs: object,
) -> Optional[str]:
    """Return the closest match, or `default` if nothing passes the threshold."""
    result = closest_n(query, choices, n=1, **kwargs)  # type: ignore[arg-type]
    return result[0][0] if result else default
