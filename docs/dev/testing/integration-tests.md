# Integration Tests

Integration tests verify that multiple components work correctly together with
realistic inputs and minimal mocking.

## Status

Integration tests are not currently committed in this template. This page defines
how to add them when your project grows.

## What Integration Tests Should Cover

- Interaction between parser, validation, and execution layers
- I/O boundaries (filesystem, CLI, serialization formats)
- End-to-end behavior for a user-level workflow

## When to Write an Integration Test

Write an integration test when:

- A change spans multiple modules and cannot be trusted from unit tests alone
- A regression happened at component boundaries
- You need confidence in a real workflow, not just a pure function

Do not write integration tests for logic that can be covered by unit tests. If you can test it with a synthetic tensor, do that instead.

## Markers

If integration tests become slow or require special local setup, use markers and
document them in `tests/conftest.py` and [Optional Test Markers](optional-markers.md).

## Intended Structure

```python
# tests/integration/test_cli_flow.py

@pytest.fixture(scope="module")
def sample_project(tmp_path_factory):
    root = tmp_path_factory.mktemp("project")
    (root / "input.txt").write_text("hello\n")
    return root


def test_cli_generates_output(sample_project):
    result = run_cli(sample_project)
    assert result.exit_code == 0
    assert (sample_project / "output.txt").is_file()
```

Use module-scoped fixtures when setup is expensive but deterministic.

## Checkpoint Path

Run integration tests with the regular test command unless you introduce separate
markers or split commands.

```shell
uv run pytest --cov --cov-report=term-missing --cov-fail-under=80
```

## Related

- [Testing Overview](index.md)
- [Optional Test Markers](optional-markers.md)
- [Unit Tests](unit-tests.md)
