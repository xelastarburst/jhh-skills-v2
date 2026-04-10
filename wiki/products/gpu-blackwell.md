---
title: Blackwell GPU Architecture
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# Blackwell GPU Architecture

## What It Is

Blackwell is NVIDIA's data center GPU architecture, successor to Hopper, designed from the ground up as the engine of AI factories. The architecture comes in three main configurations: the B200 GPU (a single accelerator), the GB200 Grace-Blackwell Superchip (pairing a B200 GPU with a Grace ARM CPU over a 900 GB/s NVLink-C2C interconnect), and the GB200 NVL72 — a liquid-cooled, rack-scale system that connects 36 Grace CPUs and 72 Blackwell GPUs into what Jensen describes as "a single GPU." Blackwell represents a fundamental shift from chip-scale to rack-scale thinking: the unit of compute is no longer a GPU, it is a rack.

## Key Facts

- **Transistor count**: 208 billion transistors across two reticle-limited dies connected by a 10 TB/s chip-to-chip interconnect (each die manufactured at TSMC 4NP process)
- **Process node**: TSMC 4NP (NVIDIA-customized 4nm)
- **Memory**: Up to 192 GB HBM3e per GPU, with 8 TB/s memory bandwidth
- **NVLink 5th generation**: 1.8 TB/s bidirectional bandwidth per GPU (a 2x jump over Hopper's NVLink 4th gen at 900 GB/s)
- **FP4 inference performance**: 20 petaFLOPS (B200) — the new precision tier purpose-built for inference workloads
- **FP8 performance**: 10 petaFLOPS (B200), roughly 2.5x Hopper H100 FP8
- **Second-generation Transformer Engine**: Supports FP4 precision with dynamic range management, enabling 2x the inference throughput per GPU compared to FP8 on Hopper
- **RAS Engine (Reliability, Availability, Serviceability)**: Dedicated engine for AI-specific diagnostics, chip-level self-testing, and preemptive fault detection — designed for 24/7 AI factory uptime
- **Decompression Engine**: Hardware-accelerated database decompression, enabling up to 18x faster database query acceleration for data analytics and retrieval-augmented generation workloads
- **Secure AI**: Confidential computing with TEE (Trusted Execution Environment) support across the full GPU
- **GB200 NVL72**: 36 Grace CPUs + 72 Blackwell GPUs in a single liquid-cooled rack; 13.5 TB aggregate HBM3e; 130 TB/s bisection NVLink bandwidth; up to 720 petaFLOPS FP4 inference; 120 petaFLOPS FP8 training; consumes approximately 120 kW per rack
- **Availability**: B200 and GB200 began shipping to cloud and hyperscaler partners in Q4 2024, with broader availability throughout 2025. GB200 NVL72 racks deployed at scale in 2025.
- **DGX B200**: 8x B200 GPUs per node, 1.4 TB HBM3e, NVLink Switch interconnect, targeted at enterprises building AI factories
- **Key performance claim**: A single GB200 NVL72 rack can serve a GPT-MoE 1.8T parameter model for inference at up to 30x higher throughput than an equivalent Hopper-based deployment

## Strategic Significance

Blackwell is the clearest expression of Jensen's "AI factory" thesis made silicon. Three strategic moves define it:

**1. Rack-scale is the new chip-scale.** The GB200 NVL72 is not 72 GPUs in a rack — it is a single GPU that happens to fill a rack. This is Jensen's Amdahl's Law reasoning applied architecturally: if communication between GPUs is the bottleneck, then eliminate the boundary between GPUs. The 1.8 TB/s NVLink 5th gen and NVLink Switch architecture make the rack the unit of compute, not the chip. Competitors selling individual accelerators are competing at the wrong abstraction level.

**2. Purpose-built for the inference economy.** Hopper was the training architecture. Blackwell is the inference architecture. The FP4 Transformer Engine, the decompression engine, the RAS engine — every new silicon block targets the economics of serving tokens at scale. Jensen's thesis: training is a fixed cost; inference is a variable cost that scales with every user, every agent, every query. The architecture that wins inference wins the recurring revenue stream.

**3. The full-stack advantage made physical.** Blackwell is not just a chip — it is a chip + NVLink fabric + Grace CPU + liquid cooling + networking + system software, all co-designed. This is NVIDIA selling a computing platform, not a component. Cloud providers and sovereign AI programs buy racks, not chips. The integration depth makes component-level competition (AMD MI300X, custom ASICs) structurally disadvantaged — they have to replicate the entire rack, not just match the GPU.

Blackwell also deepens the CUDA moat. Every Blackwell optimization (FP4 kernels, transformer engine auto-tuning, decompression engine APIs) runs through CUDA libraries. The software ecosystem that runs on Blackwell does not trivially port to alternative hardware.

## How It Connects

- Previous generation: [Hopper GPU Architecture](gpu-hopper.md) — Blackwell succeeds Hopper with 2-4x performance per watt improvements
- Systems: [DGX Systems](dgx-systems.md) — DGX B200 and SuperPOD built on Blackwell
- Networking: [Networking](networking.md) — NVLink 5th gen and NVSwitch are critical to NVL72
- Competitor response: [AMD](../competitors/amd.md) — MI300X/MI350 compete at chip level but lack rack-scale integration
- Market context: [Data Center AI](../markets/data-center-ai.md) — Blackwell targets the shift from training capex to inference opex
- Economic thesis: [Inference Economy](../concepts/inference-economy.md) — Blackwell is the hardware embodiment of the inference economy thesis
- Gaming variant: [GeForce & Gaming](gpu-gaming.md) — RTX 50-series shares the Blackwell architecture name but is a different silicon design

## Jensen's Framing

At **GTC 2024** (March 2024), Jensen introduced Blackwell with characteristically physical language: **"Blackwell is not a chip. It is a platform."** He held up the GB200 NVL72 as a single system, emphasizing that NVIDIA now sells racks, not GPUs.

At **GTC 2025** (March 2025), with Blackwell shipping at scale, Jensen reframed the narrative around AI factories: **"Every data center will become an AI factory. Blackwell is the engine of the AI factory."** He positioned the architecture not as a product upgrade but as the enabling infrastructure for an entirely new type of industrial facility — one that ingests data and produces intelligence.

On inference economics, Jensen has emphasized the shift from training to inference as the dominant workload: "The world's data centers are being reimagined as AI factories. The amount of inference that the world needs is going to be extraordinary." Blackwell's FP4 capabilities and the NVL72's aggregate throughput are designed for this reality — Jensen frequently cites the 30x inference throughput improvement over Hopper as the headline metric, because inference throughput directly maps to the unit economics of AI services.

Jensen has also used Blackwell to articulate the "three computers" framework from GTC 2025: one computer for training, one for simulation (Omniverse), and one for deployment (inference). Blackwell NVL72 racks serve as all three, configured differently through software — reinforcing the platform-not-product positioning.
