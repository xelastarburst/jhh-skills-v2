# feat/knowledge-refresh — merge notes

Major revamp of the Virtual Jensen project: web app rewrites on the
Claude Agent SDK, a full knowledge-refresh ingestion pipeline, a
quality benchmarking harness, and the infrastructure to keep Jensen's
institutional memory fresh automatically.

Branch: `feat/knowledge-refresh` → `main`
Merge shape: 14 commits, +7326 / −699 lines across 38 files
Merge cleanliness: `git merge-tree main HEAD` → no conflicts
(fast-forward possible; recommended merge command is
`git merge --no-ff feat/knowledge-refresh` to keep the feature branch
narrative legible in `git log --graph`).

## What this delivers

### 1. Web app now runs on the Claude Agent SDK

Before: the FastAPI app called the Anthropic SDK directly, billing
through `ANTHROPIC_API_KEY`.
After: `ClaudeSDKClient` per browser session, auth via Claude Code
OAuth / Max plan, `permission_mode="bypassPermissions"`, tools
pinned to `cwd=wiki/`. No API credits burned for personal use.

Jensen now has access to `WebSearch`, `WebFetch`, `Read`, `Grep`,
`Glob` — he looks up current facts and reads the wiki live instead of
reasoning from a frozen knowledge blob.

Critical detail: `ANTHROPIC_API_KEY` is scrubbed from the subprocess
env at startup so Claude Code can't silently fall back to API billing
when a stale key exists in `.env`.

**End-user impact:** demo runs on the user's Max plan subscription;
no recurring cost.

### 2. Knowledge-refresh ingestion pipeline

`scripts/ingest/` — a tiered fetcher + subagent system that keeps
`wiki/*.md` and `references/interviews-log.md` current without
human-in-the-loop scraping.

- **Sources** (`sources.yaml`): 17 interview sources with quality
  tiers A/B/C (Acquired, BG2, Lex Fridman, Stratechery, NVIDIA
  keynotes, etc.) and 12 wiki sources (NVIDIA newsroom, AMD, Intel,
  Google, AWS, Azure, SemiAnalysis, The Information).
- **Fetchers** (`fetchers/`): RSS (feedparser + regex fallback),
  YouTube (yt-dlp `--flat-playlist` after YouTube killed the free
  `videos.xml` feed), HTML hash-diff for pages without a feed.
- **Subagents** (`agents/`): `update_wiki.py` proposes fenced
  unified-diff edits to specific wiki pages; `extract_interview.py`
  appends dated entries to `references/interviews-log.md` —
  **never** rewrites `SKILL.md` (no `Edit` tool granted).
- **Runner** (`run.py`): three modes —
  - default (fetch-only, dry-run),
  - `--invoke-agents` (fetch + subagents dry-run),
  - `--invoke-agents --apply` (subagents land local
    `ingest/YYYY-MM-DD-<source>` branches, append to log,
    persist `state.json`).
- **Transcription**: five backends with a clear free-first default —
  `whisper` (faster-whisper distil-large-v3), `parakeet` (NeMo),
  `parakeet-mlx` (Apple Silicon native), `youtube` (yt-dlp
  auto-captions), `assemblyai` (paid, optional — for diarization).
  Plus `--diarize` (pyannote-audio overlay, free, requires HF token).
- **Scheduling**: three `launchd` plists (daily 06:00, weekly Monday
  07:00, monthly 1st 07:00) with an `install.sh` that rewrites the
  repo path and flips `Disabled=false`. Dry-run by default.

### 3. Benchmarking harness

`scripts/bench/` — 10 scripted Jensen scenarios + LLM-judge grading
so we can detect voice/framework/tool-use drift over time.

- **Deterministic checks** (regex, free): AI-disclaimer absence,
  first-person ratio, signature-phrase coverage, question density,
  tool-use appropriateness, debrief structure.
- **LLM judge**: Haiku 4.5 (not Opus, to avoid self-bias) scores
  six dimensions on 0–4 with verbatim-quote evidence requirement.
- **Per-turn-active checks**: tool-use / structure dimensions only
  apply to the final turn of each case, not the opener.
- **Trend report** (`report.py`): exits 1 on regression (≥1 pt drop
  on any dimension or ≥10 pp deterministic pass-rate drop).
