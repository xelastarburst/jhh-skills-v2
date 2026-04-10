---
title: AI Software Landscape
last_updated: 2026-04-09
freshness: quarterly
category: competitors
---

# AI Software Landscape

## What It Is

The open-source AI software ecosystem — Hugging Face, vLLM, PyTorch, JAX, and the constellation of tools built around them — represents a different kind of competitive threat to NVIDIA than hardware competitors. At the whiteboard, Jensen would draw the stack and point to the layer above CUDA: if open-source software abstracts away the hardware layer, NVIDIA's GPU becomes a commodity. Hugging Face as the model distribution hub, vLLM as the inference serving standard, PyTorch as the training framework — each of these "layer above" tools reduces the developer's direct interaction with CUDA. Jensen's stack thinking says: if you do not own value at the software layer, someone will commoditize you at the hardware layer. This is why NVIDIA invests heavily in NIM, TensorRT-LLM, and its own software stack — to ensure that NVIDIA's software, not just its hardware, is the platform developers build on.

## Key Facts

### Hugging Face
- **Model Hub**: Over 1 million public models hosted as of 2025 (up from ~500K in early 2024). Largest open repository of ML models in the world. Covers NLP, computer vision, audio, multimodal, and generative AI.
- **Datasets**: Over 200,000 datasets hosted on the Hub.
- **Spaces**: Over 500,000 ML demo applications hosted.
- **Revenue model**: Enterprise Hub subscriptions, Inference Endpoints (managed model serving), PRO subscriptions. Valued at $4.5B as of August 2023 funding round.
- **Ecosystem role**: De facto standard for model distribution and sharing. The `transformers` library is the most widely used library for loading and running pre-trained models. Nearly every open-source model (Llama, Mistral, Falcon, StableLM, etc.) is distributed via Hugging Face.
- **Hardware abstraction**: Hugging Face's `transformers` and `optimum` libraries increasingly abstract hardware backends. `optimum` provides optimized inference for NVIDIA (via TensorRT), AMD (via ROCm), Intel (via OpenVINO), and other backends. This abstraction layer is exactly what Jensen's framework identifies as a commoditization risk.
- **Strategic significance**: Hugging Face is not a hardware competitor — it is a distribution layer that could determine which hardware gets used. If Hugging Face's one-click deployment defaults to the cheapest available GPU (regardless of vendor), it weakens NVIDIA's software moat.

### vLLM
- **What it is**: Open-source LLM inference serving engine. Uses PagedAttention algorithm for efficient KV-cache memory management. Originally developed at UC Berkeley (Sky Computing Lab).
- **Adoption**: Rapidly became the most popular open-source LLM inference server. Used by major AI companies and cloud providers. Deployed in production at scale by numerous organizations serving LLM APIs.
- **Performance**: Competitive with NVIDIA's TensorRT-LLM on many LLM inference benchmarks, sometimes matching or exceeding throughput. Key advantage: simplicity — vLLM is easier to deploy and configure than TensorRT-LLM.
- **Hardware support**: Primarily optimized for NVIDIA GPUs (via CUDA), but growing support for AMD GPUs (ROCm), AWS Neuron (Trainium/Inferentia), and TPU. Multi-hardware support is a commoditization vector — if vLLM runs well on AMD, the incentive to use NVIDIA-specific TensorRT-LLM weakens.
- **Competitive dynamic with TensorRT-LLM**: NVIDIA's TensorRT-LLM offers deeper optimization (kernel fusion, quantization, custom CUDA kernels) that can deliver 20-40% better throughput on NVIDIA hardware. But TensorRT-LLM is more complex to configure and is NVIDIA-specific. vLLM trades peak performance for simplicity and portability. For many deployments, "90% of TensorRT-LLM performance with 10% of the setup effort" is good enough.
- **Community**: Active open-source development, strong GitHub engagement (40,000+ stars), rapid feature addition. Supported by contributions from multiple companies.

### PyTorch
- **Dominance**: PyTorch is the dominant ML framework by a wide margin. Estimated 70-80%+ of ML research papers, industry projects, and GitHub repositories use PyTorch. Created by Meta AI Research (originally Facebook AI Research), now governed by the PyTorch Foundation under the Linux Foundation.
- **CUDA optimization**: PyTorch is deeply optimized for NVIDIA GPUs via CUDA, cuDNN, and NCCL. NVIDIA engineers contribute significantly to PyTorch's CUDA backend. This deep integration is part of the CUDA moat — PyTorch-on-CUDA is the path of least resistance for most ML work.
- **Alternative backends**: PyTorch supports ROCm (AMD), XLA (TPU/Google), Intel extensions, and others. However, CUDA backend is the most mature, best-optimized, and best-tested by a significant margin. Running PyTorch on non-NVIDIA hardware is functional but involves more friction.
- **torch.compile**: PyTorch 2.0+ introduced `torch.compile` with Triton-based compilation, which generates optimized GPU kernels automatically. This reduces the need for hand-written CUDA kernels — a double-edged sword for NVIDIA. It makes PyTorch more efficient on NVIDIA hardware, but also makes it potentially easier to target alternative hardware via compiler backends.
- **Strategic significance for NVIDIA**: PyTorch's CUDA-first design is a core pillar of the CUDA moat. NVIDIA's strategy is to keep PyTorch-on-CUDA the highest-performance, lowest-friction path. If PyTorch becomes equally performant on alternative hardware, the moat weakens.

