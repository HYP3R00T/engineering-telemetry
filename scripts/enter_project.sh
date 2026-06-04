#!/usr/bin/env bash
set -eu

# Ensure Commitizen (cz) is available
if ! command -v cz >/dev/null 2>&1; then
    uv tool install commitizen
    command -v cz >/dev/null 2>&1 || { echo "Failed to install commitizen"; exit 1; }
fi

# Ensure prek is installed and hooks are set up idempotently
if command -v prek >/dev/null 2>&1; then
    # Check if pre-commit hook is already installed
    if [ ! -x .git/hooks/pre-commit ] || ! grep -q "prek" .git/hooks/pre-commit 2>/dev/null; then
        prek install --overwrite >/dev/null
    fi

    # Check if commit-msg hook is already installed
    if [ ! -x .git/hooks/commit-msg ] || ! grep -q "prek" .git/hooks/commit-msg 2>/dev/null; then
        prek install --hook-type commit-msg --overwrite >/dev/null
    fi
fi

# Set Git configurations safely and idempotently
if ! git config --global --get push.autoSetupRemote >/dev/null 2>&1; then
    git config --global push.autoSetupRemote true || echo "Warning: Failed to set git config push.autoSetupRemote"
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$repo_root" ]; then
    if ! git config --global --get-all safe.directory | grep -Fxq "$repo_root"; then
        git config --global --add safe.directory "$repo_root" || echo "Warning: Failed to set git safe.directory"
    fi
fi
