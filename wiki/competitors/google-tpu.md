---
title: Google TPU
last_updated: 2026-04-09
freshness: quarterly
category: competitors
---

# Google TPU

## What It Is

Google's Tensor Processing Units are custom-designed AI accelerators built specifically for Google's machine learning workloads and offered through Google Cloud. At the whiteboard, Jensen would draw TPU as the canonical vertical integration play: Google controls the chip, the compiler (XLA), the framework (JAX), the cloud platform, and the workloads. This is the strongest possible competitive position for a single company's needs — and simultaneously the weakest possible position for building a platform. TPU optimizes for Google. NVIDIA optimizes for everyone. That distinction is the entire strategic analysis.

## Key Facts

- **TPU v5e** (launched 2023): Cost-optimized inference chip. 256 TFLOPS BF16 per chip. 16 GB HBM2e per chip. Designed for high-throughput, cost-sensitive inference workloads. Available in pods up to 256 chips. Priced significantly below v5p for inference-heavy workloads.
- **TPU v5p** (launched December 2023): Training-optimized chip. 459 TFLOPS BF16 per chip. 95 GB HBM2e per chip. 2.76 TB/s memory bandwidth. Interconnect: ICI (Inter-Chip Interconnect) enabling pods of up to 8,960 chips. Designed for large-scale model training. Available on Google Cloud as Cloud TPU.
- **Trillium (TPU v6e)** (announced Google Cloud Next 2024, available 2024-2025): ~4.7x improvement in peak compute performance per chip over TPU v5e. 256-chip pod configurations. Improved energy efficiency (67% improvement per chip over v5e). Third-generation SparseCore for embedding-heavy workloads. Enhanced ICI bandwidth for multi-host training.
- **TPU v6 (full, unreleased details)**: Expected training-oriented counterpart to Trillium (v6e), analogous to v5p vs v5e split. Rumored for 2025-2026 availability. Likely significant HBM and compute upgrades.
- **Software stack**: JAX (primary framework, developed by Google), XLA compiler (optimizes computation graphs for TPU hardware), TensorFlow (legacy but still supported), PyTorch/XLA (community bridge, less mature than native PyTorch on CUDA). Pathways (Google's internal distributed training system, not fully public).
- **Key users**: Google DeepMind (Gemini model family trained on TPUs), Anthropic (significant TPU usage for Claude training alongside NVIDIA GPUs), Apple (reported TPU usage for ML workloads), various Google-internal teams (Search, YouTube recommendations, Ads ranking). Limited third-party adoption outside Google Cloud.
- **Cloud TPU pricing**: TPU v5e on-demand ~$1.20/chip/hour. TPU v5p on-demand ~$4.20/chip/hour (varies by region and commitment). Committed-use and spot pricing available at significant discounts. Generally priced competitively vs NVIDIA GPU cloud instances for supported workloads.
- **Market position**: Google does not sell TPU chips — they are cloud-only. This limits TAM to Google Cloud customers willing to commit to the TPU/JAX ecosystem. TPUs handle a significant share of Google's internal ML compute but represent a small fraction of the external AI accelerator market.
- **JAX adoption**: JAX has grown significantly among researchers and AI labs (Google DeepMind, Anthropic, some academic groups). However, PyTorch remains the dominant ML framework by a wide margin in industry and academia. PyTorch's share of ML research papers and GitHub projects is estimated at 70-80%+. JAX's share is growing but remains a minority.

## Strategic Significance

Jensen's framework produces a nuanced assessment of Google TPU — it is the strongest alternative to NVIDIA's platform, and simultaneously the most self-limiting.

**Platform vs product analysis.** This is the core Jensen lens. NVIDIA's GPU is a platform: it serves every workload, every framework, every customer, every cloud. Google's TPU is a product: it serves Google's workloads first, Google Cloud customers second, and everyone else not at all.

Platform economics compound. Every developer who writes CUDA code makes NVIDIA GPUs more valuable. Every library optimized for CUDA deepens the ecosystem. Every university course taught on CUDA creates future customers. TPU has none of these dynamics at scale outside Google. JAX is excellent but serves a niche. XLA is powerful but locked to the TPU/JAX pathway. The compounding loop is internal to Google, not external to the market.

**The vertical integration trade-off.** Google's TPU strategy is rational: control the full stack to optimize total cost of ownership for the world's largest ML workloads. Google trains Gemini, runs Search ranking, powers YouTube recommendations, and serves Ads models — all at scale that justifies custom silicon. For these workloads, TPU is likely cheaper and more efficient than renting NVIDIA GPUs.

But vertical integration is a double-edged sword. Jensen would note: Google optimizes for Google's workloads. That means TPU is excellent for large-scale transformer training and serving (Google's primary use case) but less flexible for the long tail of ML workloads — reinforcement learning, GNNs, custom architectures, scientific computing, inference of novel model types. NVIDIA's generality is a feature, not a limitation.

