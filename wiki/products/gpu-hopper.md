---
title: Hopper GPU Architecture
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# Hopper GPU Architecture

## What It Is

Hopper is NVIDIA's data center GPU architecture that powered the generative AI revolution. Named after computing pioneer Grace Hopper, the architecture introduced the world's first Transformer Engine — a hardware block purpose-built for the attention mechanisms that underpin large language models. Hopper comes in three main configurations: the H100 (the workhorse that trained most frontier AI models from 2023-2024), the H200 (a memory-upgraded variant with HBM3e for larger models and faster inference), and the GH200 Grace Hopper Superchip (combining the H200 GPU with NVIDIA's Grace ARM CPU via a coherent NVLink-C2C link). Hopper is the architecture that proved GPU data centers could become AI training factories, establishing the blueprint that Blackwell now scales.

## Key Facts

- **Transistor count**: 80 billion transistors on a single monolithic die
- **Process node**: TSMC 4N (NVIDIA-customized 4nm)
- **Streaming Multiprocessors**: 132 SMs, 16,896 CUDA cores, 528 Tensor Cores (4th generation)
- **H100 SXM memory**: 80 GB HBM3, 3.35 TB/s memory bandwidth
- **H200 memory**: 141 GB HBM3e, 4.8 TB/s memory bandwidth — a 76% capacity increase and 43% bandwidth increase over H100, enabling larger models to fit in a single GPU
- **GH200 Grace Hopper Superchip**: H200 GPU + Grace ARM CPU connected via 900 GB/s NVLink-C2C coherent interconnect; 624 GB total memory (141 GB HBM3e + 480 GB LPDDR5X), all accessible as a unified memory space
- **NVLink 4th generation**: 900 GB/s bidirectional bandwidth per GPU
- **NVSwitch**: Enables all-to-all GPU communication in DGX H100 systems (8 GPUs, 3.6 TB/s bisection bandwidth)
- **First-generation Transformer Engine**: Hardware support for FP8 (E4M3 and E5M2 formats) with automatic mixed precision — dynamically switches between FP8 and FP16 on a per-tensor basis
- **FP8 Tensor Core performance**: Up to 3,958 teraFLOPS (H100 SXM, sparse)
- **FP16 Tensor Core performance**: Up to 1,979 teraFLOPS (H100 SXM, sparse)
- **TDP**: 700W (H100 SXM), 350W (H100 PCIe)
- **DGX H100**: 8x H100 SXM GPUs, 640 GB HBM3 aggregate, 3.6 TB/s NVSwitch bisection bandwidth
- **Announced**: GTC 2022 (March 2022). H100 shipping: Q3 2022 (early access), broad availability 2023
- **H200 announced**: November 2023, shipping Q2 2024
- **GH200 announced**: May 2023 (Computex), shipping Q2 2024
- **Performance vs prior gen**: H100 delivers up to 9x faster AI training and up to 30x faster AI inference compared to A100 (Ampere) for large language models
- **PCIe variant**: H100 PCIe — 80 GB HBM3, lower TDP (350W), for air-cooled enterprise deployments

## Strategic Significance

Hopper's strategic significance is best understood as the architecture that converted NVIDIA from "the GPU company" into "the AI infrastructure company." Three dynamics define its importance:

**1. The architecture that proved the AI factory thesis.** When Jensen bet on the transformer engine in 2020-2021 (during Hopper's design phase), transformers were dominant in NLP but the generative AI explosion had not yet happened. ChatGPT launched in November 2022 — the same quarter H100 began shipping. The timing was not coincidence; it was the result of Jensen's inflection-reading: he saw transformers scaling and purpose-built silicon for that trajectory. Every major frontier model (GPT-4, Claude, Gemini, Llama) was trained primarily on H100 clusters. Hopper did not just benefit from the AI wave — it enabled it.

**2. The supply constraint that proved demand is insatiable.** H100 allocation became the most coveted resource in the technology industry from 2023-2024. Cloud providers, sovereign AI programs, and AI labs competed for supply. Wait times stretched to months. This supply-demand dynamic proved Jensen's thesis that compute demand from AI workloads is effectively unbounded — every increment of supply is immediately absorbed by researchers and companies scaling models. The shortage also demonstrated the switching cost of the CUDA ecosystem: even customers frustrated by wait times did not switch to AMD or Google TPUs, because their entire software stack ran on CUDA.

**3. H200 as the inference bridge.** The H200 upgrade (same GPU die, HBM3e memory) demonstrated a key strategic pattern: memory bandwidth and capacity are often the inference bottleneck, not raw compute. By offering 76% more memory in the same form factor, NVIDIA extended Hopper's relevance into the inference era while Blackwell ramped. This "upgrade within architecture" move keeps customers on NVIDIA silicon through generation transitions — a flywheel play that prevents competitive openings.

Hopper also established NVIDIA's system-level selling motion. DGX H100 and HGX H100 reference designs meant cloud providers and OEMs deployed NVIDIA-designed systems, not just NVIDIA chips. This set the precedent for Blackwell's even deeper system integration (NVL72).

## How It Connects

- Successor: [Blackwell GPU Architecture](gpu-blackwell.md) — Blackwell delivers 2-4x Hopper performance with rack-scale integration
- Software foundation: [CUDA Ecosystem](../software/cuda-ecosystem.md) — Hopper's dominance reinforced CUDA as the mandatory AI software platform
- Competitor context: [AMD](../competitors/amd.md) — MI300X launched as a direct H100/H200 competitor; ROCm ecosystem gap kept most workloads on Hopper
- Market impact: [Data Center AI](../markets/data-center-ai.md) — Hopper-era demand established the $100B+ AI infrastructure market
- Systems: [DGX Systems](dgx-systems.md) — DGX H100 was the reference platform for AI training clusters

## Jensen's Framing

At **GTC 2022**, Jensen introduced Hopper by connecting it directly to the transformer revolution: **"The [transformer] model has really become the workhorse of AI. We designed an engine specifically for it."** The Transformer Engine was positioned not as a feature but as a thesis — that transformers would become the dominant compute workload, and purpose-built silicon would define the competitive landscape.

During the **Acquired FM interview** (March 2024), Jensen reflected on the H100 demand explosion with characteristic understatement about timing: "We sensed that something was happening. The amount of computation that was necessary to train these large language models was growing at an extraordinary rate." He connected this to NVIDIA's decade-long investment in the CUDA ecosystem, noting that demand for H100s validated the entire software platform strategy: developers had no viable alternative because the software stack was too deep.

On the H100 supply shortage, Jensen has framed scarcity not as a failure but as evidence of a thesis: **"The demand for AI infrastructure is insatiable. Every GPU we ship is absorbed immediately."** He has used this to argue for continued massive investment in supply — the correct response to insatiable demand is more supply, not higher prices.

Jensen has also used Hopper to illustrate his "zero-billion-dollar market" concept. When Hopper was designed (2020-2021), the "generative AI infrastructure" market was effectively zero. Market research firms had no reports. Customers were not requesting transformer-optimized hardware. Jensen's willingness to commit billions to a market that did not yet exist — based on his reading of the transformer scaling trajectory — is a case study in his own technology bet framework.
