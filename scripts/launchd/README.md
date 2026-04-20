# Virtual Jensen — launchd agents

Three launch agents that run the ingest pipeline on a schedule so the
wiki and interview log don't silently rot.

| Plist                                      | When                 | Tier    | Default mode |
|--------------------------------------------|----------------------|---------|--------------|
| `com.virtual-jensen.daily.plist`           | every day 06:00      | daily   | dry-run      |
| `com.virtual-jensen.weekly.plist`          | Mondays 07:00        | weekly  | dry-run      |
| `com.virtual-jensen.monthly.plist`         | 1st of month 07:00   | monthly | dry-run      |

**Dry-run by default.** Each plist passes `--invoke-agents` but NOT
`--apply`, so the pipeline runs the subagents without committing
branches or appending to the log. Read the logs for a few cycles
before flipping to apply mode.

## Install

```bash
scripts/launchd/install.sh
```

The installer:

1. Rewrites the hard-coded `/Users/alex/Documents/jhh-skills-v2` path in
   each plist to match your clone's path (auto-detected from the script
   location).
2. Flips `Disabled=true` to `Disabled=false`.
3. `plutil -lint`s the rewritten plist before registering it.
4. Calls `launchctl load -w` for each.

Install a subset:

```bash
scripts/launchd/install.sh daily          # just the daily tick
scripts/launchd/install.sh daily weekly   # skip monthly
```

Verify:

```bash
launchctl list | grep virtual-jensen
```

## Flipping to apply mode

Once you've read a few dry-run cycles and trust the output, edit the
installed plist(s) under `~/Library/LaunchAgents/` (not the tracked
source — those stay dry-run to keep the repo safe for other clones).
Add a `--apply` string to the `ProgramArguments` array:

```xml
<array>
    <string>/Users/.../virtual-jensen-web/.venv/bin/python</string>
    <string>/Users/.../scripts/ingest/run.py</string>
    <string>--tier</string><string>daily</string>
    <string>--invoke-agents</string>
    <string>--apply</string>        <!-- add this line -->
</array>
```

Then reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.virtual-jensen.daily.plist
launchctl load   ~/Library/LaunchAgents/com.virtual-jensen.daily.plist
```

## Uninstall

Any one:

```bash
launchctl unload -w ~/Library/LaunchAgents/com.virtual-jensen.daily.plist
rm ~/Library/LaunchAgents/com.virtual-jensen.daily.plist
```

All three:

```bash
for f in daily weekly monthly; do
    launchctl unload -w ~/Library/LaunchAgents/com.virtual-jensen.$f.plist
    rm ~/Library/LaunchAgents/com.virtual-jensen.$f.plist
done
```

## Logs

Each agent writes stdout and stderr to
`scripts/ingest/logs/<tier>.{out,err}.log`. These are gitignored. They
are append-only per run — rotate manually if they get large.

```bash
tail -f scripts/ingest/logs/daily.out.log
tail -f scripts/ingest/logs/daily.err.log
```

## Caveats

- **Tier inheritance:** weekly inherits daily, monthly inherits both.
  Running all three at once (which happens on the 1st of the month when
  it falls on a Monday) duplicates work harmlessly but re-hits Claude.
  If that bothers you, stagger the hours (monthly 05:00, weekly 06:00,
  daily 07:00).
- **Sleeping laptops:** launchd catches up missed runs on next wake,
  but only once — a laptop asleep through both Monday and Tuesday skips
  Monday's weekly tick. Acceptable for a local dev tool; not acceptable
  if you're relying on this for a production workflow.
- **The web app doesn't need to be running.** These plists invoke
  `scripts/ingest/run.py`, which spawns subagents against Claude Code's
  CLI directly — not against `localhost:8000`.
