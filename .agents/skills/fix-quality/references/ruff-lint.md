# ruff lint

Run `uv run ruff check --fix` to auto-apply fixable violations.

Then run `uv run ruff check` to see what remains. Remaining violations
need manual fixes - do not suppress with `# noqa` unless the rule is
genuinely inapplicable and you can explain why in a comment.

`E501` (line too long) is ignored per `ruff.toml` - do not add line breaks
purely to satisfy it.
