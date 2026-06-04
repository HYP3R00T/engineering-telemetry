# Property-Based Tests

Property-based tests verify that a function satisfies a mathematical invariant across many randomly generated inputs, rather than a single fixed example. This catches edge cases that hand-written tests miss.

This project uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing.

## When to Use Property-Based Tests

Property-based tests are well suited for:

- Mathematical invariants in utility functions (range limits, monotonicity, idempotence)
- Shape contracts that must hold for any valid input size
- Functions where the correct output can be described as a rule rather than a specific value

They are not suited for:

- Tests that require a specific expected output value
- Tests that depend on external services or heavy runtime setup

## Installing Hypothesis

Hypothesis is not included by default. Install it when you start adding property tests:

```bash
uv add --dev hypothesis
```

```toml
[dependency-groups]
dev = [
  "pytest>=9.0.2",
  "pytest-cov>=7.0.0",
  "hypothesis>=6.151.9",
]
```

## Examples

### Output range constraint

`clamp_unit_interval` must always return values in `[0, 1]` for any numeric input.

```python
from hypothesis import given
from hypothesis import strategies as st
from project.math_utils import clamp_unit_interval

@given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_clamped_to_unit_interval(value: float) -> None:
  result = clamp_unit_interval(value)
  assert 0.0 <= result <= 1.0
```

### Shape preservation

Applying a normalizer twice should produce the same output as once.

```python
@given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
def test_normalizer_is_idempotent(value: float) -> None:
  once = clamp_unit_interval(value)
  twice = clamp_unit_interval(once)
  assert once == twice
```

### Monotonicity

A larger input must not produce a smaller clamped output.

```python
@given(
  st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
  st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
)
def test_monotone(a: float, b: float) -> None:
  x, y = sorted((a, b))
  assert clamp_unit_interval(x) <= clamp_unit_interval(y)
```

## File Layout

Place property tests under `tests/property/`, mirroring the source tree by module group.

```text
tests/property/
  utils/
    test_math_utils_properties.py
  parsing/
    test_parser_properties.py
```

## Suppressing Hypothesis Output in CI

Hypothesis prints a summary when it finds a failing example. This is useful locally but noisy in CI. Add a `settings` profile to `conftest.py` if needed:

```python
from hypothesis import settings
settings.register_profile("ci", max_examples=50)
settings.load_profile("ci")
```

## Related

- [Testing Overview](index.md)
- [Unit Tests](unit-tests.md)
