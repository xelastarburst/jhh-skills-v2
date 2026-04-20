#!/usr/bin/env sh
#
# Install the Virtual Jensen launchd agents into ~/Library/LaunchAgents/.
# Rewrites the hard-coded /Users/alex/... paths to point at THIS clone,
# flips `Disabled` to false, and registers each plist with launchctl.
#
# Dry-run safe: the plists pass --invoke-agents WITHOUT --apply by default.
# You'll need to hand-edit the installed copy to add --apply once you've
# reviewed a few cycles of logs.
#
# Usage:
#     scripts/launchd/install.sh                 # install all three
#     scripts/launchd/install.sh daily           # install just one
#     scripts/launchd/install.sh daily weekly    # a subset

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
VENV_PY="$REPO_ROOT/virtual-jensen-web/.venv/bin/python"
AGENTS_DIR="$HOME/Library/LaunchAgents"
SOURCE_DIR="$REPO_ROOT/scripts/launchd"

if [ ! -x "$VENV_PY" ]; then
    echo "error: $VENV_PY not found or not executable." >&2
    echo "       create the web app venv first: cd virtual-jensen-web && python3 -m venv .venv && pip install -r requirements.txt" >&2
    exit 1
fi

mkdir -p "$AGENTS_DIR"
mkdir -p "$REPO_ROOT/scripts/ingest/logs"

if [ $# -eq 0 ]; then
    tiers="daily weekly monthly"
else
    tiers="$*"
fi

for tier in $tiers; do
    src="$SOURCE_DIR/com.virtual-jensen.$tier.plist"
    dst="$AGENTS_DIR/com.virtual-jensen.$tier.plist"

    if [ ! -f "$src" ]; then
        echo "skipping $tier: $src not found" >&2
        continue
    fi

    # Rewrite the /Users/alex/Documents/jhh-skills-v2 placeholder to REPO_ROOT
    # AND flip Disabled=true to Disabled=false so the agent actually runs.
    sed \
        -e "s|/Users/alex/Documents/jhh-skills-v2|$REPO_ROOT|g" \
        -e "s|<key>Disabled</key>.*<true/>|<key>Disabled</key><false/>|" \
        "$src" > "$dst"

    # plutil validates before loading; loading a broken plist throws a
    # cryptic error, better to fail here with a legible message.
    if ! plutil -lint "$dst" >/dev/null 2>&1; then
        echo "error: plutil rejected $dst" >&2
        plutil -lint "$dst" >&2 || true
        rm -f "$dst"
        exit 1
    fi

    # Unload first in case an old copy is already registered.
    launchctl unload "$dst" 2>/dev/null || true
    launchctl load -w "$dst"
    echo "installed: $dst"
done

echo ""
echo "Running agents:"
launchctl list | awk 'NR==1 || /virtual-jensen/' || true
echo ""
echo "Logs:    $REPO_ROOT/scripts/ingest/logs/"
echo "Uninstall:"
for tier in $tiers; do
    echo "    launchctl unload -w \"$AGENTS_DIR/com.virtual-jensen.$tier.plist\""
    echo "    rm \"$AGENTS_DIR/com.virtual-jensen.$tier.plist\""
done
