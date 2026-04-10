# Virtual Jensen Wiki Knowledge Base — Design Spec

**Date**: 2026-04-09  
**Status**: Draft  
**Approach**: Pre-built wiki + live web search fallback (Karpathy LLM Wiki pattern, Approach B)

---

## Problem

The Virtual Jensen skill models how Jensen Huang thinks but has nearly zero knowledge of what NVIDIA actually builds and sells. Products are referenced only as historical case studies for reasoning patterns (CUDA, Mellanox, RIVA 128). Jensen can't discuss current GPU architectures, software platforms, competitive positioning, or market dynamics with any specificity.

## Goal

Give Jensen a comprehensive, structured knowledge base covering the full NVIDIA product portfolio, software ecosystem, competitive landscape, and market dynamics. When the wiki is stale or insufficient, Jensen uses web search to fetch current data. The wiki is the floor; live search is the ceiling.

## Architecture

Inspired by Karpathy's LLM Wiki pattern (three-layer architecture):

```
Layer 3: THE SCHEMA (SKILL.md + freshness conventions)
  - How Jensen reasons (existing)
  - When to consult wiki (new)  
  - When to fetch live data (new)
  - How to handle stale information (new)

Layer 2: THE WIKI (wiki/ directory, LLM-maintained markdown)
  - Products, software, competitors, markets, concepts
  - Structured, cross-linked, freshness-tagged
  - Jensen's "institutional memory"

Layer 1: RAW SOURCES (existing references/ + future raw/)
  - GTC transcripts, earnings calls, product specs
  - Immutable primary documents
```

## Freshness Model

Every wiki page has frontmatter with freshness metadata:

```yaml
---
title: Page Title
last_updated: 2026-04-09
freshness: quarterly | fast-moving | evergreen
category: products | software | competitors | markets | concepts
---
```

### Freshness Tiers

| Tier | Window | Examples | What goes stale |
|------|--------|----------|-----------------|
| **evergreen** | 12+ months | CUDA moat analysis, accelerated computing thesis, historical case studies | Structural truths — almost nothing |
| **quarterly** | ~3 months | Product specs, architecture details, competitive positioning, software features | New launches, arch refreshes, competitor releases |
| **fast-moving** | ~2 weeks | Market share, pricing, earnings, availability, latest announcements | Constantly — new deals, earnings, partner announcements |

### Staleness Protocol

Baked into SKILL.md as explicit instructions for Jensen:

1. **Check before citing.** Before using any wiki page, check `last_updated` against freshness tier.
2. **Caveat or verify.** Past the freshness window:
   - **quarterly** pages: "Let me check if anything's changed" then web search
   - **fast-moving** pages: Always verify via web search before citing numbers
   - **evergreen** pages: Use directly
3. **Never bluff.** If unable to verify stale data: "My last briefing was [date]. The landscape may have shifted."
4. **Date-stamp claims.** "As of GTC 2026, Blackwell..." not "Blackwell does X."
5. **Prefer structural over point-in-time.** "NVIDIA's moat is the CUDA ecosystem" ages better than "B200 has 208B transistors."

## Wiki Page Structure

Every page follows a consistent format:

```markdown
---
title: [Product/Topic Name]
last_updated: 2026-04-09
freshness: [tier]
category: [category]
---

# [Product/Topic Name]

## What It Is
One-paragraph essence — what Jensen would say at the whiteboard.

## Key Facts
Concrete data: specs, numbers, benchmarks, dates.

## Strategic Significance
Why this matters in Jensen's reasoning — platform play, stack position, moat.

## How It Connects
Cross-links to related wiki pages.

## Jensen's Framing
How Jensen has actually talked about this — direct quotes where available.
```

"Strategic Significance" and "Jensen's Framing" differentiate this from a generic product wiki. Every page connects facts to Jensen's reasoning framework.

## Wiki Directory Structure

```
wiki/
├── index.md                          # Category-organized navigation catalog
├── log.md                            # Append-only ingestion log
├── products/
│   ├── gpu-blackwell.md              # B200, GB200, GB200 NVL72, B100
│   ├── gpu-hopper.md                 # H100, H200, GH200
│   ├── gpu-gaming.md                 # RTX 50-series, DLSS, GeForce stack
│   ├── dgx-systems.md               # DGX B200, SuperPOD, DGX Cloud
│   ├── networking.md                 # ConnectX-7, Spectrum-X, NVLink, NVSwitch
│   ├── drive-platform.md            # DRIVE Thor, DRIVE Orin, Hyperion
│   └── robotics-platforms.md         # Jetson Thor, IGX
├── software/
│   ├── cuda-ecosystem.md             # CUDA, CUDA-X, cuDNN, cuBLAS, TensorRT
│   ├── nim-nemo.md                   # NIM microservices, NeMo framework, guardrails
│   ├── omniverse.md                  # Omniverse, OpenUSD, digital twins
│   ├── isaac-cosmos.md               # Isaac Sim, Isaac ROS, Cosmos world models
│   ├── ai-enterprise.md             # AI Enterprise, RAPIDS, Triton Inference Server
│   └── domain-specific.md           # cuLitho, Clara, BioNeMo, Earth-2
├── competitors/
│   ├── amd.md                        # MI300X/MI350, ROCm, competitive position
│   ├── google-tpu.md                 # TPU v5/Trillium, JAX, Cloud TPU ecosystem
│   ├── intel.md                      # Gaudi 3, Ponte Vecchio, oneAPI
│   ├── custom-asics.md              # AWS Trainium/Inferentia, MS Maia, Google Axion
│   └── ai-software-landscape.md     # Hugging Face, vLLM, open-source stacks, PyTorch
├── markets/
│   ├── data-center-ai.md            # Training vs inference economics, cloud spend
│   ├── sovereign-ai.md              # Nation-state AI infra, partnerships
│   ├── automotive-av.md             # AV market, ADAS, partnership landscape
│   ├── robotics-physical-ai.md      # Physical AI market, humanoid robots, warehouse
│   ├── gaming-market.md             # GeForce market, PC gaming dynamics
│   └── edge-enterprise.md           # Edge AI, enterprise inference, on-prem
└── concepts/
    ├── accelerated-computing.md     # The core thesis: why accelerated > general purpose
    ├── inference-economy.md         # Inference scaling laws, token economics
    ├── ai-factories.md             # "Two factories" vision, data factory + AI factory
    ├── three-waves-of-ai.md        # Perception → generation → agentic
    ├── physical-ai.md              # AI with a body, simulation-to-reality pipeline
    └── cuda-moat.md                # Install base dynamics, ecosystem lock-in analysis
```