- **Baseline locked in** at git `1e6f685`: 93.9% deterministic pass,
  3.60/4 mean LLM judge (voice_consistency 4.00, framework 3.78,
  in_character 3.60, pushback 3.50, tool-use 3.50, factual 3.25).
- **Pre-commit hook** (`scripts/hooks/pre-commit`): runs a 4-case
  subset of the bench before commits that touch `app.py`, `SKILL.md`,
  wiki pages, references, or the bench config itself. Skips cleanly
  on unrelated commits. `JHH_SKIP_BENCH=1` escape hatch.

### 4. Skill + documentation

- `SKILL.md`: embedded abbreviated strategy-meeting protocol +
  debrief rubric so the skill is self-contained.
- `README.md`: "Running the Web Demo" section; Claude Code / Max
  auth flow.
- `scripts/ingest/README.md`: transcript-quality chain, six tiers,
  install commands per backend.
- `scripts/bench/README.md`: how to run, interpret results, and
  install the pre-commit hook.
- `scripts/launchd/README.md`: install / flip-to-apply / uninstall.
- `scripts/ingest/SMOKE_TEST.md`: record of the first successful
  end-to-end run.

## End-to-end proof (2026-04-20)

Dry-run pipeline executed against live feeds at git `d875852`:

1. Fetched 18 NVIDIA Blog posts.
2. Wiki subagent (Opus 4.7) triaged them, read 4 candidate pages,
   and proposed 4 targeted edits to:
   - `wiki/concepts/inference-economy.md` (cost-per-token TCO bullet)
   - `wiki/concepts/ai-factories.md` (power-flexible AI factories)
   - `wiki/software/cuda-ecosystem.md` (Kubernetes DRA driver)
   - `wiki/software/agent-toolkit-nemoclaw.md` (Gemma 4 acceleration)
3. Explicit per-page rationale; frontmatter preserved; `last_updated`
   bumped; freshness tier unchanged; inline source URLs.
4. Subagent correctly skipped 8 noise items (GeForce NOW game adds,
   editorial pieces, duplicates of existing content).

Wall time 3 min 30 s. Zero unexpected errors. See
`scripts/ingest/SMOKE_TEST.md`.

## Before-you-merge checklist

- [ ] Inspect the baseline JSON at `scripts/bench/history/` to
      confirm the snapshot matches what you want as "known good".
- [ ] Read through `SKILL.md` diff to confirm the embedded meeting
      rubric and KB-tool section match your mental model.
- [ ] Optionally install `pre-commit` hook locally
      (`scripts/hooks/install.sh`) so future commits auto-gate on
      bench regression.
- [ ] **Security**: the API key pasted in the transcript during
      development is still live on the Anthropic account. Nothing in
      the merged code uses it, but rotate it at
      <https://console.anthropic.com/settings/keys> to be safe.

## After-merge setup (optional but recommended)

```bash
# Install local STT for the interview pipeline
virtual-jensen-web/.venv/bin/pip install faster-whisper yt-dlp

# Install bench pre-commit hook
scripts/hooks/install.sh

# Arm the daily / weekly / monthly launchd agents (dry-run)
scripts/launchd/install.sh

# First dry-run of the pipeline end-to-end
virtual-jensen-web/.venv/bin/python scripts/ingest/run.py \
    --tier daily --invoke-agents
```

## Commit list (chronological)

```
bb1d14a feat: rewrite web app on Claude Agent SDK; Max plan OAuth
bd21f89 feat: knowledge-refresh ingestion scaffold (dry-run)
bb620b6 feat: benchmarking suite for Jensen response quality
954d93f feat: ingestion subagents + yt-dlp YouTube backend
2369db6 feat: curate interview sources + wire AssemblyAI
1e6f685 feat: local open-source STT (whisper + parakeet)
75aca27 fix(bench): per-turn check+rubric filtering; tighter regex
1159983 chore: lock in first bench baseline
ca3aba7 feat(ingest): --apply mode on update_wiki.py
7ad42c5 feat(ingest): parakeet-mlx + pyannote diarization
6650a3d feat(bench): 4/4 anchors for three more cases
2494407 feat(bench): git pre-commit hook
d875852 feat(ingest): runner auto-invokes subagents; launchd plists
e55d113 chore: record first successful E2E pipeline smoke test
```
