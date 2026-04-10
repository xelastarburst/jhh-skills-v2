# JHH Wiki Knowledge Base — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Virtual Jensen comprehensive, structured knowledge of NVIDIA products, software, competitors, and markets via a wiki layer with freshness metadata and web search fallback.

**Architecture:** A `wiki/` directory of cross-linked markdown pages following Karpathy's LLM Wiki pattern. Each page has freshness-tagged frontmatter. SKILL.md gets a KNOWLEDGE BASE section instructing Jensen when to use the wiki vs web search. The web app system prompt gets a condensed version of all wiki knowledge.

**Tech Stack:** Markdown files, YAML frontmatter, web research via WebFetch/WebSearch tools

**Spec:** `docs/superpowers/specs/2026-04-09-jhh-wiki-knowledge-base-design.md`

---

## File Map

### New Files (wiki/)
```
wiki/
├── index.md
├── log.md
├── products/
│   ├── gpu-blackwell.md
│   ├── gpu-hopper.md
│   ├── gpu-gaming.md
│   ├── dgx-systems.md
│   ├── networking.md
│   ├── drive-platform.md
│   └── robotics-platforms.md
├── software/
│   ├── cuda-ecosystem.md
│   ├── nim-nemo.md
│   ├── omniverse.md
│   ├── isaac-cosmos.md
│   ├── ai-enterprise.md
│   └── domain-specific.md
├── competitors/
│   ├── amd.md
│   ├── google-tpu.md
│   ├── intel.md
│   ├── custom-asics.md
│   └── ai-software-landscape.md
├── markets/
│   ├── data-center-ai.md
│   ├── sovereign-ai.md
│   ├── automotive-av.md
│   ├── robotics-physical-ai.md
│   ├── gaming-market.md
│   └── edge-enterprise.md
└── concepts/
    ├── accelerated-computing.md
    ├── inference-economy.md
    ├── ai-factories.md
    ├── three-waves-of-ai.md
    ├── physical-ai.md
    └── cuda-moat.md
```

### Modified Files
```
SKILL.md                          — Add KNOWLEDGE BASE section
virtual-jensen-web/app.py         — Update SYSTEM_PROMPT with condensed wiki knowledge
```

---

## Page Template

Every wiki page MUST follow this exact structure. Agents writing pages should copy this template:

```markdown
---
title: [Name]
last_updated: 2026-04-09
freshness: [evergreen | quarterly | fast-moving]
category: [products | software | competitors | markets | concepts]
---

# [Name]

## What It Is
[One paragraph. What Jensen would say at the whiteboard. No marketing fluff.]

## Key Facts
[Bullet points. Concrete specs, numbers, dates, benchmarks. Cite sources where possible.]

## Strategic Significance
[Why this matters in Jensen's reasoning framework. Connect to: platform vs product, stack thinking, flywheel test, commodity test, install base dynamics, or zero-billion-dollar market test. This is what makes the page useful to Jensen — not just facts but WHY they matter strategically.]

## How It Connects
[Cross-links to related wiki pages using relative paths.]
- See: `../competitors/amd.md` — MI300X comparison
- See: `../software/cuda-ecosystem.md` — software stack dependency
- See: `../concepts/inference-economy.md` — why inference perf matters here

## Jensen's Framing
[How Jensen has actually talked about this. Direct quotes from GTC keynotes, interviews, earnings calls where available. If no direct quote exists, describe how Jensen's reasoning framework would frame this. Cite source (e.g., "GTC 2026 keynote", "Acquired FM interview, March 2024").]
```

---

## Task 1: Wiki Scaffolding — index.md, log.md, Directory Structure

**Files:**
- Create: `wiki/index.md`
- Create: `wiki/log.md`
- Create: directories `wiki/products/`, `wiki/software/`, `wiki/competitors/`, `wiki/markets/`, `wiki/concepts/`

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/lingq/Documents/jhh-skills/virtual-jensen
mkdir -p wiki/products wiki/software wiki/competitors wiki/markets wiki/concepts
```

- [ ] **Step 2: Create index.md**

Write `wiki/index.md`:

```markdown
---
title: Virtual Jensen Wiki — Index
last_updated: 2026-04-09
---

# Virtual Jensen Knowledge Base

Jensen's institutional memory. Structured product, software, competitive, and market knowledge organized for strategic reasoning.

**Freshness tiers:** Each page has a `freshness` tag in frontmatter.
- **evergreen** (12+ months): Structural truths, theses, historical analysis
- **quarterly** (~3 months): Product specs, competitive positioning, software features
- **fast-moving** (~2 weeks): Pricing, earnings, availability, latest announcements

---

## Products

- [Blackwell GPU Architecture](products/gpu-blackwell.md) — B200, GB200, GB200 NVL72
- [Hopper GPU Architecture](products/gpu-hopper.md) — H100, H200, GH200
- [GeForce & Gaming](products/gpu-gaming.md) — RTX 50-series, DLSS, gaming stack
- [DGX Systems](products/dgx-systems.md) — DGX B200, SuperPOD, DGX Cloud
- [Networking](products/networking.md) — ConnectX-7, Spectrum-X, NVLink, NVSwitch
- [DRIVE Platform](products/drive-platform.md) — DRIVE Thor, DRIVE Orin, Hyperion
- [Robotics Platforms](products/robotics-platforms.md) — Jetson Thor, IGX

## Software

- [CUDA Ecosystem](software/cuda-ecosystem.md) — CUDA, CUDA-X, cuDNN, cuBLAS, TensorRT
- [NIM & NeMo](software/nim-nemo.md) — NIM microservices, NeMo framework, guardrails
- [Omniverse](software/omniverse.md) — Omniverse, OpenUSD, digital twins
- [Isaac & Cosmos](software/isaac-cosmos.md) — Isaac Sim, Isaac ROS, Cosmos world models
- [AI Enterprise](software/ai-enterprise.md) — AI Enterprise suite, RAPIDS, Triton
- [Domain-Specific Software](software/domain-specific.md) — cuLitho, Clara, BioNeMo, Earth-2

## Competitors

- [AMD](competitors/amd.md) — MI300X/MI350, ROCm, competitive position
- [Google TPU](competitors/google-tpu.md) — TPU v5/Trillium, JAX, Cloud TPU
- [Intel](competitors/intel.md) — Gaudi 3, Ponte Vecchio, oneAPI
- [Custom ASICs](competitors/custom-asics.md) — AWS Trainium, MS Maia, Google Axion
- [AI Software Landscape](competitors/ai-software-landscape.md) — Hugging Face, vLLM, PyTorch

## Markets

- [Data Center AI](markets/data-center-ai.md) — Training vs inference economics, cloud spend
- [Sovereign AI](markets/sovereign-ai.md) — Nation-state AI infrastructure
- [Automotive & AV](markets/automotive-av.md) — AV market, ADAS, partnerships
- [Robotics & Physical AI](markets/robotics-physical-ai.md) — Physical AI, humanoid robots
- [Gaming Market](markets/gaming-market.md) — GeForce, PC gaming dynamics
- [Edge & Enterprise](markets/edge-enterprise.md) — Edge AI, on-prem inference

## Concepts