### JAX
- **Position**: Google-developed ML framework. Focused on functional programming, composability, and XLA compilation. Primary framework for Google DeepMind (Gemini), Anthropic (Claude), and some academic research groups.
- **Market share**: Significantly smaller than PyTorch. Estimated at 10-15% of ML research usage. Growing in the frontier model training segment but not displacing PyTorch in the broader ecosystem.
- **NVIDIA support**: JAX runs on NVIDIA GPUs via CUDA/XLA. NVIDIA has worked to ensure JAX performance on GPUs is competitive. However, JAX is also the primary pathway to TPU, making it a potential pipeline for workloads to shift from NVIDIA hardware to Google hardware.
- **Strategic significance**: JAX's growth is less about JAX replacing PyTorch and more about JAX creating an alternative stack (JAX + XLA + TPU) that bypasses CUDA entirely. If JAX becomes the standard for frontier model training, it weakens the assumption that all important ML work runs on PyTorch-on-CUDA.

### Other Notable Projects
- **GGML / llama.cpp**: Inference runtime optimized for running LLMs on consumer hardware (CPUs, Apple Silicon, consumer GPUs). Extremely popular for local inference. Supports NVIDIA GPU acceleration via CUDA but is primarily a CPU/edge solution. Demonstrates that inference workloads can increasingly run without high-end NVIDIA GPUs.
- **Triton (OpenAI)**: Open-source programming language for writing GPU kernels. Simpler than raw CUDA. Increasingly used in PyTorch's `torch.compile` stack. Could potentially target non-NVIDIA GPUs, though currently NVIDIA-focused.
- **MLX (Apple)**: ML framework optimized for Apple Silicon. Small but growing adoption for on-device ML development.
- **ONNX Runtime**: Cross-platform inference runtime supporting multiple hardware backends. Enables model portability across NVIDIA, AMD, Intel, and CPU.

## Strategic Significance

Jensen's stack thinking identifies this category as the "layer above" threat — qualitatively different from hardware competitors but potentially more dangerous to NVIDIA's long-term position.

**The commoditization risk.** Jensen's framework: if the software layer above you abstracts away your hardware, you become a commodity. The logic chain:

1. Hugging Face becomes the standard for model distribution and deployment
2. vLLM becomes the standard for LLM inference serving
3. Both tools support multiple hardware backends (NVIDIA, AMD, TPU, Trainium)
4. Developers interact with Hugging Face + vLLM, not with CUDA directly
5. Hardware selection becomes a pricing/availability decision, not an ecosystem decision
6. NVIDIA's GPU becomes a commodity competing on price
7. NVIDIA's margins compress

This is the nightmare scenario for Jensen. It explains NVIDIA's aggressive investment in its own software stack (NIM, TensorRT-LLM, CUDA libraries, AI Enterprise) — to ensure that developers interact with NVIDIA's software, not just generic open-source tools.

**NVIDIA's counter-strategy: own the software layer.** Jensen's response to the commoditization risk is to make NVIDIA's software the performance tier above open-source alternatives:

- **TensorRT-LLM vs vLLM**: TensorRT-LLM is faster on NVIDIA hardware (20-40% throughput advantage in optimized configurations). The trade-off: performance vs simplicity. NVIDIA's bet is that production deployments care about performance enough to use NVIDIA-optimized tools.
- **NIM (NVIDIA Inference Microservices)**: Containerized, optimized inference packages for popular models. NIM bundles TensorRT-LLM optimization into easy-to-deploy containers. This is NVIDIA's answer to Hugging Face's ease of deployment — making NVIDIA-optimized inference as simple as `docker pull`.
- **CUDA libraries deepening**: cuBLAS, cuDNN, NCCL, cuSPARSE, Cutlass — each library provides NVIDIA-specific optimization that generic frameworks cannot match. The more computation flows through CUDA libraries, the harder it is for alternative hardware to compete.

