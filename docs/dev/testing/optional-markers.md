# Optional Test Markers

Some tests are slower or require extra local setup. Use optional markers so the
default test run stays fast and reliable.

## Markers

| Marker | Purpose | How to run |
|---|---|---|
| `slow` | Longer-running scenarios | `uv run pytest -m slow` |
| `external` | Depends on optional external service setup | `uv run pytest -m external` |

Unmarked tests should pass in a normal local and CI environment.

## Marker Configuration

Register markers in `pyproject.toml` under pytest options.

```toml
[tool.pytest.ini_options]
markers = [
  "slow: long-running tests",
  "external: tests requiring optional external setup",
]
```

## Applying a Marker

Apply markers at class or function scope.

```python
import pytest


@pytest.mark.slow
class TestLargeWorkflow:
    def test_end_to_end(self): ...


@pytest.mark.external
def test_optional_service_contract(): ...
```

## Coverage Guidance

Keep coverage exclusions minimal and explicit. Do not exclude code to avoid writing
tests. If a branch is hard to test, explain why in code review and add focused
coverage where practical.

## Coverage Threshold

Use the repository standard command:

```bash
uv run pytest --cov --cov-report=term-missing --cov-fail-under=80
```

## Related

- [Testing Overview](index.md)
- [Integration Tests](integration-tests.md)
- [Unit Tests](unit-tests.md)