- [Accelerated Computing](concepts/accelerated-computing.md) — The core thesis
- [Inference Economy](concepts/inference-economy.md) — Inference scaling, token economics
- [AI Factories](concepts/ai-factories.md) — Data factory + AI factory vision
- [Three Waves of AI](concepts/three-waves-of-ai.md) — Perception, generation, agentic
- [Physical AI](concepts/physical-ai.md) — AI with a body, simulation-to-reality
- [CUDA Moat](concepts/cuda-moat.md) — Install base dynamics, ecosystem lock-in
```

- [ ] **Step 3: Create log.md**

Write `wiki/log.md`:

```markdown
# Wiki Ingestion Log

Append-only record of wiki updates.

---

## [2026-04-09] Initial wiki creation

- Created wiki directory structure
- Created index.md with full page catalog
- Sources: NVIDIA official documentation, GTC 2025/2026 keynotes, CES 2026 keynote, Acquired FM interview, Lex Fridman #494, industry coverage
- Pages created: 27 (7 products, 6 software, 5 competitors, 6 markets, 6 concepts)
```

- [ ] **Step 4: Commit scaffolding**

```bash
git add wiki/index.md wiki/log.md
git commit -m "feat: add wiki scaffolding — index, log, directory structure"
```

---

## Task 2: Product Pages — GPU Architectures

**Files:**
- Create: `wiki/products/gpu-blackwell.md`
- Create: `wiki/products/gpu-hopper.md`
- Create: `wiki/products/gpu-gaming.md`

**Research required:** Use WebFetch/WebSearch to get current specs for Blackwell (B200, GB200, GB200 NVL72, B100), Hopper (H100, H200, GH200), and GeForce RTX 50-series. Key data points needed:
- Transistor counts, process nodes, memory type/capacity/bandwidth
- FP8/FP4 throughput, TDP
- Key architectural innovations (transformer engine, NVLink generations)
- Pricing tiers where public
- DLSS version, ray tracing gen for gaming

- [ ] **Step 1: Research Blackwell architecture**

Search for: "NVIDIA Blackwell B200 GB200 specs architecture 2025 2026". Fetch NVIDIA's official Blackwell page and recent tech coverage. Extract: transistor count, process node, memory (HBM3e), NVLink 5th gen bandwidth, FP4/FP8 TFLOPS, GB200 NVL72 rack-scale specs, key innovations (second-gen transformer engine, RAS engine, decompression engine).

- [ ] **Step 2: Research Hopper architecture**

Search for: "NVIDIA Hopper H100 H200 GH200 specs". Extract: 80B transistors, TSMC 4N, 80GB/141GB HBM3/HBM3e, FP8 performance, transformer engine gen 1, NVLink 4th gen, grace-hopper superchip details.

- [ ] **Step 3: Research GeForce RTX 50-series**

Search for: "NVIDIA RTX 5090 5080 5070 specs DLSS 4 2025". Extract: Blackwell gaming architecture, DLSS 4 (multi-frame generation), specs for 5090/5080/5070/5060, pricing, neural rendering capabilities.

- [ ] **Step 4: Write gpu-blackwell.md**

Write `wiki/products/gpu-blackwell.md` following the page template. Include:
- What It Is: Blackwell as the successor to Hopper, purpose-built for the inference economy and trillion-parameter models
- Key Facts: All specs from research
- Strategic Significance: Connect to inference economy thesis, AI factory vision, rack-scale thinking (GB200 NVL72 as a single GPU), NVLink as moat
- How It Connects: Link to `gpu-hopper.md`, `../competitors/amd.md`, `../concepts/inference-economy.md`, `../markets/data-center-ai.md`, `dgx-systems.md`
- Jensen's Framing: Quotes from GTC 2025 keynote on Blackwell, "the engine of the AI factory"

- [ ] **Step 5: Write gpu-hopper.md**

Write `wiki/products/gpu-hopper.md` following the page template. Include:
- What It Is: The architecture that powered the generative AI revolution, the workhorse of AI training
- Key Facts: H100 specs, H200 (memory upgrade), GH200 (grace-hopper superchip)
- Strategic Significance: First architecture with transformer engine — purpose-built for LLM workloads, established NVIDIA's dominance in the AI training market
- How It Connects: Link to `gpu-blackwell.md` (successor), `../software/cuda-ecosystem.md`, `../competitors/amd.md`, `../markets/data-center-ai.md`
- Jensen's Framing: How Jensen positioned Hopper as the inflection point for generative AI

- [ ] **Step 6: Write gpu-gaming.md**

Write `wiki/products/gpu-gaming.md` following the page template. Include:
- What It Is: GeForce RTX 50-series based on Blackwell gaming architecture, DLSS 4 with multi-frame generation, neural rendering
- Key Facts: RTX 5090/5080/5070 specs, pricing, DLSS 4 capabilities
- Strategic Significance: Gaming as the install base play — CUDA on every GeForce, neural rendering as the bridge between gaming and AI, GeForce revenue funding R&D
- How It Connects: Link to `../concepts/cuda-moat.md` (install base), `../markets/gaming-market.md`
- Jensen's Framing: "CUDA on GeForce" as the original platform bet, gaming as the flywheel that funded the AI stack

- [ ] **Step 7: Commit GPU architecture pages**

```bash
git add wiki/products/gpu-blackwell.md wiki/products/gpu-hopper.md wiki/products/gpu-gaming.md
git commit -m "feat: add GPU architecture wiki pages — Blackwell, Hopper, gaming"
```

---

## Task 3: Product Pages — Systems, Networking, Automotive, Robotics

**Files:**
- Create: `wiki/products/dgx-systems.md`
- Create: `wiki/products/networking.md`
- Create: `wiki/products/drive-platform.md`
- Create: `wiki/products/robotics-platforms.md`

**Research required:** Use WebFetch/WebSearch for:
- DGX B200, DGX SuperPOD, DGX Cloud specs and pricing
- ConnectX-7, Spectrum-X, NVLink 5th gen, NVSwitch specs
- DRIVE Thor, DRIVE Orin, Hyperion architecture, automotive partnerships
- Jetson Thor, IGX Orin, Isaac Nova Orin reference platforms

- [ ] **Step 1: Research DGX systems**

Search for: "NVIDIA DGX B200 SuperPOD DGX Cloud 2025 2026 specs". Extract: DGX B200 config (8x B200), SuperPOD (rack-scale), DGX Cloud partnerships (Azure, GCP, Oracle), pricing model, performance claims.

- [ ] **Step 2: Research networking products**

Search for: "NVIDIA ConnectX-7 Spectrum-X NVLink NVSwitch 2025 2026". Extract: ConnectX-7 (400Gb/s InfiniBand/Ethernet), Spectrum-X (Ethernet for AI), NVLink 5th gen bandwidth (1.8TB/s), NVSwitch specs, Quantum InfiniBand switches.

- [ ] **Step 3: Research DRIVE platform**

Search for: "NVIDIA DRIVE Thor Orin Hyperion automotive 2025 2026". Extract: DRIVE Thor (next-gen SoC, 2000 TOPS), DRIVE Orin (current gen, 254 TOPS), Hyperion sensor platform, automotive partnerships (Mercedes, JLR, BYD, Volvo, etc.), DRIVE Sim.

- [ ] **Step 4: Research robotics platforms**

Search for: "NVIDIA Jetson Thor IGX Isaac Nova 2025 2026". Extract: Jetson Thor (next-gen robotics SoC), IGX Orin (industrial edge), Isaac Nova Orin reference robot, Project GR00T humanoid foundation model.

- [ ] **Step 5: Write dgx-systems.md**

Write `wiki/products/dgx-systems.md` following the page template.
- What It Is: The AI factory in a box. DGX is how NVIDIA sells compute as a complete system, not just chips.
- Key Facts: DGX B200 specs, SuperPOD config, DGX Cloud model
- Strategic Significance: Stack thinking — DGX is NVIDIA owning the full stack from chip to system to cloud. Moves NVIDIA from component seller to systems company. Higher margins, deeper lock-in.
- How It Connects: `gpu-blackwell.md`, `networking.md`, `../concepts/ai-factories.md`, `../markets/data-center-ai.md`
- Jensen's Framing: "The AI factory" — GTC 2025/2026 keynote framing

- [ ] **Step 6: Write networking.md**

Write `wiki/products/networking.md` following the page template.
- What It Is: Post-Mellanox networking stack — the connective tissue of the AI factory
- Key Facts: ConnectX-7, Spectrum-X, NVLink 5, NVSwitch, Quantum switches
- Strategic Significance: Amdahl's Law — networking is the bottleneck in distributed training/inference. Mellanox acquisition was Jensen's stack thinking in action. Spectrum-X extends from InfiniBand-only to Ethernet, massively expanding TAM.
- How It Connects: `dgx-systems.md`, `gpu-blackwell.md`, `../concepts/accelerated-computing.md`
- Jensen's Framing: "Data centers are defined by I/O, not processors" — Mellanox rationale

- [ ] **Step 7: Write drive-platform.md**

Write `wiki/products/drive-platform.md` following the page template.
- What It Is: End-to-end autonomous driving platform — SoC + software + simulation
- Key Facts: DRIVE Thor/Orin specs, Hyperion sensor suite, key partnerships, DRIVE Sim
- Strategic Significance: Zero-billion-dollar market play in autonomous driving. Platform (not chip) approach — NVIDIA sells the full AV stack. Simulation (DRIVE Sim via Omniverse) is the moat: synthetic data > real-world data for edge cases.
- How It Connects: `../software/omniverse.md`, `../software/isaac-cosmos.md`, `../markets/automotive-av.md`, `../concepts/physical-ai.md`
- Jensen's Framing: "Physical AI" framing from GTC 2025/2026

- [ ] **Step 8: Write robotics-platforms.md**

Write `wiki/products/robotics-platforms.md` following the page template.
- What It Is: Hardware platforms for embodied AI — from industrial edge to humanoid robots
- Key Facts: Jetson Thor specs, IGX Orin, Isaac Nova Orin, Project GR00T
- Strategic Significance: The "next frontier" after digital AI. Jensen's thesis: every robot needs a brain, and NVIDIA wants to be that brain. Platform play — Jetson is the "CUDA for robots." GR00T is the foundation model play for humanoids.
- How It Connects: `../software/isaac-cosmos.md`, `../concepts/physical-ai.md`, `../markets/robotics-physical-ai.md`, `drive-platform.md`
- Jensen's Framing: "We have digital agents. Now we have physically embodied agents. We call them robots." — GTC 2026

- [ ] **Step 9: Commit systems/networking/auto/robotics pages**

```bash
git add wiki/products/dgx-systems.md wiki/products/networking.md wiki/products/drive-platform.md wiki/products/robotics-platforms.md
git commit -m "feat: add product wiki pages — DGX, networking, DRIVE, robotics"
```

---

## Task 4: Software Pages

**Files:**
- Create: `wiki/software/cuda-ecosystem.md`
- Create: `wiki/software/nim-nemo.md`
- Create: `wiki/software/omniverse.md`
- Create: `wiki/software/isaac-cosmos.md`
- Create: `wiki/software/ai-enterprise.md`
- Create: `wiki/software/domain-specific.md`

**Research required:** Use WebFetch/WebSearch for:
- CUDA toolkit version, CUDA-X library catalog, cuDNN/cuBLAS/TensorRT versions
- NIM microservice catalog, NeMo framework features, NeMo Guardrails
- Omniverse Cloud, OpenUSD adoption, digital twin deployments
- Isaac Sim latest, Isaac ROS, Cosmos world foundation models
- AI Enterprise 5.x features, RAPIDS latest, Triton Inference Server
- cuLitho (TSMC/ASML partnerships), Clara (healthcare), BioNeMo (drug discovery), Earth-2 (climate)

- [ ] **Step 1: Research CUDA ecosystem**

Search for: "NVIDIA CUDA toolkit 2025 2026 CUDA-X libraries cuDNN TensorRT latest". Extract: CUDA toolkit version, number of CUDA-X libraries (400+), cuDNN version, TensorRT-LLM features, developer ecosystem size (4M+ developers), key library categories.

- [ ] **Step 2: Research NIM and NeMo**

Search for: "NVIDIA NIM microservices NeMo framework 2025 2026". Extract: NIM concept (pre-built inference microservices), NIM catalog contents (LLMs, vision, speech), NeMo framework for custom model training, NeMo Guardrails for safety, deployment model.

- [ ] **Step 3: Research Omniverse**

Search for: "NVIDIA Omniverse Cloud OpenUSD digital twins 2025 2026". Extract: Omniverse as simulation platform, OpenUSD foundation, Omniverse Cloud, key industry deployments (BMW, Siemens, etc.), connection to Isaac Sim and DRIVE Sim.

- [ ] **Step 4: Research Isaac and Cosmos**

Search for: "NVIDIA Isaac Sim Cosmos world foundation models 2025 2026". Extract: Isaac Sim for robot simulation, Isaac ROS for deployment, Cosmos world foundation models (what they are, how they work), simulation-to-reality pipeline.

- [ ] **Step 5: Research AI Enterprise and domain-specific software**

Search for: "NVIDIA AI Enterprise RAPIDS Triton 2025 2026" and "NVIDIA cuLitho Clara BioNeMo Earth-2 2025 2026". Extract: AI Enterprise suite components, RAPIDS for data science, Triton Inference Server features, cuLitho (computational lithography with TSMC/ASML), Clara for healthcare imaging, BioNeMo for drug discovery, Earth-2 for climate simulation.

- [ ] **Step 6: Write cuda-ecosystem.md**

Write `wiki/software/cuda-ecosystem.md` following the page template. Freshness: **evergreen** (the ecosystem story is structural, though version numbers are quarterly).
- What It Is: The software platform moat. CUDA + 400+ acceleration libraries that make NVIDIA GPUs programmable for every workload.
- Key Facts: CUDA toolkit version, 4M+ developers, key CUDA-X libraries by category, TensorRT-LLM for inference optimization
- Strategic Significance: THE moat. Install base dynamics — CUDA on every GPU, developers build on CUDA, libraries compound, switching costs grow. This is the flywheel that makes "just build a better chip" an insufficient competitive strategy.
- How It Connects: `../concepts/cuda-moat.md`, `../competitors/amd.md` (ROCm comparison), `../products/gpu-blackwell.md`
- Jensen's Framing: "Install base defines an architecture" — Acquired FM. The CUDA ecosystem is why a 10% faster competitor chip doesn't matter.

- [ ] **Step 7: Write nim-nemo.md**

Write `wiki/software/nim-nemo.md` following the page template. Freshness: **quarterly**.
- What It Is: NVIDIA's inference-as-a-service layer. NIM packages optimized models as microservices; NeMo provides the training/customization framework.
- Key Facts: NIM catalog, deployment options, NeMo Guardrails, enterprise licensing
- Strategic Significance: Platform play for inference. NIM makes NVIDIA the default deployment path for AI models — not just the training hardware. This captures the inference economy that Jensen predicts is 100x training.
- How It Connects: `../concepts/inference-economy.md`, `ai-enterprise.md`, `../markets/data-center-ai.md`
- Jensen's Framing: Inference as the permanent compute economy — GTC 2026

- [ ] **Step 8: Write omniverse.md**

Write `wiki/software/omniverse.md` following the page template. Freshness: **quarterly**.
- What It Is: Simulation and digital twin platform built on OpenUSD. The "third computer" in Jensen's framework.
- Key Facts: Omniverse Cloud, OpenUSD standard, industry deployments, connection to Isaac Sim and DRIVE Sim
- Strategic Significance: The simulation computer. Jensen's "three computers" framework: training computer, simulation computer, deployment computer. Omniverse IS the simulation computer. Digital twins create a flywheel: simulate → optimize → deploy → collect data → improve simulation.
- How It Connects: `isaac-cosmos.md`, `../products/drive-platform.md`, `../concepts/physical-ai.md`, `../concepts/ai-factories.md`
- Jensen's Framing: "Three computers" — GTC 2025

- [ ] **Step 9: Write isaac-cosmos.md**

Write `wiki/software/isaac-cosmos.md` following the page template. Freshness: **quarterly**.
- What It Is: Robot simulation (Isaac) and world foundation models (Cosmos) — the software stack for physical AI.
- Key Facts: Isaac Sim features, Isaac ROS, Cosmos world models (video prediction, physics understanding), simulation-to-reality pipeline
- Strategic Significance: This is how Jensen makes the physical AI thesis real. Cosmos models "reason about edge scenarios, break them down into familiar physical interactions." Isaac + Cosmos + Omniverse = complete pipeline from simulation to deployed robot.
- How It Connects: `omniverse.md`, `../products/robotics-platforms.md`, `../concepts/physical-ai.md`, `../markets/robotics-physical-ai.md`
- Jensen's Framing: "AI that understands friction, inertia, cause and effect" — GTC 2025. Cosmos at CES 2026.

- [ ] **Step 10: Write ai-enterprise.md**

Write `wiki/software/ai-enterprise.md` following the page template. Freshness: **quarterly**.
- What It Is: Enterprise software suite that packages NVIDIA's AI stack for production deployment. RAPIDS for data science, Triton for inference serving, plus enterprise support and certification.
- Key Facts: AI Enterprise components, RAPIDS library set, Triton Inference Server features, certified platforms, pricing model
- Strategic Significance: Enterprise software revenue stream. Moves NVIDIA from hardware-only to recurring software revenue. Also deepens lock-in: enterprises that deploy on AI Enterprise have high switching costs.
- How It Connects: `nim-nemo.md`, `cuda-ecosystem.md`, `../markets/edge-enterprise.md`, `../markets/data-center-ai.md`
- Jensen's Framing: Software as the multiplier on hardware value

- [ ] **Step 11: Write domain-specific.md**

Write `wiki/software/domain-specific.md` following the page template. Freshness: **quarterly**.
- What It Is: Vertical-specific software platforms — cuLitho (semiconductor lithography), Clara (healthcare), BioNeMo (drug discovery), Earth-2 (climate simulation).
- Key Facts: cuLitho partnership with TSMC/ASML (40-60x speedup), Clara medical imaging, BioNeMo protein/molecule models, Earth-2 digital twin of earth
- Strategic Significance: Zero-billion-dollar market plays in each vertical. Each is a platform bet: NVIDIA provides the simulation/AI infrastructure, the industry builds on top. cuLitho is especially strategic — it makes NVIDIA essential to the semiconductor manufacturing process itself.
- How It Connects: `../concepts/accelerated-computing.md`, `omniverse.md`
- Jensen's Framing: Each of these is Jensen's "zero-billion-dollar market" reasoning in action

- [ ] **Step 12: Commit software pages**

```bash
git add wiki/software/cuda-ecosystem.md wiki/software/nim-nemo.md wiki/software/omniverse.md wiki/software/isaac-cosmos.md wiki/software/ai-enterprise.md wiki/software/domain-specific.md
git commit -m "feat: add software wiki pages — CUDA, NIM/NeMo, Omniverse, Isaac/Cosmos, AI Enterprise, domain-specific"
```

---

## Task 5: Competitor Pages

**Files:**
- Create: `wiki/competitors/amd.md`
- Create: `wiki/competitors/google-tpu.md`
- Create: `wiki/competitors/intel.md`
- Create: `wiki/competitors/custom-asics.md`
- Create: `wiki/competitors/ai-software-landscape.md`

**Research required:** Use WebFetch/WebSearch for:
- AMD MI300X/MI325X/MI350 specs, ROCm state, market share, roadmap
- Google TPU v5e/v5p/Trillium specs, JAX ecosystem, Cloud TPU availability
- Intel Gaudi 3 specs, Ponte Vecchio status, oneAPI adoption, roadmap (Falcon Shores)
- AWS Trainium2/Inferentia2, Microsoft Maia 100, Google Axion — specs, availability, strategy
- Hugging Face ecosystem, vLLM adoption, PyTorch vs JAX landscape, open-source inference stacks

- [ ] **Step 1: Research AMD competitive position**

Search for: "AMD MI300X MI350 ROCm 2025 2026 vs NVIDIA". Extract: MI300X specs (192GB HBM3, 153 TFLOPS FP16), MI325X, MI350 roadmap, ROCm software maturity vs CUDA, adoption by hyperscalers, market share estimates, AMD strategy.

- [ ] **Step 2: Research Google TPU**

Search for: "Google TPU v5 Trillium 2025 2026 specs Cloud TPU". Extract: TPU v5e/v5p specs, Trillium (TPU v6) specs, JAX framework adoption, Cloud TPU pricing, who uses TPUs (Google internal, Anthropic, etc.), how TPUs compete with NVIDIA.

- [ ] **Step 3: Research Intel AI accelerators**

Search for: "Intel Gaudi 3 Falcon Shores 2025 2026". Extract: Gaudi 3 specs, Intel's pivot from Ponte Vecchio, oneAPI adoption (or lack thereof), Falcon Shores roadmap, Intel's competitive position.

- [ ] **Step 4: Research custom ASICs**

Search for: "AWS Trainium2 Microsoft Maia Google Axion custom AI chips 2025 2026". Extract: Trainium2 specs and availability, Maia 100 specs and Azure deployment, Google Axion (Arm-based), strategy behind hyperscaler custom silicon (cost control, supply diversification, negotiating leverage vs NVIDIA).

- [ ] **Step 5: Research AI software landscape**

Search for: "Hugging Face vLLM PyTorch open source AI inference stack 2025 2026". Extract: Hugging Face model hub size and ecosystem, vLLM adoption for inference, PyTorch vs JAX landscape, TensorRT-LLM vs vLLM benchmarks, open-source alternatives to NVIDIA's software stack.

- [ ] **Step 6: Write amd.md**

Write `wiki/competitors/amd.md` following the page template. Freshness: **quarterly**.
- What It Is: NVIDIA's closest direct competitor in AI accelerators. MI300X is AMD's Hopper competitor; MI350 targets Blackwell.
- Key Facts: MI300X/MI325X/MI350 specs, ROCm maturity, hyperscaler adoption, market share
- Strategic Significance: Through Jensen's lens — AMD competes at the chip layer but lacks the stack. ROCm is years behind CUDA in ecosystem depth. Jensen's "stack vs stack, not product vs product" framework: even if MI300X matches H100 on raw specs, the CUDA ecosystem moat means customers don't switch. AMD's real threat is if ROCm reaches "good enough" for hyperscalers who want supply diversification.
- How It Connects: `../products/gpu-blackwell.md`, `../products/gpu-hopper.md`, `../software/cuda-ecosystem.md`, `../concepts/cuda-moat.md`
- Jensen's Framing: "It's not about the chip... it's the chip, the programming model, and a whole bunch of software" — apply to AMD comparison

- [ ] **Step 7: Write google-tpu.md**

Write `wiki/competitors/google-tpu.md` following the page template. Freshness: **quarterly**.
- What It Is: Google's custom AI accelerator, purpose-built for their workloads. Different competitive dynamic than AMD — Google builds for itself first, cloud customers second.
- Key Facts: TPU v5/Trillium specs, JAX ecosystem, Cloud TPU availability, key users
- Strategic Significance: Through Jensen's lens — TPUs are the custom ASIC play. They optimize for Google's specific workloads (training large models, Search inference). The weakness: limited ecosystem outside Google. JAX adoption is growing but PyTorch + CUDA dominates. The real question: does Google's vertical integration (TPU + JAX + own models) create a competing stack, or does it fragment the market?
- How It Connects: `custom-asics.md`, `../software/cuda-ecosystem.md`, `../concepts/cuda-moat.md`
- Jensen's Framing: Vertical integration vs horizontal platform — Jensen would analyze this as a product (Google's needs) vs platform (NVIDIA serves everyone) dynamic

- [ ] **Step 8: Write intel.md**

Write `wiki/competitors/intel.md` following the page template. Freshness: **quarterly**.
- What It Is: Intel's AI accelerator efforts — Gaudi (from Habana Labs acquisition) and the troubled Ponte Vecchio/Falcon Shores roadmap.
- Key Facts: Gaudi 3 specs, Ponte Vecchio status, oneAPI adoption, Falcon Shores timeline
- Strategic Significance: Through Jensen's lens — Intel's AI story is a cautionary tale of trying to enter a market where the incumbent owns the stack. oneAPI can't replicate CUDA's ecosystem. Gaudi gets hyperscaler trials on price, but the software gap prevents deep adoption. Jensen's commodity test applies: if Intel is competing on price, they're playing the commodity game.
- How It Connects: `amd.md`, `../software/cuda-ecosystem.md`, `../concepts/cuda-moat.md`
- Jensen's Framing: "Are other people already doing this?" — Intel entered GPU computing late, into an established CUDA ecosystem

- [ ] **Step 9: Write custom-asics.md**

Write `wiki/competitors/custom-asics.md` following the page template. Freshness: **quarterly**.
- What It Is: Hyperscaler custom silicon — AWS Trainium/Inferentia, Microsoft Maia, Google Axion. Cloud providers building their own chips.
- Key Facts: Trainium2 specs, Maia 100 specs, Axion specs, deployment status, availability
- Strategic Significance: Through Jensen's lens — this is the real competitive threat, not AMD. Hyperscalers have: (1) captive demand, (2) deep pockets, (3) motivation to reduce NVIDIA dependency. BUT: they face the same ecosystem problem. Custom ASICs work for specific workloads (internal inference) but can't match CUDA's generality. Jensen's platform vs product test: custom ASICs are products (solve one workload), NVIDIA is the platform (solves all workloads).
- How It Connects: `google-tpu.md`, `../software/cuda-ecosystem.md`, `../concepts/cuda-moat.md`, `../markets/data-center-ai.md`
- Jensen's Framing: "The rich developer ecosystem is really valued, and really, really deeply appreciated" — even hyperscalers building custom chips still support CUDA

- [ ] **Step 10: Write ai-software-landscape.md**

Write `wiki/competitors/ai-software-landscape.md` following the page template. Freshness: **quarterly**.
- What It Is: The open-source and third-party software ecosystem that could disintermediate NVIDIA's software stack.
- Key Facts: Hugging Face model hub stats, vLLM vs TensorRT-LLM benchmarks, PyTorch dominance, JAX growth, open-source inference alternatives
- Strategic Significance: Through Jensen's lens — this is the "layer above" competition. If Hugging Face + vLLM become the default deployment stack and they abstract away hardware, NVIDIA's software moat weakens. Jensen's stack thinking: NVIDIA needs to own value at the software layer (hence NIM, TensorRT-LLM) to prevent commoditization at the hardware layer.
- How It Connects: `../software/nim-nemo.md`, `../software/cuda-ecosystem.md`, `../concepts/cuda-moat.md`
- Jensen's Framing: Stack thinking — if you don't own the software layer, someone else will, and they'll commoditize your hardware

- [ ] **Step 11: Commit competitor pages**

```bash
git add wiki/competitors/amd.md wiki/competitors/google-tpu.md wiki/competitors/intel.md wiki/competitors/custom-asics.md wiki/competitors/ai-software-landscape.md
git commit -m "feat: add competitor wiki pages — AMD, Google TPU, Intel, custom ASICs, AI software"
```

---

## Task 6: Market Pages

**Files:**
- Create: `wiki/markets/data-center-ai.md`
- Create: `wiki/markets/sovereign-ai.md`
- Create: `wiki/markets/automotive-av.md`
- Create: `wiki/markets/robotics-physical-ai.md`
- Create: `wiki/markets/gaming-market.md`
- Create: `wiki/markets/edge-enterprise.md`

**Research required:** Use WebFetch/WebSearch for:
- Data center AI market size, training vs inference split, cloud capex trends, NVIDIA data center revenue
- Sovereign AI initiatives (countries building national AI infrastructure), NVIDIA sovereign AI partnerships
- Autonomous vehicle market, ADAS adoption, NVIDIA automotive revenue and partnerships
- Robotics market (industrial, warehouse, humanoid), physical AI investment trends
- PC gaming market, GeForce market share, GPU pricing trends
- Edge AI market, enterprise on-prem inference trends

- [ ] **Step 1: Research data center AI market**

Search for: "NVIDIA data center revenue 2025 2026 training inference market AI capex". Extract: NVIDIA data center revenue trajectory, training vs inference revenue split, hyperscaler capex trends (Microsoft, Google, Amazon, Meta spending), total addressable market estimates.

- [ ] **Step 2: Research sovereign AI**

Search for: "NVIDIA sovereign AI partnerships 2025 2026 countries national AI". Extract: Which countries are building sovereign AI infrastructure, NVIDIA's role (DGX systems, partnerships), key deals (France, India, Japan, Singapore, UAE, etc.), the strategic framing.

- [ ] **Step 3: Research automotive and robotics markets**

Search for: "NVIDIA automotive revenue partnerships AV market 2025 2026" and "robotics humanoid robot market physical AI investment 2025 2026". Extract: NVIDIA automotive revenue, key AV partnerships, ADAS adoption curve, humanoid robot companies (Figure, 1X, Agility, Tesla Bot), physical AI investment trends.

- [ ] **Step 4: Research gaming and edge markets**

Search for: "PC gaming market GPU market share NVIDIA 2025 2026" and "edge AI enterprise inference on-prem market 2025 2026". Extract: PC gaming market size, NVIDIA GeForce market share vs AMD, GPU ASP trends, edge AI adoption, enterprise inference deployment patterns.

- [ ] **Step 5: Write data-center-ai.md**

Write `wiki/markets/data-center-ai.md` following the page template. Freshness: **fast-moving**.
- What It Is: The core market. Data center AI encompasses training and inference infrastructure at hyperscalers, cloud providers, and enterprises.
- Key Facts: Revenue figures, market size, training vs inference split, capex trends, key customers
- Strategic Significance: Jensen's thesis: inference demand will be 100x training. The market is shifting from "build the model" (training) to "run the model at scale" (inference). This is why Blackwell is optimized for inference. The AI factory vision: every company becomes an AI company, every data center becomes an AI factory.
- How It Connects: `../products/gpu-blackwell.md`, `../products/dgx-systems.md`, `../concepts/inference-economy.md`, `../concepts/ai-factories.md`, `../competitors/amd.md`
- Jensen's Framing: "100x inference demand" — GTC 2025. "AI factory" — GTC 2026.

- [ ] **Step 6: Write sovereign-ai.md**

Write `wiki/markets/sovereign-ai.md` following the page template. Freshness: **fast-moving**.
- What It Is: Nation-states building their own AI infrastructure for data sovereignty, national security, and economic competitiveness.
- Key Facts: Countries with sovereign AI programs, NVIDIA partnerships, DGX system deployments, revenue from sovereign AI
- Strategic Significance: A new market Jensen identified early. Every nation wants its own AI — can't rely on US hyperscalers for national intelligence. This multiplies NVIDIA's TAM beyond just big tech. Also diversifies customer base away from hyperscaler concentration risk.
- How It Connects: `../products/dgx-systems.md`, `data-center-ai.md`
- Jensen's Framing: Sovereign AI as a "zero-billion-dollar market" that is rapidly emerging

- [ ] **Step 7: Write automotive-av.md**

Write `wiki/markets/automotive-av.md` following the page template. Freshness: **quarterly**.
- What It Is: Autonomous driving and ADAS market — NVIDIA as platform provider for the automotive AI stack.
- Key Facts: NVIDIA automotive revenue, pipeline, key partnerships, ADAS adoption rates, regulatory landscape
- Strategic Significance: Long-term platform play. Automotive is a slow-moving market (7-year design cycles) but the platform economics are Jensen's favorite: design win → multi-year revenue stream → ecosystem lock-in. Every car with NVIDIA silicon is an install base node.
- How It Connects: `../products/drive-platform.md`, `../software/omniverse.md`, `../concepts/physical-ai.md`
- Jensen's Framing: Physical AI applied to transportation. Simulation (DRIVE Sim) as the key advantage — you can't test AVs in the real world fast enough.

- [ ] **Step 8: Write robotics-physical-ai.md**

Write `wiki/markets/robotics-physical-ai.md` following the page template. Freshness: **quarterly**.
- What It Is: The emerging market for AI-powered robots — industrial, warehouse, humanoid, and general-purpose.
- Key Facts: Key companies, investment levels, NVIDIA's position (Jetson, Isaac, Cosmos, GR00T), humanoid robot landscape
- Strategic Significance: Jensen's biggest "zero-billion-dollar market" bet since CUDA. His reasoning chain: (1) AI learns to understand the physical world (Cosmos), (2) robots need brains (Jetson), (3) robots need simulation (Isaac + Omniverse), (4) NVIDIA provides the full stack. The market is pre-revenue but the conditions are emerging rapidly.
- How It Connects: `../products/robotics-platforms.md`, `../software/isaac-cosmos.md`, `../concepts/physical-ai.md`
- Jensen's Framing: "The next big thing is Physical AI, AI with a body" — GTC Paris

- [ ] **Step 9: Write gaming-market.md**

Write `wiki/markets/gaming-market.md` following the page template. Freshness: **quarterly**.
- What It Is: PC gaming GPU market — NVIDIA's original business and still a major revenue segment.
- Key Facts: GeForce market share, gaming revenue, RTX adoption rates, DLSS adoption, pricing trends, competitive dynamics vs AMD
- Strategic Significance: Gaming is the install base flywheel. Every GeForce ships with CUDA. Gaming funds R&D that advances data center products. DLSS/neural rendering is the bridge between gaming and AI — the same tensor cores that run LLMs also run DLSS.
- How It Connects: `../products/gpu-gaming.md`, `../concepts/cuda-moat.md`
- Jensen's Framing: "CUDA on every GeForce" — the original platform bet

- [ ] **Step 10: Write edge-enterprise.md**

Write `wiki/markets/edge-enterprise.md` following the page template. Freshness: **quarterly**.
- What It Is: Enterprise AI deployment at the edge and on-premises — inference outside the cloud.
- Key Facts: Edge AI market size, enterprise on-prem inference trends, NVIDIA IGX/Jetson deployments, AI Enterprise software attach rate
- Strategic Significance: The "last mile" of Jensen's AI factory vision. Not every workload goes to the cloud — manufacturing, healthcare, retail, telco all need local inference. NVIDIA's play: Jetson/IGX for hardware + AI Enterprise for software = recurring revenue at the edge.
- How It Connects: `../products/robotics-platforms.md`, `../software/ai-enterprise.md`, `../concepts/ai-factories.md`
- Jensen's Framing: AI factories are not just hyperscaler data centers — every enterprise becomes an AI factory

- [ ] **Step 11: Commit market pages**

```bash
git add wiki/markets/data-center-ai.md wiki/markets/sovereign-ai.md wiki/markets/automotive-av.md wiki/markets/robotics-physical-ai.md wiki/markets/gaming-market.md wiki/markets/edge-enterprise.md
git commit -m "feat: add market wiki pages — data center, sovereign AI, automotive, robotics, gaming, edge"
```

---

## Task 7: Concept Pages

**Files:**
- Create: `wiki/concepts/accelerated-computing.md`
- Create: `wiki/concepts/inference-economy.md`
- Create: `wiki/concepts/ai-factories.md`
- Create: `wiki/concepts/three-waves-of-ai.md`
- Create: `wiki/concepts/physical-ai.md`
- Create: `wiki/concepts/cuda-moat.md`

**Research required:** Lighter research needed here — most concepts are well-documented in existing `references/` files and GTC keynotes. Use WebFetch/WebSearch for latest framing and data points.

- [ ] **Step 1: Research latest concept framing**

Search for: "NVIDIA accelerated computing thesis 2026", "inference economy scaling laws 2026", "NVIDIA AI factory vision 2026", "physical AI NVIDIA 2026". Extract latest data points, framing shifts, and new examples Jensen has used.

- [ ] **Step 2: Write accelerated-computing.md**

Write `wiki/concepts/accelerated-computing.md` following the page template. Freshness: **evergreen**.
- What It Is: Jensen's foundational thesis — general-purpose computing hit a wall (end of Moore's Law for single-thread performance), and the future belongs to domain-specific acceleration. Every workload that can be parallelized should be.
- Key Facts: CPU vs GPU performance divergence, accelerated computing adoption curve, CUDA-X library count, workloads that have been accelerated (AI, HPC, graphics, genomics, drug discovery, climate, EDA)
- Strategic Significance: This IS Jensen's essence — the one governing force. Everything NVIDIA does flows from this thesis. It's why NVIDIA exists as a $2T+ company.
- How It Connects: `cuda-moat.md`, `inference-economy.md`, `../software/cuda-ecosystem.md`
- Jensen's Framing: "The more you buy, the more you save" — accelerated computing is cheaper than general-purpose for parallelizable workloads. This is the core pitch.

- [ ] **Step 3: Write inference-economy.md**

Write `wiki/concepts/inference-economy.md` following the page template. Freshness: **evergreen** (the thesis is structural, though data points are fast-moving).
- What It Is: Jensen's prediction that inference compute demand will be 100x training. As AI moves from research to production, the dominant workload shifts from training models to running them at scale.
- Key Facts: Training vs inference compute ratio, token economics, reasoning model compute multipliers (chain-of-thought = more tokens = more compute), inference optimization techniques
- Strategic Significance: This thesis drives NVIDIA's product strategy — Blackwell optimized for inference, NIM for inference deployment, TensorRT-LLM for inference optimization. If Jensen is right about 100x, the AI hardware market is far larger than current estimates.
- How It Connects: `../products/gpu-blackwell.md`, `../software/nim-nemo.md`, `../markets/data-center-ai.md`, `ai-factories.md`
- Jensen's Framing: "100x inference demand" — GTC 2025. "Chain-of-reasoning compute" — BG2 Pod.

- [ ] **Step 4: Write ai-factories.md**

Write `wiki/concepts/ai-factories.md` following the page template. Freshness: **evergreen**.
- What It Is: Jensen's "two factories" / "AI factory" framework. Traditional factories manufacture physical goods. AI factories manufacture intelligence — they take in data and produce tokens/predictions.
- Key Facts: The AI factory concept, "data factory + AI factory" framing, DGX as AI factory infrastructure, enterprise AI factory deployments
- Strategic Significance: This reframes NVIDIA's market. NVIDIA doesn't sell chips — it sells the machinery for intelligence manufacturing. Every company that deploys AI is building an AI factory, and NVIDIA provides the equipment.
- How It Connects: `../products/dgx-systems.md`, `inference-economy.md`, `../markets/data-center-ai.md`, `../markets/sovereign-ai.md`
- Jensen's Framing: "Two factories" — GTC 2025. "AI factory era" — GTC 2026.

- [ ] **Step 5: Write three-waves-of-ai.md**

Write `wiki/concepts/three-waves-of-ai.md` following the page template. Freshness: **evergreen**.
- What It Is: Jensen's framework for AI evolution: (1) Perception — AI learns to see/hear/read, (2) Generation — AI learns to create content, (3) Agentic — AI learns to act autonomously and reason.
- Key Facts: Timeline of each wave, key breakthroughs, current state (deep into generation, entering agentic), what "agentic" means specifically
- Strategic Significance: Each wave expands compute demand. Perception was training-heavy. Generation added inference demand. Agentic multiplies inference demand (agents reason in loops, consuming tokens continuously). Jensen's product strategy tracks these waves.
- How It Connects: `inference-economy.md`, `physical-ai.md`, `../markets/data-center-ai.md`
- Jensen's Framing: "Three waves of AI" — GTC 2025. "Three markets collapsing into one" — GTC 2026.

- [ ] **Step 6: Write physical-ai.md**

Write `wiki/concepts/physical-ai.md` following the page template. Freshness: **evergreen**.
- What It Is: AI that understands and interacts with the physical world — "AI with a body." The convergence of simulation, robotics, and foundation models.
- Key Facts: Definition (AI that understands friction, inertia, cause and effect), the simulation-to-reality pipeline, Cosmos world models, key application domains (robotics, autonomous driving, industrial)
- Strategic Significance: Jensen's next "zero-billion-dollar market" after digital AI. The reasoning chain: (1) AI must understand physics to act in the real world, (2) you can't train physical AI in the real world (too slow, too dangerous), (3) therefore you need simulation (Omniverse + Isaac + Cosmos), (4) NVIDIA owns the simulation stack, (5) therefore NVIDIA is positioned to own physical AI.
- How It Connects: `../software/isaac-cosmos.md`, `../software/omniverse.md`, `../products/robotics-platforms.md`, `../products/drive-platform.md`, `../markets/robotics-physical-ai.md`
- Jensen's Framing: "AI that understands friction, inertia, cause and effect" — GTC 2025. "The next big thing is Physical AI, AI with a body" — GTC Paris.

- [ ] **Step 7: Write cuda-moat.md**

Write `wiki/concepts/cuda-moat.md` following the page template. Freshness: **evergreen**.
- What It Is: The analysis of NVIDIA's competitive moat through the lens of install base dynamics, ecosystem lock-in, and platform economics.
- Key Facts: 4M+ CUDA developers, 400+ CUDA-X libraries, ecosystem switching costs, ROCm vs CUDA gap, historical analogy (x86 vs RISC, VHS vs Betamax)
- Strategic Significance: This is the meta-analysis that ties everything together. Jensen's entire competitive strategy rests on the CUDA moat. Hardware advantages are temporary (competitors can build faster chips). Ecosystem advantages are durable (competitors can't replicate 20 years of libraries, tools, courses, and developer muscle memory).
- How It Connects: `../software/cuda-ecosystem.md`, `../competitors/amd.md`, `../competitors/google-tpu.md`, `../competitors/custom-asics.md`, `accelerated-computing.md`
- Jensen's Framing: "Install base defines an architecture. Everything else is secondary." — Acquired FM. x86 vs RISC as the defining analogy.

- [ ] **Step 8: Commit concept pages**

```bash
git add wiki/concepts/accelerated-computing.md wiki/concepts/inference-economy.md wiki/concepts/ai-factories.md wiki/concepts/three-waves-of-ai.md wiki/concepts/physical-ai.md wiki/concepts/cuda-moat.md
git commit -m "feat: add concept wiki pages — accelerated computing, inference economy, AI factories, three waves, physical AI, CUDA moat"
```

---

## Task 8: Update SKILL.md with Knowledge Base Section

**Files:**
- Modify: `SKILL.md` (insert new section between REASONING LENSES and HOW TO CHALLENGE, approximately line 131)

- [ ] **Step 1: Read current SKILL.md to confirm insertion point**

Read `SKILL.md` and identify the exact location between the `## REASONING LENSES` section (ends around line 131) and the `## HOW TO CHALLENGE` section (starts around line 169).

