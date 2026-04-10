---
title: AMD
last_updated: 2026-04-09
freshness: quarterly
category: competitors
---

# AMD

## What It Is

AMD is NVIDIA's most direct competitor in the data center GPU accelerator market, competing with the Instinct MI-series against NVIDIA's H100/H200/B200 lineup. At the whiteboard, Jensen would frame AMD as a chip-layer competitor trying to win a stack-layer war. AMD builds competitive silicon — the MI300X is a genuinely capable accelerator with 192 GB of HBM3 memory — but competes primarily on hardware specs and price. The critical gap is ROCm: AMD's software ecosystem is years behind CUDA in maturity, library breadth, developer tooling, and third-party optimization. AMD can win design wins on paper specs; it struggles to win workloads in production.

## Key Facts

- **MI300X** (launched December 2023): 192 GB HBM3 memory (vs H100's 80 GB HBM3), 5.3 TB/s memory bandwidth, 1,307 TFLOPS FP16 peak, 2,615 TFLOPS FP8 peak, 750W TDP. CDNA 3 architecture. Uses 3D chiplet design with 12 XCDs (compute dies) + 4 IODs, totaling 153 billion transistors. Built on TSMC 5nm (compute) and 6nm (I/O).
- **MI325X** (announced late 2024, shipping 2025): Incremental upgrade — 256 GB HBM3e memory (vs MI300X's 192 GB HBM3), 6 TB/s memory bandwidth. Same CDNA 3 compute architecture. Positioned as a memory-capacity play for larger models.
- **MI350** (announced, expected H2 2025 / early 2026): CDNA 4 architecture on TSMC 3nm. AMD claims up to 35x improvement in inference performance over MI300X for select workloads. Supports FP4 and FP6 data types (matching Blackwell's FP4). Up to 288 GB HBM3e. First AMD GPU to directly target NVIDIA's Blackwell generation.
- **MI400** (roadmap): CDNA "Next" architecture, expected 2026-2027 timeframe. Details sparse.
- **ROCm** (Radeon Open Compute): AMD's open-source GPU compute platform. Version 6.x released in 2024-2025. Supports PyTorch and JAX. Key gaps vs CUDA: fewer optimized libraries, less mature profiling tools, limited third-party support (most ML frameworks optimize for CUDA first, ROCm second), smaller developer community. ROCm has improved significantly — PyTorch support is now functional — but the long tail of CUDA-optimized code (custom kernels, specialized libraries, research code) remains a major barrier.
- **Hyperscaler adoption**: Microsoft Azure offers MI300X instances (ND MI300X v5). Meta has deployed MI300X at scale for internal workloads. Oracle Cloud Infrastructure offers MI300X. Major cloud providers use AMD GPUs for supply diversification and NVIDIA pricing leverage, not as primary training platforms.
- **Market share**: NVIDIA holds approximately 80-90% of the data center AI accelerator market by revenue (estimates vary by source, 2024-2025). AMD's data center GPU revenue grew to approximately $5-6 billion annualized run rate by late 2024, up from near-zero in 2022. AMD originally guided $4.5B for 2024 data center GPU revenue, then raised guidance multiple times. Still a fraction of NVIDIA's $40B+ quarterly data center revenue.
- **Revenue context**: AMD total revenue ~$25-26B (2024 annual). Data center segment (including EPYC CPUs) is AMD's largest and fastest-growing segment. GPU accelerator revenue is a subset of this.

## Strategic Significance

Jensen's framework applied to AMD produces a clear diagnosis: AMD competes at the chip layer in a market where the stack determines the winner.

**Stack vs stack analysis.** Map both stacks:

- NVIDIA: GPU silicon + NVLink interconnect + Grace CPU + DGX systems + CUDA + cuDNN/cuBLAS/NCCL + TensorRT + Triton Inference Server + NIM microservices + AI Enterprise + developer ecosystem (4+ million CUDA developers) + 20 years of optimized libraries + ecosystem of ISVs, frameworks, and research tools.
- AMD: GPU silicon + Infinity Fabric + ROCm + hipBLAS/hipDNN (CUDA-ported libraries) + limited system integration + growing but thin third-party ecosystem.

At every layer above silicon, NVIDIA's stack is deeper. The gap is not linear — it compounds. A researcher choosing a platform evaluates not just FLOPS but: will my PyTorch code run without modifications? Will FlashAttention be optimized? Will vLLM perform well? Will my custom CUDA kernels port? Each "maybe" is friction that pushes the decision back to NVIDIA.

**The ecosystem moat test.** If AMD ships an MI350 that is 10% faster than B200 on raw benchmarks, do customers switch? For most workloads: no. The CUDA ecosystem — libraries, tools, profilers, debuggers, documentation, Stack Overflow answers, course materials, trained engineers — is too deep. Switching costs are measured not in hardware dollars but in engineering months of porting, debugging, and re-optimizing. Jensen's moat test says AMD has a product advantage (when it has one) but not an ecosystem advantage.

**The commodity test.** AMD's competitive strategy is largely price/performance and memory capacity. The MI300X's 192 GB HBM3 was a genuine advantage over the 80 GB H100 — it enabled larger models to fit in a single GPU. But competing on specs is a commodity game. When NVIDIA ships H200 (141 GB) and then B200 (192 GB HBM3e), the memory advantage disappears. AMD must perpetually out-spec NVIDIA on hardware while fighting the software gap — a structurally exhausting position.

**Where AMD is genuinely threatening.** Jensen would not dismiss AMD. The real threat vector is hyperscaler supply diversification. Microsoft, Meta, and Oracle are not buying MI300X because ROCm is better — they are buying it because depending on a single GPU supplier is a strategic risk. If ROCm reaches "good enough" for the top 10-20 most common training and inference workloads (standard PyTorch training, LLM inference serving), hyperscalers will allocate 10-20% of their GPU spend to AMD regardless of the CUDA advantage. This is not a technology competition — it is a procurement strategy. And it is real.

**ROCm trajectory.** ROCm is improving. AMD hired aggressively, open-sourced more of the stack, and key frameworks (PyTorch, JAX) now have functional ROCm backends. The question Jensen would ask: is ROCm on an emerging or receding trajectory? It is clearly emerging. The risk is not that ROCm matches CUDA — it never will on breadth — but that it reaches "good enough" for the high-volume workloads that matter to hyperscalers. That threshold is approaching.

## How It Connects

- [Blackwell GPU Architecture](../products/gpu-blackwell.md) — B200/GB200 is the direct Blackwell-generation competitor to MI350
- [Hopper GPU Architecture](../products/gpu-hopper.md) — H100/H200 competed directly with MI300X
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — CUDA is the primary moat against AMD's hardware competition
- [CUDA Moat](../concepts/cuda-moat.md) — AMD is the canonical case study for ecosystem moat analysis
- [Custom ASICs](custom-asics.md) — hyperscaler custom silicon competes with both AMD and NVIDIA
- [Data Center AI](../markets/data-center-ai.md) — the market where AMD vs NVIDIA competition plays out

## Jensen's Framing

Jensen consistently frames competition as stack-vs-stack rather than chip-vs-chip. On competing with AMD, he has said:

> "It's not about the chip. It's not even just the chip and the library, the programming model. It's the chip, the programming model, and a whole bunch of software that goes on top of it."

On the CUDA ecosystem as competitive defense:

> "The rich developer ecosystem is really valued, and really, really deeply appreciated." — Jensen on why cloud providers continue to support CUDA even when offered alternative hardware.

Jensen rarely mentions AMD by name in keynotes — a deliberate choice. His competitive framing is structural, not personal. He talks about "accelerated computing" vs "general-purpose computing," positioning NVIDIA as the platform that enables a paradigm shift, rather than engaging in spec-sheet comparisons. The implication: AMD is competing inside NVIDIA's paradigm (GPU accelerators running AI workloads), not offering an alternative paradigm.

At GTC 2025, Jensen emphasized the rack-scale vision (GB200 NVL72) as the competitive moat: "This is not 72 GPUs. This is one GPU." The subtext: even if a competitor matches NVIDIA at the chip level, they cannot match the NVLink fabric, the system integration, the software stack that treats 72 GPUs as a single coherent accelerator. AMD has no equivalent to NVL72's rack-scale architecture.

On the Acquired podcast (2024), Jensen articulated the install base dynamic explicitly: CUDA was subsidized on every GeForce GPU for years, building an install base of millions of CUDA-capable devices before GPU computing had a market. That install base attracted developers, who built libraries, which attracted more users, which attracted more developers. AMD cannot replicate this history — they can only try to make ROCm compatible enough that the existing CUDA ecosystem partially ports over.
