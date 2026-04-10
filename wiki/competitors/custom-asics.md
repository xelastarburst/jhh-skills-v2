---
title: Custom ASICs
last_updated: 2026-04-09
freshness: quarterly
category: competitors
---

# Custom ASICs (Hyperscaler Custom Silicon)

## What It Is

Custom ASICs are purpose-built AI accelerator chips designed by the major cloud hyperscalers — Amazon (Trainium/Inferentia), Microsoft (Maia), Google (TPU, covered separately), and Meta (MTIA) — to reduce dependence on NVIDIA GPUs and improve the economics of their AI infrastructure. At the whiteboard, Jensen would circle this category and say: this is the real competitive threat, not AMD. Hyperscalers have captive demand (they consume their own chips), deep pockets (hundreds of billions in capex), and strategic motivation (reducing NVIDIA's pricing power). But they face the same fundamental problem as every NVIDIA competitor: custom ASICs are products optimized for specific workloads, while NVIDIA is a platform that serves all workloads. The richer the developer ecosystem, the harder it is for a single-purpose chip to displace the general-purpose platform.

## Key Facts

### AWS Trainium / Inferentia
- **Trainium2** (announced re:Invent 2023, available 2024-2025): AWS's second-generation training chip. Up to 65% better price-performance vs Trainium1 (per AWS). Available in EC2 Trn2 instances (16 Trainium2 chips per instance). Trn2 UltraServers connect multiple Trn2 instances via NeuronLink for scale-out training. 2,048-chip Trn2 UltraClusters available for large model training. Integrated into Amazon SageMaker.
- **Trainium3** (announced, expected 2025-2026): Next-generation training chip built on "more advanced process node." AWS claims it will deliver significant performance improvements. Limited specs disclosed.
- **Inferentia2** (launched 2022): Inference-optimized chip. Available as EC2 Inf2 instances. Supports large model inference with up to 12 Inferentia2 chips per instance (192 GB total accelerator memory). Competitive pricing for inference workloads on AWS.
- **Software**: AWS Neuron SDK — custom compiler and runtime. Supports PyTorch and TensorFlow through Neuron plugin. Key limitation: not all PyTorch operations are supported natively; some models require modification to run on Trainium/Inferentia. The Neuron SDK is functional but has a narrower set of supported model architectures compared to CUDA.
- **Adoption**: Amazon has been aggressive about deploying Trainium internally (Alexa, Amazon Search, AWS AI services). Anthropic announced a significant partnership with AWS to use Trainium chips for Claude training. Some AWS customers use Inferentia2 for cost-optimized inference. However, the vast majority of ML training on AWS still runs on NVIDIA GPUs (P5/P5e instances with H100/H200).
- **Strategic context**: AWS spends tens of billions annually on NVIDIA GPUs. Trainium is a direct response — build your own chips to reduce per-unit cost and dependency. AWS's Annapurna Labs (acquired 2015 for ~$350M) designs the chips.

### Microsoft Maia
- **Maia 100** (announced November 2023, deployed 2024-2025): Microsoft's first custom AI accelerator. TSMC 5nm process. Designed for training and inference of Microsoft's internal AI workloads (Copilot, Bing, Azure OpenAI Service). Liquid-cooled. Deployed alongside custom Azure Cobalt Arm-based CPU. Limited public specs — Microsoft has not disclosed TFLOPS or detailed memory specifications.
- **Software**: Integrated into Microsoft's internal ML infrastructure. Not available as a standalone Azure service for external customers as of early 2026. Microsoft's approach is to use Maia for internal workloads and continue offering NVIDIA GPUs (H100, A100, B200) for external Azure customers.
- **Strategic context**: Microsoft is NVIDIA's largest customer and strategic partner (Azure hosts DGX Cloud, Azure offers extensive NVIDIA GPU instances). Maia is Microsoft's hedge — internal chip development to reduce long-term NVIDIA dependency for Microsoft's own AI services (GitHub Copilot, Microsoft 365 Copilot, Bing Chat). This is supply diversification, not replacement.

### Meta MTIA
- **MTIA v1** (announced 2023): Meta's first custom inference chip. Designed for recommendation and ranking model inference (Instagram, Facebook feed, ads). Modest performance tier — not competing with H100 on transformer training. TSMC 7nm.
- **MTIA v2** (announced 2024): Significant performance upgrade. TSMC 5nm. 3x compute, 6x memory bandwidth, and 1.5x increased efficiency over v1. Meta frames MTIA as complementary to NVIDIA GPUs, not a replacement — MTIA handles recommendation/ranking workloads while NVIDIA GPUs handle generative AI training.
- **Strategic context**: Meta is one of NVIDIA's largest GPU customers (massive H100/H200 deployments for Llama training). MTIA targets a specific workload tier (recommendations), not general-purpose AI training.

### Google Axion
- **Axion** (announced Google Cloud Next 2024): Google's custom Arm-based CPU (not an AI accelerator). Based on Arm Neoverse V2. Designed for general-purpose cloud compute workloads, not AI training/inference. Competes with AWS Graviton and Azure Cobalt, not with GPUs or TPUs. Included here for completeness as part of the hyperscaler custom silicon trend.
- Google's actual AI accelerator is the TPU — see [Google TPU](google-tpu.md) for detailed coverage.

### Broadcom / Marvell Custom ASIC Design Services
- Both Broadcom and Marvell provide ASIC design services that enable hyperscalers to build custom chips. Broadcom is reported to work with Google (TPU) and other hyperscalers on custom AI accelerator designs. Marvell similarly supports custom silicon programs. These companies are the picks-and-shovels of the custom ASIC movement — enabling hyperscalers to compete with NVIDIA without building full chip design teams from scratch.

## Strategic Significance

Jensen's framework identifies custom ASICs as the most strategically significant competitive threat — more so than AMD or Intel — because hyperscalers have the three things other competitors lack: captive demand, capital, and motivation.

**Why custom ASICs are the real threat.** Apply Jensen's competitive reasoning:

1. **Captive demand**: Hyperscalers consume their own chips. AWS does not need to convince external customers to adopt Trainium for the economics to work — Amazon's own AI services are a massive workload. This bypasses the ecosystem problem: you do not need a developer community if your developers are your own employees.
2. **Deep pockets**: AWS, Microsoft, Google, and Meta each spend $40-80B+ annually on capex. They can sustain custom chip programs through multiple generations even without external adoption.
3. **Strategic motivation**: Every NVIDIA GPU purchased gives NVIDIA pricing power over the hyperscaler. Custom silicon is a negotiating lever even if it never fully replaces NVIDIA — the credible threat of switching keeps NVIDIA's margins in check.

**The platform vs product limitation.** Jensen would immediately apply his platform-vs-product test. Trainium is a product (optimized for specific training workloads on AWS). Maia is a product (optimized for Microsoft's internal inference). MTIA is a product (optimized for Meta's recommendation models). NVIDIA's GPU is a platform (runs any workload, any framework, any model, on any cloud or on-prem).

The practical implication: custom ASICs work well for the top 10-20 workloads that represent 80% of a hyperscaler's compute. LLM training, LLM inference serving, recommendation ranking, search ranking — these are well-defined, high-volume workloads where custom silicon can be optimized. But the long tail of ML workloads — research experimentation, novel architectures, small-batch training, custom model types, scientific computing — still requires the generality of NVIDIA's platform.

**The ecosystem moat at its most relevant.** Jensen's moat test applied to custom ASICs:

- Can a researcher take their PyTorch training script and run it unmodified on Trainium? Not always — the Neuron SDK supports a subset of operations, and some models require modification.
- Can a startup building a new model architecture prototype on Trainium with the same ease as on CUDA? No — CUDA has 20 years of libraries, profiling tools, debugging tools, documentation, and community knowledge.
- Can a hyperscaler's own ML engineers use Trainium for all their workloads? Not yet — which is why AWS, Microsoft, and Meta all continue to buy massive volumes of NVIDIA GPUs alongside their custom silicon.

The CUDA ecosystem does not just compete with custom ASICs on performance — it competes on convenience, flexibility, and developer productivity. These are harder to replicate than TFLOPS.

**The negotiating leverage dynamic.** Jensen understands (and would acknowledge) that custom ASICs serve a dual purpose: direct cost savings on internal workloads AND negotiating leverage against NVIDIA pricing. Even if Trainium only handles 20% of AWS's ML compute, its existence gives AWS a credible alternative that moderates NVIDIA's pricing. This is rational procurement strategy, and Jensen would respect it as such.

**What must be true for custom ASICs to succeed broadly:**
1. The Neuron SDK / Maia software / MTIA toolchain must reach "good enough" for high-volume workloads (emerging — improving each generation)
2. Hyperscalers must invest through multiple chip generations to close the performance gap (they are doing this — Trainium2 to Trainium3, MTIA v1 to v2)
3. The workload mix must stabilize enough that purpose-built silicon can target it (partially true — LLM training/inference is standardizing)
4. The CUDA ecosystem advantage must weaken or become less relevant (not yet — CUDA's lead is widening at the library/tooling layer even as hardware alternatives improve)

Jensen's assessment: conditions 1-3 are emerging. Condition 4 is the firewall. NVIDIA's strategic response is to deepen the software stack (NIM, TensorRT-LLM, CUDA libraries, AI Enterprise) faster than custom ASICs can replicate it.

## How It Connects

- [Google TPU](google-tpu.md) — the original and most mature custom AI ASIC program
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — the software moat that limits custom ASIC displacement
- [CUDA Moat](../concepts/cuda-moat.md) — custom ASICs are the primary threat the CUDA moat must defend against
- [Data Center AI](../markets/data-center-ai.md) — custom ASICs represent 10-20% of hyperscaler AI compute and growing
- [AMD](amd.md) — AMD and custom ASICs both serve hyperscaler supply diversification goals
- [DGX Systems](../products/dgx-systems.md) — DGX's full-stack integration is NVIDIA's response to component-level competition
- [Blackwell GPU Architecture](../products/gpu-blackwell.md) — Blackwell's rack-scale design raises the bar for custom ASIC competitiveness

## Jensen's Framing

Jensen addresses the custom ASIC threat through his platform and ecosystem arguments rather than by naming specific competitors. His reasoning is structural:

> "The rich developer ecosystem is really valued, and really, really deeply appreciated." — Jensen's explanation of why cloud providers continue to support CUDA even as they develop custom silicon. The ecosystem demand comes from cloud customers, not from NVIDIA's marketing.

On why the full stack matters against component-level competition:

> "We don't sell chips. We sell the entire stack — from the silicon to the system to the software to the cloud."

Jensen's implicit argument against custom ASICs: a chip is one layer of the stack. NVIDIA sells the entire stack. Custom ASICs must replicate not just the chip but the NVLink fabric, the system software, the CUDA libraries, the developer tools, the optimization frameworks, and the ecosystem of ISVs — or they must operate in a narrower domain where this full stack is not needed.

At GTC 2025, Jensen's emphasis on the GB200 NVL72 as "one GPU" (72 GPUs connected via NVLink as a single system) was an indirect competitive statement. Custom ASICs like Trainium can scale to multi-chip configurations, but they lack the equivalent of NVLink's 1.8 TB/s per-GPU bandwidth and NVSwitch's non-blocking topology. The system-level integration gap is wider than the chip-level gap.

On the inference economy, Jensen has noted that inference workloads are more diverse than training workloads — different model sizes, different latency requirements, different batch sizes, different precision needs. This diversity favors a general-purpose platform (NVIDIA) over purpose-built ASICs that optimize for specific inference profiles. As the inference economy grows and workloads diversify, the platform advantage should strengthen, not weaken.

Jensen has also addressed the supply diversification dynamic directly: NVIDIA's response is not to fight it but to make the NVIDIA platform so much better that the "diversification tax" (running workloads less efficiently on alternative hardware) becomes harder to justify. Blackwell's performance-per-dollar improvements, NIM's inference optimization, and TensorRT-LLM's efficiency gains all serve this goal — make NVIDIA the better economic choice even when the customer has alternatives.
