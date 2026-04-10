---
title: Networking
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# Networking

## What It Is
NVIDIA's networking stack is the connective tissue of modern AI infrastructure — the fabric that turns individual GPUs into a unified compute engine. Acquired through the $6.9B Mellanox deal (2020), this portfolio spans chip-to-chip interconnects (NVLink), in-system switches (NVSwitch), network interface cards (ConnectX), data processing units (BlueField), and data center switches (Quantum for InfiniBand, Spectrum for Ethernet). The key insight: in distributed AI training and inference, networking bandwidth and latency determine total system throughput. NVIDIA now owns every layer of the networking stack from on-chip to across-the-data-center.

## Key Facts

### NVLink (GPU-to-GPU Interconnect)
- **NVLink 5th generation** (Blackwell): 1.8 TB/s bidirectional bandwidth per GPU
- NVLink 4th gen (Hopper): 900 GB/s bidirectional per GPU
- NVLink 3rd gen (Ampere): 600 GB/s bidirectional per GPU
- NVLink enables direct GPU-to-GPU communication without traversing PCIe or the CPU
- GB200 NVL72 uses NVLink to connect 72 GPUs as a single memory domain

### NVSwitch
- **4th-generation NVSwitch** (Blackwell era): connects up to 72 GPUs in an NVLink domain
- 1.8 TB/s per GPU port bandwidth, all-to-all non-blocking topology
- 3rd-gen NVSwitch (Hopper): connected 8 GPUs within DGX H100, or up to 256 GPUs via NVLink Switch System
- NVSwitch is what makes NVLink scale beyond point-to-point — it creates a GPU-scale fabric inside the system
- Each NVSwitch chip: 50 billion+ transistors (4th gen), custom NVIDIA silicon

### ConnectX Network Interface Cards (NICs)
- **ConnectX-7**: up to 400 Gb/s InfiniBand or Ethernet per port; PCIe Gen 5; hardware offloads for RDMA, RoCE, GPUDirect; primary NIC in current DGX systems
- **ConnectX-8** (announced 2024/2025): up to 800 Gb/s (NDR800 InfiniBand or 800GbE); PCIe Gen 6 ready; enhanced in-network computing capabilities
- Hardware acceleration: RDMA (Remote Direct Memory Access), GPUDirect RDMA (bypasses CPU for GPU-to-GPU across network), GPUDirect Storage
- NVIDIA DOCA SDK for programming ConnectX and BlueField

### BlueField Data Processing Units (DPUs)
- **BlueField-3**: 400 Gb/s networking + 16 Arm Cortex-A78 cores + hardware accelerators
- Offloads networking, security, storage virtualization from the host CPU
- Enables "zero-trust" security at the infrastructure level
- BlueField-4 in development

### Quantum InfiniBand Switches
- **Quantum-2 (QM9700/QM9790)**: NDR InfiniBand, 400 Gb/s per port, 64 ports per switch, 51.2 Tb/s aggregate switching capacity
- **Quantum-X800 (next gen)**: NDR800, 800 Gb/s per port, announced at GTC 2024 for 2025 availability
- InfiniBand advantages over Ethernet for AI: lossless fabric, adaptive routing, congestion control, in-network computing (SHARP — Scalable Hierarchical Aggregation and Reduction Protocol)
- SHARP enables in-network allreduce operations, reducing distributed training overhead by up to 2x