- [ ] **Step 2: Insert KNOWLEDGE BASE section**

Add the following section to `SKILL.md` after the `---` that follows REASONING LENSES and before `## HOW TO CHALLENGE`:

```markdown
## KNOWLEDGE BASE

You have a structured knowledge base about NVIDIA products, software, competitors, and markets in the `wiki/` directory. This is your institutional memory — treat it like your last briefing packet.

### How to Use the Wiki
1. Before reasoning about any NVIDIA product, technology, or competitor — consult the relevant wiki page(s)
2. Use `wiki/index.md` to navigate to the right pages
3. Check `last_updated` in each page's YAML frontmatter
4. Compare against the freshness tier:
   - **evergreen** (12+ months): Structural truths — use directly
   - **quarterly** (~3 months): Product specs, competitive data — verify if past window
   - **fast-moving** (~2 weeks): Pricing, earnings, availability — always verify via web search
5. Follow cross-references between pages to build full context

### When to Search the Web
Use web search tools (when available) to fetch current data when:
- A wiki page is past its freshness window
- The user asks about something not covered in the wiki
- The user asks about "latest", "recent", "just announced", or "current"
- You need pricing, availability, revenue, or earnings data
- Competitive claims need current verification
- A new product or announcement may have occurred since the wiki was last updated

### After Searching
- Use the freshest information available for your reasoning
- If web data contradicts the wiki, trust the web data and note the discrepancy
- Note the vintage of your information: "As of [date]..."

### Handling Stale Information
- Never cite outdated product specs as current fact
- Never guess at numbers you don't have — say you'd need to verify
- Never confuse product generations (Hopper vs Blackwell vs Rubin)
- When uncertain about freshness, caveat: "My last briefing on this was [date]"
- Prefer structural reasoning (moats, flywheels, stack position) over point-in-time data (specific TFLOPs, exact pricing) when freshness is uncertain
```

