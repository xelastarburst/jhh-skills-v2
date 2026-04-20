# Virtual Jensen — Benchmarking

Tracks whether Jensen's response quality is drifting. Two layers:

1. **Deterministic checks** — cheap regex/structure assertions that run
   on every response (e.g. *no AI disclaimers*, *signature phrase
   present*, *used wiki tool when asked a wiki-scoped question*).
2. **LLM-as-judge** — Haiku 4.5 (not Opus, to avoid self-bias) scores
   each response on rubric dimensions defined in `rubrics.yaml`.

Every run is persisted under `history/<timestamp>.json` with the git
SHA of the code that produced it, so any regression is bisectable.

## Layout

```
scripts/bench/
├── cases.yaml       # scripted scenarios (10 cases)
├── rubrics.yaml     # LLM-judge dimensions and scoring rubric
├── run.py           # drives the web app, captures transcripts, runs checks
├── grade.py         # LLM-as-judge pass — writes scores into run record
├── report.py        # trend report; exits 1 on regression
└── history/         # one JSON per run (gitignored? see below)
```

## Install

```bash
# Bench uses pyyaml + the Claude Agent SDK that the web app already depends on.
virtual-jensen-web/.venv/bin/pip install pyyaml
```

## Usage

Start the web app (in another terminal):

```bash
cd virtual-jensen-web
.venv/bin/uvicorn app:app --port 8000
```

Then in the repo root:

```bash
# 1. Drive the scripted cases, capture transcripts + run deterministic checks
virtual-jensen-web/.venv/bin/python scripts/bench/run.py

# 2. LLM-judge pass (Haiku 4.5, via Claude Code OAuth)
virtual-jensen-web/.venv/bin/python scripts/bench/grade.py

# 3. Trend report vs previous runs — exits 1 if anything regressed
virtual-jensen-web/.venv/bin/python scripts/bench/report.py
```

Subset runs for fast iteration:

```bash
scripts/bench/run.py --only opener,debrief-request
scripts/bench/run.py --tag post-prompt-tweak
scripts/bench/grade.py --dry-run           # show prompts, don't call the model
```

## What a run looks like

```
> opener — Fresh meeting — Jensen opens in character
  turns=1 errors=0 checks=4/5 (4.2s)

> voice-stress-sharp — Sharp mode must stay sharp under pushback
  turns=3 errors=0 checks=6/9 (18.7s)

...

Overall deterministic-check pass rate: 86.3% (49/57)
Saved run: history/2026-04-20T04-22-11Z.json
```

After grading:

```
Per-dimension averages:
  factual_grounding            3.4
  framework_adherence          3.6
  in_character                 3.8
  pushback_specificity         3.1
  tool_use_appropriateness     3.2
  voice_consistency            3.5
```

And the trend:

```
=== LLM judge (0–4) ===
  dimension                       now    was    Δ
  factual_grounding              3.40   3.40    —
  framework_adherence            3.60   3.60    —
  in_character                   3.80   3.80    —
  pushback_specificity           3.10   3.50   -0.40
  tool_use_appropriateness       3.20   3.20    —
  voice_consistency              3.50   3.50    —

OK  (no dimension dropped ≥1.0 pt vs previous median)
```

## Cases

10 scenarios in `cases.yaml`, covering:

- **Opener / voice** — `opener`, `voice-stress-sharp`, `voice-stress-nice`
- **Framework probing** — `vague-idea`, `multi-idea`, `zero-billion-market`
- **Tool use** — `wiki-fact-question`, `tool-forcing-current-facts`
- **Debrief** — `debrief-request` (structured rubric must appear)
- **Pushback handling** — `pushback-after-challenge`

Three cases carry hand-written **anchor** responses so the judge has a
concrete 4/4 reference. Add more anchors over time as you see patterns.

## Cost

- Deterministic checks: free (pure regex).
- LLM judge: one Haiku 4.5 call per Jensen turn × dimensions. A full run
  over 10 cases (~20 turns total, ~4 dims each) is on the order of 80
  calls — well under the Max plan's rate limits. Each call is short
  (rubric + one response ≈ 2–3K tokens in, ≤500 tokens out).

## When to run

- After **any** change to the system prompt (`app.py SYSTEM_PROMPT` or
  `SKILL.md`).
- After adding/removing a tool from `allowed_tools`.
- After upgrading the Claude Agent SDK or switching the default model.
- As a CI gate if/when this repo picks up CI.

## When scores shift, what to check

- **In-character drops** — did anything leak an AI-assistant register
  into the prompt? Check for "you are an assistant" patterns.
- **Framework adherence drops** — did the system prompt get trimmed?
  The 7-step framework must stay in the prompt.
- **Tool-use drops** — did tool descriptions get worse? Did `cwd` move
  away from the wiki?
- **Voice consistency drops** — did personality modifiers get out of
  sync with the requested mode?

## Threshold tuning

Defaults: regression = any dimension drops ≥1.0 pt vs previous run, or
deterministic pass rate drops ≥10 pp. Adjust via flags:

```bash
scripts/bench/report.py --threshold 0.5         # stricter
scripts/bench/report.py --window 5              # compare vs median of last 5
scripts/bench/report.py --pass-rate-threshold 0.05
```

## Run as a pre-commit hook

The bench can gate commits that touch Jensen's behavior. The hook is a
thin POSIX shell script at `scripts/hooks/pre-commit` that:

- Skips cleanly on commits that don't touch `virtual-jensen-web/app.py`,
  `SKILL.md`, `references/**.md`, `wiki/**.md`, `scripts/bench/cases.yaml`,
  or `scripts/bench/rubrics.yaml` — ordinary commits aren't delayed.
- Runs a **subset** of cases (`opener`, `vague-idea`, `wiki-fact-question`,
  `debrief-request`) for fast feedback (~60–90s), tagged with the current
  HEAD short SHA.
- Fails the commit if `report.py` detects a regression (≥1.0 pt drop on
  any rubric dimension, or ≥10 pp drop in deterministic pass rate).

Install (symlinks into `.git/hooks/pre-commit`, so edits to the tracked
file take effect without re-installing):

```bash
scripts/hooks/install.sh
```

Uninstall:

```bash
rm .git/hooks/pre-commit
```

Bypass on a specific commit:

```bash
JHH_SKIP_BENCH=1 git commit -m "WIP: skip bench"
```

**Warning:** the hook requires the web app to be running on
`127.0.0.1:8000`. If it isn't, the hook fails with instructions rather
than silently passing. Start it in another terminal:

```bash
cd virtual-jensen-web && .venv/bin/uvicorn app:app --port 8000
```

