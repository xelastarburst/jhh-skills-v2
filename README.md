# Virtual Jensen — JHH Reasoning Engine

A skill that models **how Jensen Huang thinks** — not his opinions, but his cognitive operations. Built from 26 primary sources.

## What It Does

**Analysis Mode**: Give it any product strategy problem and it runs Jensen's 7-step thinking process:

1. **Absorb** — Gather ground truth before forming a view
2. **Identify the Essence** — Find the ONE governing force
3. **First-Principles Reconstruction** — Rebuild from scratch
4. **Speed of Light** — Benchmark against the theoretically possible
5. **Reasoning Chain** — Build step-by-step logic to an inevitable conclusion
6. **Invert** — Surface every assumption, find the existential risks
7. **Commit or Walk Away** — No half-measures

**Strategy Meeting Mode**: Interactive roleplay where Jensen quizzes you through his framework. He asks the hard questions, pushes back on vague thinking, and forces you to reason like he does. Ends with a structured debrief scoring you on each step.

Activate with: *"spar with Jensen"*, *"strategy meeting"*, *"quiz me like Jensen"*

## Reasoning Lenses

- **Platform vs. Product** — Is there an install base play?
- **Commodity Test** — Are other people already doing this?
- **Stack Thinking** — Who owns each layer?
- **Flywheel Test** — Does this create a virtuous cycle?
- **Zero-Billion-Dollar Market** — Is being early the only defensible position?
- **Organizational Mirror** — Does the org mirror the product architecture?

---

## Installation

### Claude Code

The skill works natively with Claude Code's skill system. Two options:

**Personal install** (available in all your projects):
```bash
git clone https://github.com/xelastarburst/virtual-jensen.git
cp -r virtual-jensen ~/.claude/skills/virtual-jensen
```

**Project install** (shared with anyone who clones the repo):
```bash
git clone https://github.com/xelastarburst/virtual-jensen.git
cp -r virtual-jensen .claude/skills/virtual-jensen
```

That's it. Claude Code automatically reads the `SKILL.md` frontmatter and triggers the skill when it matches your task. You can also invoke it directly with `/virtual-jensen`.

To verify it's working, start a Claude Code session and ask: *"What would Jensen think about [your product idea]?"*

### Cursor

A pre-built Cursor rule is included at `cursor/virtual-jensen.mdc`. This is a condensed version of the full skill optimized for Cursor's `.mdc` rule format.

```bash
git clone https://github.com/xelastarburst/virtual-jensen.git

# Copy the rule into your project
cp virtual-jensen/cursor/virtual-jensen.mdc .cursor/rules/virtual-jensen.mdc
```

The rule has `alwaysApply: false`, which means Cursor will load it when it's contextually relevant (product strategy discussions, "think like Jensen," etc.). To make it always active, change `alwaysApply: true` in the frontmatter.

> **Note**: Cursor rules have a tighter context budget than Claude Code skills. The `.mdc` version is a condensed single-file version of the full framework. For the complete experience (all reference files, detailed strategy meeting protocol, source bibliography), use the Claude Code skill or read the files directly.

### OpenClaw

```bash
cp -r virtual-jensen/ ~/.openclaw/workspace/skills/virtual-jensen
```

### Other Agents (Codex, Gemini CLI, Cline, etc.)

The SKILL.md format is becoming a cross-agent standard. Copy the folder into whatever skills/instructions directory your agent uses. Or simply paste `SKILL.md` into any LLM's system prompt — the file IS the thinking system, no special tooling required.

### No Agent? Just Read It

You don't need any agent to use this. Open `SKILL.md`, read the 7-step process and reasoning lenses, and apply them yourself. The thinking system works in your head too.

---

## Running the Web Demo

The `virtual-jensen-web/` directory ships a FastAPI app that runs a live "strategy meeting" in your browser. Claude Opus 4.7 plays Jensen via the Anthropic SDK with adaptive thinking, prompt caching, and a tool-use loop — so Jensen researches on the fly:

- **Server-side `web_search` / `web_fetch`** — Jensen looks up current earnings, competitor moves, and terms he doesn't recognize.
- **Client-side wiki tools** (`list_wiki_pages`, `read_wiki_page`, `grep_wiki`) — Jensen reads the repo's `wiki/` pages on demand, with freshness warnings surfaced when a page is past its window.

### 1. Install dependencies

```bash
cd virtual-jensen-web
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

Set `ANTHROPIC_API_KEY` in a `.env` file in `virtual-jensen-web/` (or export it in your shell):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Optional — override the default model:
export JENSEN_MODEL=claude-opus-4-7   # or claude-opus-4-6, claude-sonnet-4-6
```

### 3. Run it

```bash
uvicorn app:app --reload --port 8000
```

Open <http://localhost:8000> and click **Start Meeting**. The research bibliography is available at <http://localhost:8000/research>. `/api/freshness` returns the current wiki freshness scan.

### Notes

- Freshness of the NVIDIA wiki is validated on startup against `wiki/*.md` frontmatter — stale pages are logged as warnings and surface as a banner when Jensen reads them.
- Your model/mode selection persists across reloads via `localStorage`.
- `RESEARCH.md` is served from the repo root (not duplicated in `static/`).
- Tool-use status chips render inline above Jensen's messages ("Reading `competitors/amd.md`", "Searching `NVIDIA Q1 earnings`") so you see what he's consulting in real time.

---

## Files

```
virtual-jensen/
├── SKILL.md                              # The full thinking system
├── RESEARCH.md                           # Annotated bibliography of all 26 sources
├── cursor/
│   └── virtual-jensen.mdc               # Pre-built Cursor rule (condensed)
├── references/
│   ├── reasoning-system.md               # Deep dive on each cognitive operation
│   ├── company-architecture.md           # How Jensen structures organizations
│   ├── technology-bets.md                # Historical examples of the framework
│   ├── strategy-meeting.md               # Interactive meeting protocol & debrief
│   └── sources.md                        # Full source list
├── wiki/                                 # Structured product/competitive knowledge
└── virtual-jensen-web/                   # FastAPI + browser demo
    ├── app.py
    ├── requirements.txt
    └── static/                           # index.html, research.html, app.js, style.css
```

## Research

See [RESEARCH.md](RESEARCH.md) for the complete annotated bibliography — every source used to build this reasoning model, what it contributed, and reliability notes.

## License

MIT