**The ecosystem moat test applied.** If Google builds a TPU that is 2x faster than NVIDIA's B200 for transformer training, do customers outside Google switch? Most do not, because switching to TPU means switching to Google Cloud, switching to JAX (or PyTorch/XLA with its rough edges), switching away from CUDA libraries, and accepting vendor lock-in to a single cloud provider. The switching cost is the entire stack, not just the chip.

The exceptions are revealing: Anthropic uses TPUs because (a) Google invested in Anthropic, (b) Anthropic's team has deep JAX/TPU expertise from their Google origins, and (c) Anthropic needs training scale that benefits from Google's custom interconnect. These are specific conditions, not generalizable market dynamics.

**Where TPU is genuinely strong.** Jensen would acknowledge TPU's strengths honestly. Google's ICI (Inter-Chip Interconnect) enables pod-scale training at bandwidths that rival NVLink. Google's ability to co-design hardware, compiler, and workload means TPU pods can achieve utilization rates that general-purpose GPU clusters struggle to match. For large language model training — the single most important workload class — TPU is a serious system, not a toy.

**The strategic question.** Jensen's real concern with TPU is not that it competes for external customers — it largely does not. The concern is that TPU proves the viability of custom silicon purpose-built for AI, which validates the hyperscaler custom ASIC strategy more broadly. If Google can build competitive AI chips, the reasoning goes, so can Amazon (Trainium), Microsoft (Maia), and Meta (MTIA). TPU is the proof of concept for the custom ASIC movement.

**JAX as ecosystem risk.** JAX's growth is worth tracking. If JAX becomes the preferred framework for frontier model training (it already is at DeepMind and Anthropic), it creates a pathway for workloads to move to TPU without the CUDA dependency. Jensen's stack thinking says: own value at the framework layer. This is why NVIDIA invests in NIM, TensorRT-LLM, and deep PyTorch integration — to ensure PyTorch-on-CUDA remains the default path, not JAX-on-TPU.

## How It Connects

- [Custom ASICs](custom-asics.md) — TPU is the original custom AI ASIC; validates the approach for AWS Trainium, MS Maia
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — CUDA's universality vs TPU's specificity is the core competitive dynamic
- [CUDA Moat](../concepts/cuda-moat.md) — TPU/JAX represents an alternative stack that partially bypasses the CUDA moat
- [Data Center AI](../markets/data-center-ai.md) — TPU serves the largest single customer (Google) in this market
- [AI Software Landscape](ai-software-landscape.md) — JAX vs PyTorch dynamics directly affect TPU vs GPU adoption

## Jensen's Framing

Jensen rarely discusses TPU directly in public but addresses the dynamic through structural arguments. His framing of the platform-vs-product distinction applies directly:

> "We are an open platform. We support every cloud. We support every framework. We support every developer. That's the difference between a platform and a product."

On why vertical integration has limits, Jensen has emphasized the ecosystem argument:

> "The rich developer ecosystem is really valued, and really, really deeply appreciated." — This is Jensen's indirect response to TPU: cloud providers support CUDA not because NVIDIA forces them to, but because their customers demand it. TPU cannot generate this demand outside Google's walls.

Jensen's competitive philosophy regarding Google is to compete at the platform level while acknowledging Google's right to vertically integrate. At GTC keynotes, he consistently emphasizes NVIDIA's role as the computing platform for the entire industry — not one company. The implicit contrast with TPU is clear: NVIDIA powers every cloud, every lab, every enterprise. TPU powers Google.

On the Acquired podcast (2024), Jensen discussed the CUDA install base strategy — putting CUDA on every GeForce to build ubiquity — as the foundational decision that made NVIDIA a platform rather than a product company. TPU, by contrast, was never designed for ubiquity. It was designed for efficiency within Google's walls. Both are rational strategies; they lead to fundamentally different competitive positions.
