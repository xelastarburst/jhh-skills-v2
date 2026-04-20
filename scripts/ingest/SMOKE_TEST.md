# Smoke test — 2026-04-20 (git d875852)

First end-to-end dry-run of the ingest pipeline. Captures what actually
happens when you run `scripts/ingest/run.py --tier daily
--invoke-agents` without `--apply`.

Recording this so future regressions have a concrete reference for
"the pipeline used to work like this."

## Invocation

```bash
virtual-jensen-web/.venv/bin/python scripts/ingest/run.py \
    --tier daily --invoke-agents
```

No `--apply` (proposed edits printed to stdout only; no branches
created, state.json untouched). Wall time: ~3 minutes 30 seconds.

## Fetch phase

| Source                              | Fetched | New | Notes |
|-------------------------------------|---------|-----|-------|
| NVIDIA Blog (RSS)                   | 18      | 18  | ✅ Full signal; base case for the wiki updater |
| NVIDIA Newsroom — All News (RSS)    | 0       | 0   | Feed shape may need revisiting; redirect chain looked OK |
| NVIDIA Financial News (RSS)         | 0       | 0   | No earnings event in window |
| Stratechery (Ben Thompson) (RSS)    | 0       | 0   | No Jensen-tagged posts this window |
| NVIDIA / Acquired / BG2 / Lex / …   | error   | –   | yt-dlp not installed locally; fetcher degraded cleanly with install hint |

YouTube sources return `YouTubeFeedUnavailable: yt-dlp not installed`
until `pip install yt-dlp` runs in the web-app venv — the degrade is
intentional and documented in `fetchers/youtube.py`.

## Wiki agent invocation

Input: 15 most-recent NVIDIA Blog items (the cap per invocation).
Model: `claude-opus-4-7`. Mode: dry-run.

The subagent read four candidate wiki pages, then proposed four edits
with explicit rationale-per-page:

| Target page                                    | Change                                           |
|------------------------------------------------|--------------------------------------------------|
| `wiki/concepts/inference-economy.md`          | Add "Cost per token as canonical TCO metric" bullet |
| `wiki/concepts/ai-factories.md`               | Add "Power-flexible AI factories" bullet         |
| `wiki/software/cuda-ecosystem.md`             | Add "Kubernetes DRA driver open-sourced"         |
| `wiki/software/agent-toolkit-nemoclaw.md`     | Add "Third-party open model acceleration (Gemma 4)" |

Every diff:

- Preserved YAML frontmatter structure.
- Bumped `last_updated: 2026-04-09 → 2026-04-19`.
- Left `freshness:` tier unchanged.
- Cited the source URL inline with a date stamp.
- Did not invent facts the RSS titles/summaries didn't support.

The subagent also **deliberately skipped** eight items with explicit
rationale — GeForce NOW game additions (not tracked in wiki), editorial
posts with no datable claims, summary roundups already covered by
existing wiki content, and OpenShell material already on the target
page.

## Interview agent invocation

Did not run in this pass because all Tier-A YouTube sources failed
fetch (yt-dlp missing) and the one RSS interview source (Stratechery)
had zero new items.

**Next E2E run should install yt-dlp first** to exercise the
interview pipeline, or feed the extractor a handcrafted transcript.

## State persistence

state.json was NOT updated (dry-run, as expected). A follow-up
`--apply` run on the same items would:

1. Create local branches `ingest/2026-04-19-nvidia-blog` with the
   four edits.
2. Commit with the subagent's rationale as body.
3. Persist the 18 seen IDs to state.json so next run doesn't re-surface.

## Status: ✅

Pipeline end-to-end: fetch → dedupe → subagent routing → proposed
patches → safe dry-run exit. No errors outside the expected yt-dlp
degrade.
