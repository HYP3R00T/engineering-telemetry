# Unit Tests

Unit tests verify a single function or class in isolation. They should use local,
synthetic inputs and avoid external dependencies.

## What to Unit Test

Unit tests are appropriate for:

- Pure functions with deterministic outputs
- Input validation and error handling
- Edge cases and boundary values
- Small local filesystem interactions using `tmp_path`

Unit tests are not appropriate for:

- Cross-module workflows spanning many layers
- Environment-dependent paths that need custom local setup
- Network calls or long-running jobs

## File Layout

Unit tests should mirror the source tree. Keep one test file per module when practical,
using `test_*.py` naming.

| Source module | Test file |
|---|---|
| `src/example/math_utils.py` | `tests/unit/test_math_utils.py` |
| `src/example/config.py` | `tests/unit/test_config.py` |
| `src/example/parser.py` | `tests/unit/test_parser.py` |

## Class Grouping

Group tests by the function or class they cover using a `Test` class. This keeps related tests together and makes failures easier to locate.

```python
class TestParser:
    def test_rejects_empty_input(self): ...
    def test_accepts_valid_input(self): ...
    def test_normalizes_whitespace(self): ...
```

## Synthetic Inputs

Create minimal, synthetic inputs instead of loading large fixtures.

```python
def parse_int(value: str) -> int:
    return int(value.strip())

def test_parse_int_trims_whitespace() -> None:
    assert parse_int(" 42 ") == 42
```

## Mocking Platform and Environment

Use `unittest.mock.patch` for external calls and `monkeypatch` for environment
variables.

```python
def test_env_var_overrides_default(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert load_mode() == "test"
```

## Error Handling Tests

Test that functions raise the right exception with a useful message when given invalid input. Use `pytest.raises` with a `match` pattern to assert on the message.

```python
def test_invalid_backend_raises(self):
    with pytest.raises(ValueError, match="invalid mode"):
        resolve_mode("bad-value")
```

## Filesystem Tests

Use pytest's built-in `tmp_path` fixture for tests that need real files on disk. It creates a temporary directory that is cleaned up after the test.

```python
def test_finds_single_pth(self, tmp_path: Path):
    (tmp_path / "config.toml").write_text("enabled = true\n")
    result = discover_config(tmp_path)
    assert result.name == "config.toml"
```

## Tolerance in Floating Point Assertions

Floating point values should use tolerant comparisons.

```python
assert abs(result - expected) < 1e-6
```

## Related

- [Testing Overview](index.md)
- [Optional Test Markers](optional-markers.md)
- [Property-Based Tests](property-tests.md)