- [ ] **Step 3: Commit SKILL.md update**

```bash
git add SKILL.md
git commit -m "feat: add KNOWLEDGE BASE section to SKILL.md with wiki usage and freshness instructions"
```

---

## Task 9: Update Web App System Prompt

**Files:**
- Modify: `virtual-jensen-web/app.py` (update SYSTEM_PROMPT, starting at line 48)

- [ ] **Step 1: Read current app.py to confirm SYSTEM_PROMPT location**

Read `virtual-jensen-web/app.py` and identify the SYSTEM_PROMPT string (starts at line 48, ends at line 233).

- [ ] **Step 2: Create condensed wiki knowledge block**

After all wiki pages are written (Tasks 2-7), compile a condensed knowledge block by extracting "What It Is" + key specs + "Strategic Significance" from each page, compressed to 2-3 sentences per page. This block gets appended to the end of SYSTEM_PROMPT, before the closing triple-quote.

Add the following to the SYSTEM_PROMPT in `app.py`, inserted just before the final `"""` (after the IMPORTANT RULES section):

```python
## NVIDIA KNOWLEDGE BASE (as of 2026-04-09)

This is your institutional memory. Use it as a starting point for product and competitive knowledge. When discussing specific numbers, specs, or recent events, note the vintage of your information.

### Products

**Blackwell GPU Architecture**: [Condensed from wiki/products/gpu-blackwell.md — 2-3 sentences covering key specs, positioning, and strategic significance]

**Hopper GPU Architecture**: [Condensed from wiki/products/gpu-hopper.md]

**GeForce & Gaming**: [Condensed from wiki/products/gpu-gaming.md]

**DGX Systems**: [Condensed from wiki/products/dgx-systems.md]

**Networking**: [Condensed from wiki/products/networking.md]

**DRIVE Platform**: [Condensed from wiki/products/drive-platform.md]

**Robotics Platforms**: [Condensed from wiki/products/robotics-platforms.md]

### Software Platforms

**CUDA Ecosystem**: [Condensed from wiki/software/cuda-ecosystem.md]

**NIM & NeMo**: [Condensed from wiki/software/nim-nemo.md]

**Omniverse**: [Condensed from wiki/software/omniverse.md]

**Isaac & Cosmos**: [Condensed from wiki/software/isaac-cosmos.md]

**AI Enterprise**: [Condensed from wiki/software/ai-enterprise.md]

**Domain-Specific**: [Condensed from wiki/software/domain-specific.md]

### Competitive Landscape

**AMD**: [Condensed from wiki/competitors/amd.md]

**Google TPU**: [Condensed from wiki/competitors/google-tpu.md]

**Intel**: [Condensed from wiki/competitors/intel.md]

**Custom ASICs**: [Condensed from wiki/competitors/custom-asics.md]

**AI Software Landscape**: [Condensed from wiki/competitors/ai-software-landscape.md]

### Market Dynamics

**Data Center AI**: [Condensed from wiki/markets/data-center-ai.md]

**Sovereign AI**: [Condensed from wiki/markets/sovereign-ai.md]

**Automotive & AV**: [Condensed from wiki/markets/automotive-av.md]

**Robotics & Physical AI**: [Condensed from wiki/markets/robotics-physical-ai.md]

**Gaming**: [Condensed from wiki/markets/gaming-market.md]

**Edge & Enterprise**: [Condensed from wiki/markets/edge-enterprise.md]

### Key Strategic Concepts

**Accelerated Computing Thesis**: [Condensed from wiki/concepts/accelerated-computing.md]

**Inference Economy**: [Condensed from wiki/concepts/inference-economy.md]

**AI Factories**: [Condensed from wiki/concepts/ai-factories.md]

**Three Waves of AI**: [Condensed from wiki/concepts/three-waves-of-ai.md]

**Physical AI**: [Condensed from wiki/concepts/physical-ai.md]

**CUDA Moat**: [Condensed from wiki/concepts/cuda-moat.md]

### Knowledge Freshness

This knowledge base was last updated 2026-04-09. For fast-moving topics (pricing, earnings, availability, latest announcements), note the vintage and caveat appropriately. Prefer structural reasoning over point-in-time data when uncertain about freshness.
```

