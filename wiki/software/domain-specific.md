---
title: Domain-Specific Software
last_updated: 2026-04-09
freshness: quarterly
category: software
---

# Domain-Specific Software

## What It Is
NVIDIA builds domain-specific software platforms that apply GPU-accelerated computing and AI to vertical industries. The four most strategic are cuLitho (computational lithography for semiconductor manufacturing), Clara (healthcare imaging and drug discovery), BioNeMo (foundation models for biology and chemistry), and Earth-2 (climate and weather simulation digital twin). Each represents Jensen's "zero-billion-dollar market" thesis in action: enter a vertical before the market fully exists, build the accelerated computing platform for it, and be the incumbent when demand materializes. These platforms turn NVIDIA GPUs from general-purpose processors into domain-specific accelerators through software.

## Key Facts
- **cuLitho — Computational Lithography**:
  - Partnership with TSMC and ASML, announced 2023, in production deployment
  - Accelerates computational lithography (the process of computing mask patterns for chip manufacturing) by 40-60x vs CPU-based approaches
  - Inverse lithography technology (ILT) and optical proximity correction (OPC) acceleration
  - Deployed on NVIDIA H100 GPUs in semiconductor fabs
  - TSMC is using cuLitho in production for advanced nodes (2nm and beyond)
  - Reduces computational lithography time from weeks to hours on critical layers
  - Enables use of more computationally intensive (and higher quality) algorithms that were previously impractical
  - Strategic: makes NVIDIA GPUs essential to the semiconductor manufacturing process itself — NVIDIA silicon helps make all other silicon

- **Clara — Healthcare**:
  - Clara platform spanning medical imaging, genomics, and drug discovery
  - Clara Holoscan: real-time AI computing platform for medical devices and surgical instruments (sensor processing, AI inference, visualization in a single system)
  - Clara Guardian: smart hospital infrastructure for patient monitoring
  - Clara Parabricks: GPU-accelerated genomic analysis (30-50x faster than CPU-based genome alignment and variant calling)
  - MONAI (Medical Open Network for AI): open-source framework for healthcare AI, co-developed with King's College London, used in 1,000+ hospitals and research institutions
  - FDA-cleared AI models for radiology via partner ecosystem
  - Deployed at major healthcare systems and research hospitals globally

- **BioNeMo — Biology Foundation Models**:
  - Cloud platform for building, training, and deploying biological foundation models
  - Pre-trained models include:
    - ESM-2: protein language model (understanding protein sequences)
    - AlphaFold-derived models for protein structure prediction
    - MolMIM: molecular generation for drug design
    - DiffDock: molecular docking prediction
    - GenSLM: genomic language model
  - BioNeMo Cloud service for drug discovery workflows
  - Fine-tuning support for proprietary biological data
  - Used by pharmaceutical companies (Amgen, AstraZeneca, Recursion, Generate Biomedicines, among others)
  - NIM microservices available for BioNeMo models (deploy protein folding, molecular docking as API endpoints)

- **Earth-2 — Climate & Weather Digital Twin**:
  - Digital twin platform for climate and weather simulation
  - Built on Omniverse and NVIDIA Modulus (physics-ML framework)
  - FourCastNet: AI weather model that produces 7-day global forecasts in seconds vs hours for traditional NWP
  - CorrDiff: generative AI model for super-resolution of weather data (km-scale resolution from coarse inputs)
  - Interactive visualization of climate scenarios at global and regional scales
  - Partnerships with The Weather Company, national weather agencies, climate research institutions
  - Enables simulation of climate change impacts, extreme weather events, renewable energy optimization

## Strategic Significance
Each domain-specific platform exemplifies a different facet of Jensen's strategic thinking:

1. **Zero-billion-dollar markets.** Jensen repeatedly identifies markets that are "zero billion dollars today" but will be enormous. Computational lithography for AI, AI-driven drug discovery, world-scale climate simulation — none of these were GPU markets five years ago. By building the platform before the market exists, NVIDIA is the incumbent when demand arrives. "Our strategy is to build the platform, bring it to zero-billion-dollar markets, and grow them into billion-dollar markets."

2. **cuLitho is uniquely strategic.** Making NVIDIA GPUs essential to semiconductor manufacturing is a recursive moat: NVIDIA silicon helps manufacture all advanced silicon, including NVIDIA's own. If TSMC uses cuLitho on H100s to compute mask patterns for 2nm chips (which include NVIDIA's own Blackwell designs), then NVIDIA is embedded in the supply chain that produces its own products. This also gives NVIDIA leverage and deep relationships with the most important fabs.

3. **CUDA-X in action.** Each domain platform is a proof of Jensen's thesis that CUDA-X libraries turn general-purpose GPUs into domain-specific accelerators. cuLitho turns H100 into a lithography accelerator. Clara turns it into a medical imaging accelerator. BioNeMo turns it into a drug discovery accelerator. The hardware is the same; the software is domain-specific.

4. **BioNeMo and NIM convergence.** BioNeMo models deployed as NIM microservices mean pharmaceutical companies can access protein folding and molecular docking via API. This is the inference economy applied to drug discovery — recurring compute revenue from a domain that has never been an NVIDIA market before.

5. **Earth-2 and Omniverse convergence.** Earth-2 built on Omniverse demonstrates that digital twins scale from factory floors to the entire planet. It validates the Omniverse platform at the most extreme scale and creates partnerships with governments and climate agencies that have long-term infrastructure budgets.

6. **Each vertical deepens the moat.** Every domain-specific library added to the CUDA-X ecosystem is another library that AMD's ROCm does not have. cuLitho has no ROCm equivalent. Clara Parabricks has no ROCm equivalent. The competitive gap widens with every vertical NVIDIA enters.

## How It Connects
- [Accelerated Computing](../concepts/accelerated-computing.md) — Domain-specific software is how accelerated computing enters every industry
- [Omniverse](omniverse.md) — Earth-2 is built on Omniverse; domain platforms leverage the simulation infrastructure
- [CUDA Ecosystem](cuda-ecosystem.md) — Each domain platform is built on CUDA-X libraries
- [NIM & NeMo](nim-nemo.md) — BioNeMo models deploy as NIM microservices
- [AI Enterprise](ai-enterprise.md) — Domain platforms are part of the broader enterprise offering

## Jensen's Framing
Jensen uses domain-specific platforms as his primary evidence that accelerated computing is not just about AI, but about every industry:

> "Accelerated computing is for every industry. cuLitho accelerates semiconductor manufacturing. Clara accelerates healthcare. BioNeMo accelerates drug discovery. Earth-2 accelerates climate science. Every industry has its computational grand challenges, and GPU-accelerated computing can solve them."
> -- Jensen Huang, GTC keynote themes (paraphrased from multiple appearances)

On cuLitho specifically, Jensen has called it "one of the most important applications of accelerated computing" because of its recursive strategic value. At GTC 2023 when introducing the TSMC partnership: "Computational lithography is one of the largest computational workloads in the world. It takes billions of CPU hours. cuLitho, running on NVIDIA GPUs, accelerates this by 40x or more. This means better chips, made faster, at lower cost."

On the zero-billion-dollar-market philosophy: Jensen has repeatedly said that NVIDIA's job is to "build the platforms, create the markets, and be patient." He cites CUDA itself as the original example — in 2006, GPU computing was a zero-billion-dollar market. NVIDIA invested for a decade before the AI boom turned it into the most valuable computing platform in the world. cuLitho, Clara, BioNeMo, and Earth-2 are the next generation of that same strategy.
