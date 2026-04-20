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
reads. **Default path is all-local, all-free.** Paid services are
optional upgrades for when you explicitly need speaker diarization.

| Rank | Source                                      | Cost     | When to use |
|------|---------------------------------------------|----------|-------------|
| 1    | Official channel CC (human-authored)        | Free     | Best by a mile when the channel uploads real captions — use yt-dlp's `--write-sub` manually if you spot one |
| 2    | **Parakeet-MLX** (`--service parakeet-mlx`) | Free, local, **Apple Silicon only** | Same weights as NeMo Parakeet, ported to Apple's MLX framework — runs natively on M-series GPUs with no PyTorch dependency. Lightest install of any local backend on an M-series Mac and often the fastest. `pip install parakeet-mlx`. |
| 3    | **NVIDIA Parakeet via NeMo** (`--service parakeet`) | Free, local | Best English accuracy on the Open ASR Leaderboard. NVIDIA's own model — thematically perfect for this project. Heavier install (~2 GB of PyTorch + NeMo); use this path if you're on Linux/CUDA or a non-Apple Mac. |
| 4    | **faster-whisper distil-large-v3** (`--service whisper`) — the default | Free, local | Strong accuracy, lightweight install (one `pip install`). No diarization by default — pair with `--diarize` for speaker labels. |
| 5    | yt-dlp auto-captions (`--service youtube`)  | Free     | 30-second fetch. Only accurate enough for daily monitoring to decide whether to upgrade. |
| 6    | AssemblyAI (`--service assemblyai`)         | ~$0.17/hr | Opt-in *only* when you need speaker diarization on a multi-speaker podcast *without* running pyannote locally (see `--diarize` below). |
| 7    | Raw RSS summary                             | Free     | For paywalled text sources (Stratechery article, The Information) — treat as an alert, not a transcript |

Flip a source to auto-upgrade by setting `upgrade_transcript: true` in
`sources.yaml`. The upcoming runner auto-invocation will default to
`--service whisper` for those.

### Wiring local Whisper (recommended default)

```bash
pip install faster-whisper
# First run downloads the model (~1.5 GB for distil-large-v3).
scripts/ingest/upgrade_transcript.py <video_id>   # whisper is the default
```

Output goes to `scripts/ingest/transcripts/<id>.whisper.txt` with
per-segment `[HH:MM:SS]` timestamps.

Runtime expectations on a laptop:
- CPU (int8 quantized): ~10–15 min per 2-hour episode
- Apple Silicon MPS: ~5–8 min
- CUDA: ~2–4 min

### Wiring Parakeet (best English quality)

```bash
pip install 'nemo_toolkit[asr]'       # ~2 GB install
scripts/ingest/upgrade_transcript.py <video_id> --service parakeet
```

Output goes to `scripts/ingest/transcripts/<id>.parakeet.txt`. NeMo has
segment-level timestamps on newer releases; the script falls back to a
single unsegmented block on older NeMo.

### Wiring Parakeet-MLX (Apple Silicon, lightest local option)

```bash
pip install parakeet-mlx                                   # no PyTorch
scripts/ingest/upgrade_transcript.py <video_id> --service parakeet-mlx
```

Output goes to `scripts/ingest/transcripts/<id>.parakeet-mlx.txt`. The
script hard-fails on non-Apple-Silicon platforms with a pointer to the
NeMo or whisper backends.

### Speaker diarization with pyannote (`--diarize`)

Any local STT backend (`whisper`, `parakeet`, `parakeet-mlx`) can be
post-processed with [pyannote.audio](https://github.com/pyannote/pyannote-audio)
to attach speaker labels:

```bash
pip install pyannote.audio torch torchaudio
export HF_TOKEN=hf_...                                     # or HUGGING_FACE_HUB_TOKEN
# Accept the model terms once at:
#   https://huggingface.co/pyannote/speaker-diarization-3.1
scripts/ingest/upgrade_transcript.py <video_id> --service parakeet-mlx --diarize
```

The script extracts audio once, runs the STT backend and pyannote on the
same file, aligns pyannote's speaker intervals to the STT's per-segment
timestamps, and writes a second file alongside the raw transcript:

```
scripts/ingest/transcripts/<id>.<service>.txt            # raw timestamped transcript
scripts/ingest/transcripts/<id>.<service>.diarized.txt   # [HH:MM:SS] Speaker A: ...
```

Speakers are re-labelled `A`, `B`, `C`, ... in first-appearance order so
the output stays stable regardless of pyannote's internal `SPEAKER_0N`
numbering. If `HF_TOKEN` is missing, or if `pyannote.audio` isn't
installed, the script exits with a specific install / auth message and
does not touch any transcript files.

### Wiring AssemblyAI (optional, paid — only for diarization)

Skip this unless you specifically need speaker-labelled transcripts
*and* you'd rather pay $0.17/hr than run pyannote locally (see `--diarize`
above).

1. Get a key from <https://www.assemblyai.com> (free signup credit covers
   ~100 hours of diarized audio).
2. Add to `virtual-jensen-web/.env` or your shell:
   ```bash
   ASSEMBLYAI_API_KEY=your_key_here
   ```
3. Upgrade:
   ```bash
   scripts/ingest/upgrade_transcript.py <video_id> --service assemblyai
   ```

## Why no API keys (for the fetchers)?

Every **fetcher** here is public-web-scrapable — yt-dlp against public
channel pages, RSS, plain HTML. Local Whisper/Parakeet run on your
machine — no network call after the model is downloaded. AssemblyAI
is the only paid dependency, opt-in per upgrade.
