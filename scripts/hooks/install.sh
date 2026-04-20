#!/usr/bin/env sh
# Install the Virtual Jensen pre-commit hook as a symlink so edits to the
# tracked file under scripts/hooks/pre-commit take effect immediately.
#
# Uninstall:  rm .git/hooks/pre-commit

set -eu

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    printf 'error: not inside a git repo.\n' >&2
    exit 1
}

HOOK_SRC="$REPO_ROOT/scripts/hooks/pre-commit"
HOOK_DST="$REPO_ROOT/.git/hooks/pre-commit"

if [ ! -f "$HOOK_SRC" ]; then
    printf 'error: %s not found.\n' "$HOOK_SRC" >&2
    exit 1
fi

if [ -e "$HOOK_DST" ] || [ -L "$HOOK_DST" ]; then
    printf 'error: %s already exists.\n' "$HOOK_DST" >&2
    printf '       Merge it manually with scripts/hooks/pre-commit, or remove it:\n' >&2
    printf '           rm %s\n' "$HOOK_DST" >&2
    exit 1
fi

mkdir -p "$REPO_ROOT/.git/hooks"

# Symlink (not copy) — relative target so the repo is portable across clones.
ln -s ../../scripts/hooks/pre-commit "$HOOK_DST"
chmod +x "$HOOK_SRC"

printf 'installed: %s -> ../../scripts/hooks/pre-commit\n' "$HOOK_DST"
printf 'uninstall with:  rm %s\n' "$HOOK_DST"
