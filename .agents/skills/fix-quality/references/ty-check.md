# ty check

Run `uv run ty check`. There is no auto-fix - all errors require manual
resolution.

Prefer fixing the root type issue over adding `# type: ignore`. If a
third-party library lacks stubs, that is the one acceptable use of ignore.

Add type annotations to all new functions. Do not widen types to `Any`
to silence errors.
