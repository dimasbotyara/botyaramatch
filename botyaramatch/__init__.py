"""botyaramatch: find the closest matching string. Made by dimasbotyara 😎"""

from .algorithms import HAS_RAPIDFUZZ
from .core import closest, closest_n, score
from .normalize import normalize, switch_layout

__version__ = "0.1.0"
__all__ = [
    "HAS_RAPIDFUZZ",
    "closest",
    "closest_n",
    "normalize",
    "score",
    "switch_layout",
]