**The "good enough" threshold.** Jensen would identify the critical question: at what point does vLLM-on-AMD become "good enough" that the 20-40% TensorRT-LLM advantage on NVIDIA does not justify the price premium? For cost-sensitive inference deployments (which will dominate as inference scales), "good enough" may arrive sooner than NVIDIA would like. This is the same "good enough" dynamic that threatens NVIDIA via ROCm — the open-source software layer accelerates it by making hardware switching easier.

**Hugging Face as kingmaker.** Jensen's platform thinking applied to Hugging Face reveals a nuanced dynamic. Hugging Face is not a hardware competitor — it is a distribution platform. Distribution platforms become kingmakers. If Hugging Face's default deployment path favors NVIDIA (via TensorRT optimization), it reinforces the CUDA moat. If Hugging Face's default path becomes hardware-agnostic (or worse, defaults to the cheapest available option), it erodes the moat. NVIDIA's relationship with Hugging Face — contributing optimizations, ensuring TensorRT integration, co-marketing — is a strategic priority, not a nice-to-have.

**PyTorch as the linchpin.** PyTorch's CUDA-first architecture is arguably the single most important pillar of the CUDA moat today. More ML code runs through PyTorch than through any other pathway. As long as PyTorch-on-CUDA is meaningfully better than PyTorch-on-ROCm or PyTorch-on-XLA, the moat holds. Jensen's strategic imperative: keep investing in PyTorch's CUDA backend, keep NVIDIA engineers contributing to PyTorch core, keep the CUDA path the fastest and most reliable. If PyTorch ever becomes truly hardware-agnostic with equal performance across backends, the CUDA moat fundamentally changes.

**Stack thinking: NVIDIA must own value at multiple layers.** Jensen's response to software-layer competition is to compete at multiple layers simultaneously. Not just hardware (GPU), not just low-level software (CUDA), but also:
- Middle layer: Libraries (cuDNN, NCCL, TensorRT)
- Upper layer: Frameworks and tools (NIM, NeMo, AI Enterprise)
- Distribution: Partnerships with every cloud, every framework, every tool vendor

The more layers NVIDIA controls, the harder it is for any single open-source tool to commoditize the stack.

## How It Connects

- [NIM & NeMo](../software/nim-nemo.md) — NVIDIA's direct response to vLLM and Hugging Face commoditization risk
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — the foundational software moat that open-source tools could abstract away
- [CUDA Moat](../concepts/cuda-moat.md) — software landscape dynamics are the primary vector by which the CUDA moat could weaken
- [AMD](amd.md) — open-source tools that support ROCm make AMD hardware more viable
- [Google TPU](google-tpu.md) — JAX represents the alternative framework pathway to Google hardware
- [Custom ASICs](custom-asics.md) — hardware-agnostic software tools make custom ASICs more viable for a broader range of workloads
- [AI Enterprise](../software/ai-enterprise.md) — NVIDIA's enterprise software layer that competes with open-source alternatives
- [Inference Economy](../concepts/inference-economy.md) — inference serving tools (vLLM, TensorRT-LLM) are critical as inference becomes the dominant workload

## Jensen's Framing

Jensen addresses the software-layer competitive threat through his consistent emphasis on NVIDIA as a software company, not just a hardware company. At GTC 2025 and 2026, he devoted significant keynote time to NIM, TensorRT-LLM, and NVIDIA's software offerings — a clear signal that Jensen views the software layer as a strategic battleground, not just a value-add.

On why NVIDIA invests in software:

> "We are a platform computing company. We don't sell chips. We sell the entire stack — from the silicon to the system to the software to the cloud."

This framing directly addresses the commoditization risk: if NVIDIA sells only chips, it can be commoditized by the software layer above. If NVIDIA sells the stack, it competes at every layer and cannot be easily abstracted away.

On the developer ecosystem as moat:

> "The rich developer ecosystem is really valued, and really, really deeply appreciated."

Jensen's argument: open-source tools like Hugging Face and vLLM are part of the NVIDIA ecosystem when they are CUDA-optimized. The key is ensuring that the highest-performance path through these tools goes through NVIDIA hardware. As long as vLLM-on-NVIDIA is faster than vLLM-on-AMD, the open-source tool actually reinforces the moat rather than eroding it.

On NIM specifically, Jensen has framed it as "inference as a microservice" — making NVIDIA-optimized inference as easy to deploy as any container. This is a direct competitive response to vLLM's ease of use: if NIM is as simple as vLLM but 30% faster, developers will choose NIM, and NIM only runs on NVIDIA.

Jensen's general philosophy on software competition aligns with his stack thinking: do not try to block open-source tools (they will win on adoption). Instead, make NVIDIA's stack the best-performing runtime beneath those tools, and offer NVIDIA's own higher-layer tools (NIM, TensorRT-LLM) for customers who want maximum performance. Compete at every layer, win at every layer.
