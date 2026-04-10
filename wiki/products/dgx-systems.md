---
title: DGX Systems
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# DGX Systems

## What It Is
DGX is NVIDIA's AI supercomputer product line — the full-stack system that bundles GPUs, networking, software, and support into a single purchasable unit. It is the physical embodiment of Jensen's "AI factory" concept: purpose-built infrastructure that takes in raw data and produces intelligence. DGX ranges from a single node (DGX B200) to rack-scale (DGX SuperPOD) to cloud-hosted (DGX Cloud), giving customers a consistent architecture from desk to data center to cloud.

## Key Facts

### DGX B200 (Single Node)
- 8x NVIDIA B200 GPUs (Blackwell architecture) per node
- Up to 1.4 TB of HBM3e GPU memory across the 8 GPUs (each B200 has up to 192 GB HBM3e)
- 2x Intel Xeon Scalable or AMD EPYC host CPUs (configuration varies by generation)
- 5th-generation NVLink interconnect: 1.8 TB/s bidirectional GPU-to-GPU bandwidth
- Up to 72 PFLOPS FP4 AI performance per node
- ConnectX-7 networking: 400 Gb/s InfiniBand or Ethernet per port, up to 8 network ports
- NVMe SSD storage: 30 TB or more per node
- 14.3 kW typical power consumption per node
- Ships with DGX OS (Ubuntu-based), NVIDIA AI Enterprise software stack, Base Command management
- Announced GTC 2024, availability ramped through 2025

### DGX GB200 NVL72 (Rack-Scale)
- 72 Blackwell GPUs + 36 Grace CPUs in a single liquid-cooled rack
- NVLink domain connects all 72 GPUs as a single logical GPU
- Up to 13.5 TB of unified HBM3e memory across the rack
- 720 PFLOPS FP4 AI performance per rack
- Designed for trillion-parameter model training and real-time inference
- Liquid cooling required (not air-cooled)
- Announced GTC 2024, production ramp began late 2024 / early 2025

### DGX SuperPOD
- Multi-rack configuration: scales from 8 to 32+ DGX nodes (or NVL72 racks)
- Interconnected via Quantum InfiniBand or Spectrum-X Ethernet fabric
- DGX SuperPOD with GB200 NVL72: up to 11.5 exaFLOPS FP4 across a full deployment
- Includes NVIDIA Base Command Manager for cluster orchestration, job scheduling, monitoring
- Shared parallel file storage (typically Lustre or GPFS-based, or NVIDIA VAST Data integration)
- Reference architecture for enterprise and sovereign AI deployments

### DGX Cloud
- Cloud-hosted DGX infrastructure accessible as a service
- Partner clouds: Microsoft Azure, Google Cloud, Oracle Cloud Infrastructure (OCI), CoreWeave, Lambda
- Monthly subscription model: DGX Cloud H100 instances started at ~$37,000/month per 8-GPU instance at launch
- Pricing varies by GPU generation, cloud partner, and commitment length
- Includes NVIDIA AI Enterprise software, Base Command Platform, NIM microservices
- Multi-node training support with dedicated high-speed interconnects (not shared cloud networking)
- DGX Cloud announced GTC 2023, expanded with Blackwell-based instances in 2025

### Pricing Context
- DGX B200 system list price: estimated $275,000-$400,000+ per node (varies by configuration; NVIDIA does not always publish exact pricing)
- DGX GB200 NVL72 rack: estimated $2-3 million per rack
- DGX Cloud: consumption/subscription pricing — shifts capex to opex for customers

## Strategic Significance

DGX is where NVIDIA completed the transformation from component seller to systems company. This is stack thinking in action: rather than selling B200 GPUs to OEMs and letting Dell or HPE capture the system-level margin, NVIDIA sells the entire integrated system — GPU, CPU, NVLink, networking, storage, OS, management software, and AI frameworks — under the DGX brand.

**Why this matters in Jensen's framework:**

1. **Full-stack ownership.** DGX captures margin at every layer of the stack. The GPU is a component; DGX is an architecture. Customers buy DGX because the integration is the product — NVIDIA has already solved the networking topology, cooling, software compatibility, and cluster management problems.

2. **AI factory economics.** Jensen frames DGX not as a server but as a "factory" — a capital investment that produces intelligence. This reframes the purchase decision from IT procurement to manufacturing infrastructure. A $3M NVL72 rack isn't expensive if it's a factory producing $50M/year in AI inference revenue.

3. **Deeper lock-in.** When a customer buys B200 GPUs, they might switch to AMD MI350 next cycle. When they buy DGX SuperPOD with Base Command, NVLink fabric, and AI Enterprise software, the switching cost spans the entire stack. The software layer (Base Command, NIM, AI Enterprise) creates recurring revenue and sticky relationships.

4. **DGX Cloud expands the funnel.** Cloud-hosted DGX removes the capex barrier, letting startups and enterprises experiment before committing to on-prem. It also positions NVIDIA as the "Intel Inside" of AI cloud — the cloud providers become distribution partners, not competitors.

5. **Reference architecture power.** Even when customers buy DGX-like systems from Dell, HPE, or Lenovo (branded as "NVIDIA-Certified Systems"), the reference design is DGX. NVIDIA sets the architecture; OEMs execute it. This is platform economics — NVIDIA designs the standard, the ecosystem builds around it.

## How It Connects
- [Blackwell GPU Architecture](gpu-blackwell.md) — the GPU engine inside DGX B200 and GB200 NVL72
- [Networking](networking.md) — NVLink, NVSwitch, and InfiniBand/Spectrum-X fabric that connects DGX nodes
- [AI Factories](../concepts/ai-factories.md) — DGX is the physical implementation of the AI factory concept
- [Data Center AI](../markets/data-center-ai.md) — DGX is the primary product serving this market
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — DGX ships pre-loaded with the full CUDA stack
- [AI Enterprise](../software/ai-enterprise.md) — bundled software layer that adds recurring revenue

## Jensen's Framing

At GTC 2024, introducing the Blackwell-based DGX systems:

> "The world's data centers are becoming AI factories. They take in raw data and they produce tokens — the commodity of intelligence. DGX is the operating unit of this new manufacturing era."

On the GB200 NVL72 rack:

> "Seventy-two GPUs connected as one. This is a single giant GPU — 13.5 terabytes of memory, linked at 1.8 terabytes per second. You cannot build this by buying components and racking them yourself. The system IS the architecture."

On DGX Cloud (GTC 2023):

> "Every enterprise needs access to AI supercomputing. DGX Cloud lets you rent an AI supercomputer from a browser. One click — you have a DGX."

On systems vs components:

> "We are a platform computing company. We don't sell chips. We sell the entire stack — from the silicon to the system to the software to the cloud. DGX is NVIDIA, fully expressed."
