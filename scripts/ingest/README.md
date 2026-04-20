# Virtual Jensen — Knowledge Refresh Pipeline

Keeps the wiki current with NVIDIA/competitor signal and captures Jensen's
new public thinking so the reasoning framework doesn't drift.

**Status:** dry-run scaffold (this commit). Fetchers work end-to-end and
print a report. LLM subagents, git-branch automation, and launchd
scheduling land in follow-up commits after you validate the sources.

---

## Layout

```
scripts/ingest/
├── sources.yaml          # canonical source registry — human-editable
├── state.json            # processed-IDs cache (gitignored)
├── run.py                # entry point
├── fetchers/             # fetch + parse; no LLM
│   ├── rss.py
│   ├── youtube.py        # uses free videos.xml feed (no API key)
│   └── html.py           # hash-based change detection
└── agents/               # (stub — LLM subagents land later)
```

## Install

```bash
pip install pyyaml feedparser
```

Both are small and pure-Python. `feedparser` is optional (there's a
regex fallback) but produces cleaner output.

## Run a dry-run

```bash
# default: daily tier only
./scripts/ingest/run.py

# all tiers at once
./scripts/ingest/run.py --tier all

# offline preview — shows what would be fetched without hitting the network
./scripts/ingest/run.py --tier all --no-fetch

# ignore prior state (treat every source item as new)
./scripts/ingest/run.py --tier daily --reset-state

# machine-readable output for piping into a subagent later
./scripts/ingest/run.py --tier daily --json
```

The runner prints, per source:
- tier, type, URL/handle
- how many items were fetched
- how many are **new** (not in `state.json`)
- the five most recent new items with title + URL

**Dry-run deliberately does not persist new IDs** — so repeated runs keep
surfacing the same items. When `--apply` mode lands, state gets committed
only after the subagent successfully produces a reviewed PR.

## Tiers

Each source declares a tier. `run.py --tier X` runs everything whose
tier is `<=` X, so `daily` is a strict subset of `weekly` which is a
strict subset of `monthly`.

| Tier     | Cadence target  | What goes here                                        |
|----------|-----------------|-------------------------------------------------------|
| daily    | every 24h       | news, earnings, new videos/podcasts, fresh interviews |
| weekly   | Mondays         | product spec pages, competitive press releases        |
| monthly  | 1st of month    | evergreen concept sources, structural audits          |

## Sources

Two groups in `sources.yaml`:

- **`interview_sources`** — feed `references/interviews-log.md` (append-only).
  Flag long-form episodes with `upgrade_transcript: true` to later request an
  AssemblyAI-quality transcript instead of YouTube auto-captions.
- **`wiki_sources`** — feed specific `wiki/*.md` pages. Each entry declares
  `targets:` (glob patterns against the wiki tree) so the future updater
  agent knows where changes belong.

### Adding a source

Edit `sources.yaml`. The runner picks it up on the next invocation. YouTube
channels only need `handle: "@name"` — channel IDs are auto-resolved and
cached in `state.json` on first run.

## Roadmap

1. ✅ Scaffold + fetchers + dry-run report (this commit).
2. Validate against your machine — sanity-check the source list, check rate
   limits, confirm the YouTube filter surfaces Jensen appearances.
3. Build `agents/update_wiki.py` (Claude Agent SDK subagent that rewrites
   a wiki page given a diff of new material).
4. Build `agents/extract_interview.py` (appends dated entries to
   `references/interviews-log.md`).
5. `--apply` mode: run fetchers → subagents → create `ingest/<date>-<topic>`
   branch → commit → print branch name. Merge is still manual.
6. Optional: `scripts/upgrade-transcript.py <video_id>` helper that pays
   for an AssemblyAI transcript on demand and replaces the auto-caption.
7. `launchd` plists at daily / weekly / monthly cadence. Disabled by default —
   enabled with `launchctl load`.

## Transcript quality chain

The interview extractor's output is only as good as the transcript it
reads. Four tiers, prefer the highest available:

| Tier | Source                                    | Cost            | When to use |
|------|-------------------------------------------|-----------------|-------------|
| 1    | Official channel CC (human-authored)      | Free            | If the channel uploaded real captions — best by a mile |
| 2    | AssemblyAI with speaker diarization       | ~$0.12/hr       | **Default for Tier-A sources** in sources.yaml (Acquired, BG2, Lex, Stratechery podcast, NVIDIA official long-form, Patrick O'Shaughnessy, All-In, Computer History Museum, Stanford GSB, Sequoia) |
| 3    | yt-dlp `--write-auto-sub` auto-captions   | Free            | Fine for daily monitoring to decide whether to upgrade |
| 4    | RSS summary only                          | Free            | For paywalled text sources (Stratechery article, The Information) — treat as an alert, not a transcript |

Flip a source to tier 2 automatically by setting `upgrade_transcript: true`
in its `sources.yaml` entry.

**Wiring AssemblyAI:**

1. Get a key from <https://www.assemblyai.com> ($50 free credit on signup
   covers ~400 hours).
2. Add it to `virtual-jensen-web/.env` (or your shell):
   ```bash
   ASSEMBLYAI_API_KEY=your_key_here
   ```
3. Upgrade a specific video:
   ```bash
   scripts/ingest/upgrade_transcript.py <video_id> --service assemblyai
   ```

The helper extracts audio via yt-dlp, uploads to AssemblyAI, polls until
the job completes, and writes `scripts/ingest/transcripts/<id>.assemblyai.txt`
with speaker labels + timestamps. Audio file is cleaned up on exit.

## Why no API keys (for the fetchers)?

Every **fetcher** here is public-web-scrapable — yt-dlp against public
channel pages, RSS, plain HTML. AssemblyAI is the only paid dependency,
and only for explicit transcript upgrades — never called during a
monitoring run.