### Spectrum-X (Ethernet for AI)
- **Spectrum-X** platform: purpose-built Ethernet networking optimized for AI workloads
- Combines Spectrum-4 switches (51.2 Tb/s, 400GbE) with ConnectX-7 NICs and NVIDIA's AI-optimized networking software
- Achieves 1.6x better AI network performance vs standard Ethernet (NVIDIA's claim)
- Key features: adaptive routing, congestion control (RoCE optimization), telemetry for AI workloads
- **Why it matters**: Many data centers are standardized on Ethernet, not InfiniBand. Spectrum-X brings InfiniBand-class performance to Ethernet, massively expanding NVIDIA's networking TAM
- Spectrum-X800: next-gen, 800GbE-class, announced 2024 for future deployment

### Networking Software
- **NVIDIA DOCA SDK**: programming framework for BlueField DPUs and ConnectX NICs
- **NVIDIA UFM (Unified Fabric Manager)**: management, monitoring, and orchestration for InfiniBand and Ethernet fabrics
- **NetQ**: network monitoring and validation for Spectrum Ethernet switches
- **GPUDirect technologies**: RDMA, Storage, Peer-to-Peer — eliminate CPU bottlenecks in GPU data movement

## Strategic Significance

Networking is arguably NVIDIA's most strategically important acquisition-driven capability. The Mellanox deal was pure stack thinking and Amdahl's Law in action.

**Why this matters in Jensen's framework:**

1. **Amdahl's Law is the core insight.** In a distributed AI system, total throughput is limited by the slowest component. You can double GPU FLOPS, but if the network can't feed data to GPUs fast enough, you've wasted half your investment. Jensen recognized that networking was becoming THE bottleneck in AI infrastructure. Owning the bottleneck layer is the highest-leverage move.

2. **Post-Mellanox: owning the full data center stack.** Before Mellanox, NVIDIA sold GPUs and let customers figure out networking. After Mellanox, NVIDIA controls: GPU compute (CUDA) + GPU interconnect (NVLink/NVSwitch) + host networking (ConnectX/BlueField) + switch fabric (Quantum/Spectrum). No competitor owns this full stack. AMD has GPUs but not networking. Broadcom has networking but not GPUs. Only NVIDIA has both.

3. **Spectrum-X is a massive TAM expansion.** InfiniBand is the gold standard for AI networking but serves a niche market (HPC, large AI clusters). Ethernet is everywhere. Spectrum-X takes NVIDIA's networking intelligence into the Ethernet world, expanding the addressable market by 10x+. Every data center doing AI inference — not just training — is now a target.

4. **NVLink as vertical integration moat.** NVLink is proprietary — no one else can plug into it. A system built on NVLink (like the GB200 NVL72) is an NVIDIA-only architecture. Competitors can match GPU FLOPS but cannot match the system-level bandwidth that NVLink provides. This makes head-to-head GPU benchmark comparisons misleading — the real comparison is system throughput, and NVLink dominates there.

5. **In-network computing (SHARP) is a secret weapon.** SHARP performs collective operations (allreduce) inside the network switch itself, rather than bouncing data back to GPUs. This is not just faster networking — it's a fundamentally different compute model. NVIDIA is moving computation into the network fabric, blurring the line between networking and computing.

6. **Flywheel with DGX.** DGX systems use ConnectX-7, NVLink, NVSwitch, and Quantum/Spectrum switches. DGX SuperPOD IS a networking product as much as a compute product. Networking revenue grows directly with every DGX sale.

## How It Connects
- [DGX Systems](dgx-systems.md) — DGX is the primary system consumer of NVIDIA's networking stack
- [Blackwell GPU Architecture](gpu-blackwell.md) — NVLink 5th gen and NVSwitch 4th gen are co-designed with Blackwell silicon
- [Accelerated Computing](../concepts/accelerated-computing.md) — networking is the enabling layer that makes accelerated computing work at scale
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — GPUDirect, NCCL, and DOCA are the software layers on top of networking hardware
- [Data Center AI](../markets/data-center-ai.md) — networking is the fastest-growing component of data center AI spend

## Jensen's Framing

On why NVIDIA acquired Mellanox (post-acquisition, 2020):

> "The data center is the new unit of computing. You can't think about the processor in isolation — you have to think about the entire data center as one giant computer. And in that computer, networking IS computing."

On Amdahl's Law and networking:

> "Data centers used to be defined by their processors. Now they're defined by their I/O. The network determines how fast your AI factory runs. If you have the world's fastest GPUs connected by the world's slowest network, you have the world's slowest AI factory."

On Spectrum-X (GTC 2024):

> "Ninety percent of Ethernet networks deployed today are not optimized for AI. Spectrum-X brings AI-class performance to the world's most widely deployed networking architecture. This is a giant opportunity."

On NVLink scale:

> "NVLink lets you build a computer that has never existed before — 72 GPUs with 13 terabytes of memory, all at 1.8 terabytes per second. No bus. No bottleneck. One giant GPU. This is what it means to own the full stack."
