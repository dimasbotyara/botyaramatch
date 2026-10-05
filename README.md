# botyaramatch 😎

> Find the closest matching string. Fast, tiny, zero-dependency fuzzy matching
> for English and Russian text — with **ё/е normalization** and **keyboard
> layout fixing** built in.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero deps](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#)
[![Optional: rapidfuzz](https://img.shields.io/badge/optional-rapidfuzz-orange.svg)](#optional-acceleration-with-rapidfuzz)

**botyaramatch** is a small, dependency-free Python library for fuzzy string
matching. It ships three classic algorithms — **Levenshtein**, **Jaro-Winkler**
and **trigram (Dice coefficient)** — plus quality-of-life features that most
libraries forget about:

- 🇷🇺 **Russian-aware normalization** — `ё` → `е`, casefold, whitespace squashing.
- ⌨️ **Keyboard layout fixing** — turn `ghbdtn` into `привет` and `руддщ` into `hello`.
- 🎯 **Top-N results with a threshold** — get `[(choice, score), …]` sorted by similarity.
- ⚡ **Optional acceleration** with [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz)
  when it's installed — otherwise pure Python kicks in automatically.
- 📦 **Zero runtime dependencies**, one small package, ~200 lines of code.

Made with ❤️ by **dimasbotyara**.

---

## Table of contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [API reference](#api-reference)
  - [`score`](#score)
  - [`closest`](#closest)
  - [`closest_n`](#closest_n)
  - [`normalize`](#normalize)
  - [`switch_layout`](#switch_layout)
  - [`HAS_RAPIDFUZZ`](#has_rapidfuzz)
- [Algorithms](#algorithms)
  - [Levenshtein](#levenshtein)
  - [Jaro-Winkler](#jaro-winkler)
  - [Trigram (Dice)](#trigram-dice)
  - [Which one should I use?](#which-one-should-i-use)
- [Normalization & layout fixing](#normalization--layout-fixing)
- [Optional acceleration with rapidfuzz](#optional-acceleration-with-rapidfuzz)
- [Real-world examples](#real-world-examples)
- [Running the tests](#running-the-tests)
- [Project layout](#project-layout)
- [FAQ](#faq)
- [License](#license)

---

## Installation

### From source (editable install)

```bash
git clone https://github.com/dimasbotyara/botyaramatch.git
cd botyaramatch
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
pip install -e .
```

### With optional acceleration

```bash
pip install -e ".[fast]"
```

### From PyPI (once published)

```bash
pip install botyaramatch
# or with the fast extra:
pip install "botyaramatch[fast]"
```

> **Note on Arch Linux / CachyOS / PEP 668.** If `pip install -e .` fails with
> `error: externally-managed-environment`, you are on a system where the OS
> Python is protected. Just create a virtual environment first:
>
> ```bash
> python -m venv .venv
> source .venv/bin/activate
> pip install -e .
> ```
>
> Never use `--break-system-packages` on your main Python — it can break your
> system packages.

---

## Quick start

```python
from botyaramatch import closest, closest_n, score, switch_layout, normalize

# 1. Simple similarity score
score("kitten", "sitting")                      # 0.5714... (Levenshtein by default)
score("martha", "marhta", method="jaro")        # 0.9611... (Jaro-Winkler)
score("привет", "превет")                       # 0.8333... (typo in Russian)

# 2. Pick the single best match
closest("яблко", ["яблоко", "груша", "банан"])  # 'яблоко'
closest("pyton", ["java", "python", "ruby"])    # 'python'

# 3. Top-N with scores and a threshold
closest_n("pyton", ["java", "python", "ruby"], n=2)
# [('python', 0.8333...), ('java', 0.3333...)]

# 4. Fix the keyboard layout on the fly
closest("ghbdtn", ["привет", "пока"], layout_fix=True)   # 'привет'
closest("руддщ", ["hello", "world"], layout_fix=True)    # 'hello'

# 5. Normalize manually
normalize("  ЁЛКА   Большая ")    # 'елка большая'
switch_layout("ghbdtn")           # 'привет'
switch_layout("руддщ")            # 'hello'
```

---

## API reference

### `score`

```python
score(a: str, b: str, method: str = "levenshtein", normalize: bool = True) -> float
```

Return a similarity score between `a` and `b` in the range `[0.0, 1.0]`.
`1.0` means identical, `0.0` means nothing in common.

| Parameter   | Type   | Default          | Description |
|-------------|--------|------------------|-------------|
| `a`         | `str`  | —                | First string. |
| `b`         | `str`  | —                | Second string. |
| `method`    | `str`  | `"levenshtein"`  | One of `"levenshtein"`, `"jaro"`, `"trigram"`. |
| `normalize` | `bool` | `True`           | Apply [`normalize`](#normalize) to both strings first. |

Raises `ValueError` for an unknown `method`.

```python
score("abc", "abc")                # 1.0
score("abc", "")                   # 0.0
score("ёлка", "елка")              # 1.0  (ё/е normalization)
score("a", "b", method="nope")     # ValueError
```

---

### `closest`

```python
closest(
    query: str,
    choices: Iterable[str],
    default: Optional[str] = None,
    **kwargs,
) -> Optional[str]
```

Return the single most similar item from `choices`, or `default` if nothing
passes the `threshold`. Extra keyword arguments are forwarded to
[`closest_n`](#closest_n) (`n`, `method`, `threshold`, `normalize`, `layout_fix`).

```python
closest("яблко", ["яблоко", "груша", "банан"])           # 'яблоко'
closest("zzzzzz", ["яблоко", "груша"], threshold=0.8)    # None
closest("zzzzzz", ["яблоко", "груша"], threshold=0.8, default="?")  # '?'
```

---

### `closest_n`

```python
closest_n(
    query: str,
    choices: Iterable[str],
    n: int = 3,
    method: str = "levenshtein",
    threshold: float = 0.0,
    normalize: bool = True,
    layout_fix: bool = False,
) -> List[Tuple[str, float]]
```

Return up to `n` best matches as a list of `(choice, score)` tuples, sorted by
descending score. Ties keep their original order (stable sort).

| Parameter     | Type             | Default          | Description |
|---------------|------------------|------------------|-------------|
| `query`       | `str`            | —                | The string to match. |
| `choices`     | `Iterable[str]`  | —                | Candidates to compare against. |
| `n`           | `int`            | `3`              | How many results to return. |
| `method`      | `str`            | `"levenshtein"`  | Similarity algorithm. |
| `threshold`   | `float`          | `0.0`            | Drop candidates scoring below this. |
| `normalize`   | `bool`           | `True`           | Normalize both sides. |
| `layout_fix`  | `bool`           | `False`          | Also try `switch_layout(query)` and keep the best of the two. |

```python
closest_n("pyton", ["java", "python", "ruby"], n=2)
# [('python', 0.8333...), ('java', 0.3333...)]

closest_n("a", [])            # []
```

---

### `normalize`

```python
normalize(text: str) -> str
```

Casefold the string, replace `ё` with `е`, and collapse all whitespace runs
into single spaces (leading/trailing whitespace removed).

```python
normalize("  ЁЛКА   Большая ")   # 'елка большая'
normalize("Hello,\tWorld!\n")    # 'hello, world!'
```

---

### `switch_layout`

```python
switch_layout(text: str) -> str
```

Convert text typed in the wrong keyboard layout. The direction is detected
automatically from the character mix:

- Mostly Latin → transliterate to Russian: `'ghbdtn'` → `'привет'`
- Mostly Cyrillic → transliterate to Latin: `'руддщ'` → `'hello'`

Characters with no mapping are left untouched.

```python
switch_layout("ghbdtn")     # 'привет'
switch_layout("руддщ")      # 'hello'
switch_layout("Rfr dslf")   # 'Как вида'  (mixed-case folded to lower)
```

---

### `HAS_RAPIDFUZZ`

```python
from botyaramatch import HAS_RAPIDFUZZ
```

`True` if `rapidfuzz` was importable at load time, `False` otherwise. Useful
for logging or feature detection.

---

## Algorithms

All algorithms return a normalized score in `[0.0, 1.0]` and are exposed
through the `method` argument. They are also available directly from
`botyaramatch.algorithms` if you need them.

### Levenshtein

Edit-distance-based similarity:

```
score = 1 - (edit_distance / max(len(a), len(b)))
```

Great default. Intuitive, works well for typos and single-word correction.
Sensitive to length differences and word order.

```python
score("kitten", "sitting")          # 0.571428...
score("яблоко", "яблко")            # 0.833333...
```

### Jaro-Winkler

A Jaro similarity with a bonus for a matching prefix (up to 4 chars). Excellent
for **short strings and names**, where getting the first letters right matters.

```python
score("martha", "marhta", method="jaro")    # 0.9611...
score("DWAYNE", "DUANE", method="jaro")     # ~0.84
```

### Trigram (Dice)

Compares sets of character trigrams (with padding on both ends):

```
score = 2 * |A ∩ B| / (|A| + |B|)
```

Robust for **longer strings** and tolerant to word reordering, because it does
not care about positions.

```python
score("hello world", "world hello", method="trigram")   # high
```

### Which one should I use?

| Task                                          | Recommended method  |
|-----------------------------------------------|---------------------|
| Typos, one word vs. one word                  | `levenshtein`       |
| Human names, short labels                     | `jaro`              |
| Long descriptions, reordered words            | `trigram`           |
| Not sure                                      | `levenshtein`       |

You can always compare all three and take the max — the API makes this trivial.

---

## Normalization & layout fixing

Two problems make fuzzy matching on real-world input painful, and
`botyaramatch` solves both automatically when `normalize=True` (the default).

**1. Russian `ё` / `е` confusion.** Many people type `е` where `ё` is correct,
and vice versa. `normalize()` folds them, so `"ёлка"` and `"елка"` are treated
as identical.

**2. Wrong keyboard layout.** A user typing `привет` while the layout is set to
English produces `ghbdtn`. With `layout_fix=True`, `closest` and `closest_n`
transliterate the query and keep the best-scoring variant:

```python
closest("ghbdtn", ["привет", "пока"], layout_fix=True)   # 'привет'
closest("руддщ", ["hello", "world"], layout_fix=True)    # 'hello'
```

> Note: `layout_fix` only switches the **query** side. Choices are compared
> as-is (after `normalize`).

---

## Optional acceleration with rapidfuzz

If [`rapidfuzz`](https://github.com/rapidfuzz/RapidFuzz) is installed, the
Levenshtein and Jaro-Winkler implementations are transparently replaced by its
C++ versions — often 10-100× faster on large candidate lists.

```bash
pip install "botyaramatch[fast]"
```

No API changes. Check the flag if you want to know which path is active:

```python
from botyaramatch import HAS_RAPIDFUZZ
print(HAS_RAPIDFUZZ)   # True if rapidfuzz is available
```

The trigram method is always pure Python.

---

## Real-world examples

### Spell-check a single word

```python
from botyaramatch import closest

DICTIONARY = ["python", "pandas", "numpy", "pytest", "pip"]
print(closest("pyton", DICTIONARY))    # 'python'
```

### Suggest autocompletions from a list

```python
from botyaramatch import closest_n

cities = ["Moscow", "Munich", "Madrid", "Manchester", "Mumbai"]
for city, score_ in closest_n("manchstr", cities, n=3, threshold=0.4):
    print(f"{city:<12} {score_:.2f}")
# Manchester   0.67
# Munich       0.44
# Moscow       0.36
```

### Match user input to a fixed command set (with layout fixing)

```python
from botyaramatch import closest

COMMANDS = ["start", "stop", "status", "restart"]
cmd = closest("cnfylfhn", COMMANDS, layout_fix=True)   # 'start'? depends on layout
```

### Russian city names with typos and `ё`/`е` slips

```python
from botyaramatch import closest

CITIES = ["Королёв", "Кострома", "Краснодар", "Красноярск"]
print(closest("королев", CITIES))       # 'Королёв'
print(closest("краснадар", CITIES))     # 'Краснодар'
```

### Compare all three algorithms on the same pair

```python
from botyaramatch import score

a, b = "martha", "marhta"
for m in ("levenshtein", "jaro", "trigram"):
    print(f"{m:<12} {score(a, b, method=m):.4f}")
# levenshtein  0.6667
# jaro         0.9611
# trigram      0.0000  (short strings → few trigrams)
```

---

## Running the tests

The repository ships with a `unittest`-based test suite covering scoring,
normalization, layout fixing and the `closest`/`closest_n` API.

```bash
# after `pip install -e .` inside a virtualenv
python tests/test_botyaramatch.py
# or, if you have the package installed:
python -m unittest discover -s tests -v
```

Expected output:

```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.001s

OK
```

You can also run them with `pytest` if you prefer:

```bash
pip install pytest
pytest tests/ -v
```

---

## Project layout

```
botyaramatch/
├── botyaramatch/
│   ├── __init__.py        # public API re-exports + __version__
│   ├── algorithms.py      # levenshtein, jaro_winkler, trigram, METHODS
│   ├── core.py            # score, closest, closest_n
│   └── normalize.py       # normalize, switch_layout
├── tests/
│   └── test_botyaramatch.py
├── pyproject.toml
├── README.md
└── .gitignore
```

The public surface is intentionally tiny:

```python
from botyaramatch import (
    closest,        # best single match
    closest_n,      # top-N matches
    score,          # raw similarity
    normalize,      # ё→е, casefold, whitespace
    switch_layout,  # 'ghbdtn' → 'привет'
    HAS_RAPIDFUZZ,  # speed-up availability flag
)
```

---

## FAQ

**Why "botyaramatch"?**
Because `dimasbotyara` needed a matching library and nobody was going to name
it for him. 😎

**Does it work with non-Russian languages?**
Yes. Normalization is a no-op for languages without `ё`, and all three
algorithms are language-agnostic. Russian support is just a bonus.

**Can I use it in production with big candidate lists?**
Install the `fast` extra to get `rapidfuzz`. If you need top-K over a very
large corpus (millions of strings), consider an index-based solution — this
library is linear in the number of candidates per query.

**Does `layout_fix` handle uppercase?**
`switch_layout` casefolds the input. If you need case preservation, keep the
original string around and re-apply casing yourself.

**Is it thread-safe?**
Yes. All functions are pure and stateless.

**Python version?**
3.9 and newer. The code uses only the standard library.

---

## License

MIT © dimasbotyara

---

<p align="center">
  Made with ❤️, ☕ and a bit of ⌨️ by <b>dimasbotyara</b>.
</p>