**IMPORTANT**: The `[Condensed from ...]` placeholders above MUST be replaced with actual content extracted from the completed wiki pages. Each entry should be 2-3 sentences: what it is, key numbers, and strategic significance. Do not leave placeholders.

- [ ] **Step 3: Commit web app update**

```bash
git add virtual-jensen-web/app.py
git commit -m "feat: add NVIDIA knowledge base to web app system prompt"
```

---

## Task 10: Smoke Test

- [ ] **Step 1: Verify wiki structure**

```bash
cd /Users/lingq/Documents/jhh-skills/virtual-jensen
find wiki -name "*.md" | sort
```

Expected: 29 files (index.md, log.md, 7 products, 6 software, 5 competitors, 6 markets, 6 concepts).

- [ ] **Step 2: Verify all pages have correct frontmatter**

```bash
cd /Users/lingq/Documents/jhh-skills/virtual-jensen
for f in $(find wiki -name "*.md" -not -name "index.md" -not -name "log.md"); do
  echo "=== $f ==="
  head -5 "$f"
  echo ""
done
```

Expected: Every page starts with `---`, has `title`, `last_updated`, `freshness`, `category` fields.

- [ ] **Step 3: Verify cross-references**

```bash
cd /Users/lingq/Documents/jhh-skills/virtual-jensen
grep -r "See:" wiki/ --include="*.md" | head -20
```

Expected: Cross-references pointing to existing files.

- [ ] **Step 4: Verify SKILL.md has KNOWLEDGE BASE section**

```bash
grep -n "KNOWLEDGE BASE" SKILL.md
```

Expected: Section header found.

- [ ] **Step 5: Verify web app system prompt has knowledge block**

```bash
grep -n "NVIDIA KNOWLEDGE BASE" virtual-jensen-web/app.py
```

Expected: Section found in SYSTEM_PROMPT.

- [ ] **Step 6: Start web app and test**

```bash
cd /Users/lingq/Documents/jhh-skills/virtual-jensen/virtual-jensen-web
pip install -r requirements.txt
# Set API key (user must provide)
# export NVIDIA_API_KEY=...
uvicorn app:app --reload --port 8000
```

Open http://localhost:8000, start a meeting, and test:
- Ask Jensen about Blackwell vs MI300X → should reference specific specs and strategic reasoning
- Ask about sovereign AI → should know countries and NVIDIA's role
- Ask about CUDA moat → should give ecosystem-depth analysis, not just "CUDA is important"
- Ask about "latest" anything → should caveat the vintage of information

- [ ] **Step 7: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix: address issues found during smoke testing"
```