**27 wiki pages + index + log = 29 new files**

## SKILL.md Modifications

Add a new section "KNOWLEDGE BASE" between the existing reasoning framework and the output format:

```markdown
## KNOWLEDGE BASE

You have a structured knowledge base about NVIDIA products, software, 
competitors, and markets in the `wiki/` directory. This is your institutional 
memory — treat it like your last briefing packet.

### How to Use the Wiki
1. Before reasoning about any NVIDIA product, technology, or competitor — 
   consult the relevant wiki page(s) via `wiki/index.md`
2. Check `last_updated` in each page's frontmatter
3. Compare against the freshness tier (evergreen: 12mo, quarterly: 3mo, 
   fast-moving: 2wk)
4. Follow cross-references between pages to build full context

### When to Search the Web
Use web search tools (when available) to fetch current data when:
- A wiki page is past its freshness window
- The user asks about something not covered in the wiki
- The user asks about "latest", "recent", "just announced", or "current"
- You need pricing, availability, revenue, or earnings data
- Competitive claims need current verification
- A new product or announcement may have occurred since the wiki was updated

### After Searching
- Use the freshest information available for your reasoning
- If web data contradicts the wiki, trust the web data and note the discrepancy
- Note the vintage of your information: "As of [date]..." 

### Handling Stale Information
- Never cite outdated product specs as current fact
- Never guess at numbers you don't have — say you'd need to verify
- Never confuse product generations (Hopper vs Blackwell vs Rubin)
- When uncertain about freshness, caveat: "My last briefing on this was [date]"
- Prefer structural reasoning (moats, flywheels, stack position) over 
  point-in-time data (specific TFLOPs, exact pricing) when freshness is uncertain
```

## Web App System Prompt Update

The web app (`virtual-jensen-web/app.py`) system prompt gets two additions:

1. **Condensed wiki knowledge block** — Key product facts, competitive positioning, and market dynamics compiled into a single context section appended to the existing system prompt. This is a static snapshot since the web app can't read wiki files at runtime.

2. **Freshness instructions** — Same staleness protocol as SKILL.md, adapted for the web context. Include a `last_updated` date on the knowledge block itself so Jensen knows the vintage.

The condensed block extracts the "What It Is", "Key Facts", and "Strategic Significance" sections from each wiki page, compressed to 2-3 sentences per page. Full detail stays in the wiki files; the web app gets enough for Jensen to reason and know when to search for more. Structured as:
```
## NVIDIA KNOWLEDGE BASE (as of 2026-04-09)

### Products
[Key facts from all product wiki pages, condensed]

### Software Platforms  
[Key facts from all software wiki pages, condensed]

### Competitive Landscape
[Key facts from all competitor wiki pages, condensed]

### Market Dynamics
[Key facts from all market wiki pages, condensed]

Note: This knowledge base was last updated [date]. For anything marked 
"fast-moving" or questions about recent announcements, search the web 
for current data before answering.
```

## Files Modified

| File | Change |
|------|--------|
| `SKILL.md` | Add KNOWLEDGE BASE section with wiki usage, search, and freshness instructions |
| `virtual-jensen-web/app.py` | Append condensed wiki knowledge block + freshness instructions to SYSTEM_PROMPT |

## Research Required During Implementation

Each wiki page requires web research to populate with current, accurate data. Key research areas:

- **Products**: Current specs for Blackwell, Hopper, networking, DRIVE, Jetson families
- **Software**: Current state of CUDA toolkit, NIM catalog, Omniverse, Isaac/Cosmos, AI Enterprise
- **Competitors**: AMD MI300X/MI350 specs and roadmap, Google TPU v5/Trillium, Intel Gaudi, custom ASICs (Trainium, Maia), AI software landscape
- **Markets**: Data center AI spend trends, sovereign AI deployments, AV partnership landscape, robotics/physical AI market formation, gaming market dynamics
- **Concepts**: Current state of inference scaling, AI factory deployments, physical AI progress

## Implementation Order

1. Create `wiki/` directory structure and `index.md`
2. Write product pages (highest value — these are most often referenced)
3. Write software pages (CUDA ecosystem is critical for competitive discussions)
4. Write competitor pages (essential for strategy meeting credibility)
5. Write market pages
6. Write concept pages (many already partially covered in existing references/)
7. Create `log.md` with initial ingestion entry
8. Update `SKILL.md` with KNOWLEDGE BASE section
9. Update web app system prompt with condensed wiki block
10. Test: run a strategy meeting that exercises product/competitive knowledge

## Success Criteria

- Jensen can discuss any current NVIDIA product with specific details
- Jensen can compare NVIDIA vs competitors with real specs and positioning
- Jensen correctly caveats when information might be stale
- Jensen uses web search to fill gaps when tools are available
- Jensen's product knowledge enhances (not replaces) his reasoning framework
- The web app version has equivalent knowledge to the skill version
