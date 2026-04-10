---
title: Accelerated Computing
last_updated: 2026-04-09
freshness: evergreen
category: concepts
---

# Accelerated Computing

## What It Is

Accelerated computing is the thesis that general-purpose computing has hit a fundamental wall — single-thread CPU performance improvement has slowed from ~52% per year (1986-2003) to ~3% per year post-2015 — and the future belongs to domain-specific accelerators that run parallelizable workloads orders of magnitude faster and cheaper than CPUs. In Jensen's framing, this is not one thesis among several; it is THE thesis. Everything NVIDIA does — CUDA, GPUs, AI, robotics, Omniverse — flows from this single governing insight: any workload that can be parallelized should be accelerated, and the company that owns the acceleration platform owns the future of computing.

## Key Facts

- **The Moore's Law inflection**: Dennard scaling (the ability to shrink transistors AND reduce power) ended around 2006. Moore's Law for transistor density continued but single-thread CPU performance gains collapsed. The "free performance" era ended; getting more compute now requires architectural innovation, not just smaller transistors.
- **CPU vs GPU performance divergence**: Over the past 20 years, GPU floating-point throughput has grown at roughly 2x the rate of CPU throughput. A modern NVIDIA B200 GPU delivers 20 petaFLOPS (FP4) versus single-digit teraFLOPS on the fastest CPUs — a gap of roughly 1,000x for parallel workloads.
- **"The more you buy, the more you save"**: Jensen's counterintuitive framing. Accelerated computing is not an added cost — it is a cost reduction. A workload that takes 100 CPU servers can run on 1-2 GPU servers, consuming less power, less space, less cooling, and less total cost. The GPU costs more per unit, but the total cost of ownership is lower. "Buy a $50,000 GPU system and retire $500,000 worth of CPU infrastructure."
- **Domain breadth**: Accelerated computing is not just AI. NVIDIA targets every parallelizable domain: deep learning and AI training/inference, high-performance computing and scientific simulation, computational genomics and drug discovery, climate modeling and weather prediction, electronic design automation (cuLitho for lithography), computational fluid dynamics, financial modeling, data analytics (RAPIDS), computer graphics and ray tracing, video encoding/decoding, and robotics simulation.
- **$1 trillion installed base**: As of GTC 2024, Jensen cited approximately $1 trillion worth of CUDA-capable GPUs installed worldwide — the foundation of the accelerated computing ecosystem.
- **NVIDIA's 30-year arc**: NVIDIA was founded in 1993 to build graphics accelerators. Jensen recognized early that GPUs were massively parallel processors that could be repurposed beyond graphics. CUDA (2006) was the pivotal bet — making GPUs programmable for general-purpose parallel computing. The AlexNet moment (2012) proved GPUs could train neural networks. The transformer era (2017+) proved they could power AI at scale. Each wave validated the same underlying thesis: accelerate everything.
- **Data center energy economics**: Data center power consumption is a growing global constraint. Accelerated computing directly addresses this: a GPU-accelerated data center can deliver the same compute output at a fraction of the energy. Jensen frequently cites energy efficiency as the ultimate forcing function — the world cannot build enough power plants to run AI on CPUs.

## Strategic Significance

Accelerated computing is not a product category for Jensen — it is the essence, the one governing force he has identified in computing. In his "essence" framework (see references/reasoning-system.md), once you identify the fundamental force driving an industry, everything else — org structure, investment decisions, product strategy — must align to it.

Jensen's reasoning chain:
1. General-purpose computing hit a wall (physics — Dennard scaling ended).
2. Compute demand is not slowing — it is exploding (AI, simulation, genomics, etc.).
3. Therefore, domain-specific acceleration is not optional — it is inevitable.
4. The company that builds the platform for acceleration (hardware + software + ecosystem) captures the value.
5. NVIDIA built that platform (CUDA + GPU + libraries + developers) over 20 years.
6. The install base is now so large that switching costs exceed any competitor's hardware advantage.
7. Therefore: NVIDIA's position is structurally durable, and every new accelerated workload expands the moat.

This thesis drives every major NVIDIA strategic decision: the CUDA ecosystem investment (turning GPUs into a universal acceleration platform), the Mellanox acquisition (accelerating the network layer too — Amdahl's Law), the pivot from gaming-first to data-center-first, the move into software with NIM and AI Enterprise (owning more layers of the stack), and the physical AI push (next frontier of acceleration).

The thesis also has a self-fulfilling quality. As more workloads move to accelerated computing, the install base grows, which attracts more developers, which creates more libraries, which makes acceleration easier for the next workload. Jensen has been running this flywheel since 2006, and it has compounded for two decades.

## How It Connects

- [CUDA Moat](cuda-moat.md) — CUDA is the software platform that delivers accelerated computing; the moat that protects it
- [Inference Economy](inference-economy.md) — AI inference is the largest new accelerated computing workload
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — The 400+ library ecosystem that makes acceleration practical across domains

## Jensen's Framing

> "Accelerated computing is the path forward. General-purpose computing has run out of steam. You can't just make the CPU faster anymore — the physics won't let you. But if you can take the workload and parallelize it, you can speed it up by 10x, 100x, sometimes 1,000x. The more you buy, the more you save."
> -- Jensen Huang, GTC 2025 keynote (paraphrased from keynote summary, everestgrp.com)

> "The installed base of CUDA is enormous. There's $1 trillion worth of CUDA GPUs installed around the world. And just about every single AI researcher, every single computer scientist is familiar with CUDA."
> -- Jensen Huang, Acquired FM podcast interview (2024)

> "AI crossed an important threshold — models became good enough to be useful at scale."
> -- Jensen Huang, Stratechery interview (March 2026)

> "We sensed that something was happening. The amount of computation that was necessary to train these large language models was growing at an extraordinary rate."
> -- Jensen Huang, Acquired FM podcast interview (2024)

> "If computation represents 50% of the problem and I sped it up infinitely, I only sped up the total by 2x."
> -- Jensen Huang on Amdahl's Law as applied to accelerated computing strategy, Lex Fridman Podcast #494 (March 2026)

> "Unless you have a tolerance for failure, you will never experiment, and if you don't ever experiment, you will never innovate."
> -- Jensen Huang, Stanford Entrepreneurship Corner (2011) — on why NVIDIA invested in accelerated computing for a decade before payoff
