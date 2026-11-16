# Virtual Jensen — JHH Reasoning Engine

A product strategy skill and local web app inspired by Jensen Huang's approach to reasoning, technology bets, and platform building. Use it to examine a product idea, test assumptions, or practice a strategy meeting with a demanding sparring partner.

The framework draws on [26 annotated research sources](RESEARCH.md), with supporting references and a structured NVIDIA knowledge base. The repository is named `jhh-skills-v2`; the installable skill is named `virtual-jensen`.

## What you can do

- **Analyze a strategy:** gather ground truth, find the governing force, reconstruct the problem from first principles, and test the reasoning chain.
- **Practice a strategy meeting:** work through questions and pushback, then request a structured debrief.
- **Run the browser demo:** choose an approachable or intense meeting style, watch research activity, and export a transcript or generated summary.
- **Maintain the knowledge base:** fetch source updates, review proposed wiki edits, and track response quality with the benchmark harness.

The reasoning lenses include platform versus product, commodity risk, stack ownership, flywheels, emerging markets, and organizational design. Read [SKILL.md](SKILL.md) for the full process, including risk preparation before committing.

## Use the skill

### Claude Code

Install the skill for your personal projects:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/xelastarburst/jhh-skills-v2.git \
  ~/.claude/skills/virtual-jensen
```

Or install it inside a project, from that project's root:

```bash
mkdir -p .claude/skills
git clone https://github.com/xelastarburst/jhh-skills-v2.git \
  .claude/skills/virtual-jensen
```

Start a Claude Code session and invoke `/virtual-jensen`, or ask:

> Spar with Jensen about my product strategy. Start by asking what I'm building.

For a written analysis, try:

> Apply Jensen's reasoning framework to this product idea: [your idea]. Surface the assumptions that need evidence.

### Cursor

The condensed rule lives in [cursor/virtual-jensen.mdc](cursor/virtual-jensen.mdc). From your project root:

```bash
git clone https://github.com/xelastarburst/jhh-skills-v2.git
mkdir -p .cursor/rules
cp jhh-skills-v2/cursor/virtual-jensen.mdc .cursor/rules/virtual-jensen.mdc
```

The rule sets `alwaysApply: false` and describes when it should be used. Use the full skill when you need the complete references, bibliography, and meeting protocol.

### OpenClaw and other agents

For OpenClaw, install the repository in its skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/xelastarburst/jhh-skills-v2.git \
  ~/.openclaw/workspace/skills/virtual-jensen
```

For another agent, use its supported skill installation mechanism, keeping `SKILL.md`, `references/`, and `wiki/` together. You can also read [SKILL.md](SKILL.md) directly and apply the framework without an agent.

## Run the local web app

The FastAPI demo uses the **Claude Agent SDK** and your installed **Claude Code CLI login**. Authenticate Claude Code before starting a meeting. The app deliberately removes `ANTHROPIC_API_KEY` from its environment so the child CLI uses the configured Claude Code login.

You will need Git, Python 3 with `venv`, and an authenticated `claude` executable on your `PATH`.

```bash
git clone https://github.com/xelastarburst/jhh-skills-v2.git
cd jhh-skills-v2/virtual-jensen-web

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Complete this if Claude Code is not already authenticated.
claude auth login

uvicorn app:app --reload --port 8000
```

Open [localhost:8000](http://localhost:8000), choose a model and meeting style, and start a meeting. Run `uvicorn` from `virtual-jensen-web/` so the app can find its static files.

Optional settings can be exported before starting the server or placed in `virtual-jensen-web/.env`:

| Setting | Purpose |
| --- | --- |
| `JENSEN_MODEL` | Default model ID; the available choices are defined in `app.py`. |
| `CLAUDE_CLI_PATH` | Path to the installed `claude` executable if it is not on `PATH`. |

The demo can search the web and read the repository's wiki during a conversation. It checks wiki freshness at startup and includes freshness guidance in the meeting prompt. Model and meeting-style choices persist in the browser.

Useful local pages:

- [Research bibliography](http://localhost:8000/research)
- [Wiki freshness report](http://localhost:8000/api/freshness)

## Refresh knowledge and evaluate changes

These tools are separate from the skill installation:

| Workflow | Guide |
| --- | --- |
| Fetch sources, preview wiki updates, and upgrade transcripts | [Knowledge refresh](scripts/ingest/README.md) |
| Run scripted meetings, grade responses, and compare results | [Benchmark harness](scripts/bench/README.md) |
| Schedule refresh jobs on macOS | [launchd setup](scripts/launchd/README.md) |

For an offline source preview, use an activated Python environment and run from the repository root:

```bash
python -m pip install -r scripts/ingest/requirements.txt
python scripts/ingest/run.py --tier all --no-fetch
```

The ingestion runner defaults to a dry run. `--invoke-agents` asks agents to propose updates; `--invoke-agents --apply` applies updates locally and persists processed-source state. Review the workflow guide before enabling apply mode or scheduling jobs.

## Repository map

| Path | Contents |
| --- | --- |
| [SKILL.md](SKILL.md) | Full reasoning framework and meeting instructions |
| [RESEARCH.md](RESEARCH.md) | Annotated research bibliography |
| [references/](references/) | Reasoning details, organization design, technology examples, and meeting protocol |
| [wiki/](wiki/) | NVIDIA products, software, concepts, markets, and competitors |
| [cursor/](cursor/) | Condensed Cursor rule |
| [virtual-jensen-web/](virtual-jensen-web/) | FastAPI backend and browser interface |
| [scripts/](scripts/) | Knowledge refresh, benchmarks, scheduling, and commit hooks |

## Contributing

Keep documentation and examples aligned with the implementation. Cite sources when updating research or wiki facts, and preserve each wiki page's freshness metadata. For changes to prompts, tools, or the reasoning framework, use the [benchmark guide](scripts/bench/README.md) to check response quality.

## License

[MIT](LICENSE).
