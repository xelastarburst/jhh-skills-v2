---
title: Three Waves of AI
last_updated: 2026-04-09
freshness: evergreen
category: concepts
---

# Three Waves of AI

## What It Is

Jensen frames the evolution of AI as three successive waves, each expanding what AI can do, each multiplying the demand for compute, and each building on the capabilities of the prior wave. Wave 1 is Perception — AI learns to see, hear, and read. Wave 2 is Generation — AI learns to create text, images, video, and code. Wave 3 is Agentic — AI learns to act autonomously, reason through multi-step problems, and operate in the real world. Jensen uses this framework to explain both the history of AI compute demand and the roadmap for where it goes next. Each wave is not a replacement but a stacking — agentic AI requires generation, which requires perception. The compound effect is exponential growth in compute demand.

## Key Facts

- **Wave 1: Perception (2012-2020)**
  - AI learns to classify, detect, and interpret sensory inputs.
  - Key milestones: AlexNet (2012) proved GPUs could train image classifiers. This triggered NVIDIA's all-in bet on deep learning.
  - Domains: computer vision (image classification, object detection, facial recognition), natural language processing (sentiment analysis, named entity recognition, machine translation), speech recognition (Siri, Alexa, Google Assistant).
  - Compute pattern: training is expensive but inference per query is lightweight — a single forward pass through a classifier.
  - NVIDIA products: Tesla/Volta/Ampere GPUs for training, TensorRT for edge inference deployment.
  - Market impact: created the first wave of AI startups and the initial demand for GPU training clusters.

- **Wave 2: Generation (2020-2024)**
  - AI learns to create — not just classify inputs but generate novel outputs.
  - Key milestones: GPT-3 (2020) demonstrated large language models could generate coherent text. DALL-E/Stable Diffusion (2022) proved image generation. ChatGPT (November 2022) brought generative AI to mass adoption.
  - Domains: large language models (text generation, code generation, summarization), image generation (diffusion models), video generation (Sora, Runway), music and audio generation.
  - Compute pattern: training costs explode (billions of dollars for frontier models) AND inference demand grows massively — every user interaction generates tokens.
  - NVIDIA products: H100 became the workhorse of this wave; every frontier model trained primarily on H100 clusters.
  - Market impact: created the "GPU shortage" era (2023-2024), proved Jensen's thesis about insatiable compute demand, and established the inference economy as a real market.

- **Wave 3: Agentic (2024-present)**
  - AI learns to act — not just generate outputs but reason, plan, use tools, and execute multi-step tasks autonomously.
  - Key milestones: Reasoning models (OpenAI o1/o3, DeepSeek-R1) that use chain-of-thought to "think" before answering. AI agents that can browse the web, write and execute code, manage workflows, and operate software systems.
  - Domains: AI agents for enterprise workflows, coding agents, research agents, customer service agents, robotic control agents, autonomous driving agents.
  - Compute pattern: inference demand explodes exponentially. A single agent task might involve dozens of reasoning steps, each generating hundreds of tokens. Agents operate in loops — plan, act, observe, reason, repeat — consuming continuous inference compute. Millions of concurrent agents operating 24/7 create an always-on inference load.
  - NVIDIA products: Blackwell optimized for inference, NIM for agent deployment, NeMo Guardrails for agent safety.
  - Market impact: this is the wave Jensen argues will make inference 100x training. Every enterprise will deploy agents, and every agent runs inference continuously.

- **Each wave multiplies compute demand**: Perception required training clusters. Generation required massive training AND inference. Agentic requires massive training AND massive continuous inference AND reasoning loops. The compute demand curve is not linear — it is exponential across waves.

- **Waves stack, not replace**: Agentic AI uses generative models (Wave 2) to produce text and code, which use perception models (Wave 1) to interpret inputs. An autonomous agent might use computer vision to perceive its environment, an LLM to reason about what to do, and tool-use capabilities to act. All three waves running simultaneously on GPU infrastructure.

## Strategic Significance

Jensen uses the three waves framework for three strategic purposes:

1. **Explaining why compute demand is insatiable.** Each wave is a step function increase in demand, and we are entering Wave 3 — the most compute-intensive wave yet. This justifies NVIDIA's continued investment in next-generation infrastructure and argues against anyone who claims AI compute demand will plateau.

2. **Timing product strategy.** NVIDIA's product roadmap tracks the waves. Hopper was the Wave 2 product (training frontier generative models). Blackwell is the Wave 2/3 bridge (optimized for both generation and inference). The next architectures will be increasingly optimized for agentic workloads — continuous inference, low-latency reasoning, multi-agent orchestration.

3. **Connecting to physical AI.** Jensen treats Wave 3 as bifurcating into digital agents (software agents operating in digital environments) and physical agents (robots, autonomous vehicles operating in the real world). Physical AI is the extension of the agentic wave into the physical world — and it requires an entirely new compute stack (simulation, world models, embodied AI). This is how the three waves framework connects to the physical AI thesis.

4. **Making the case for infrastructure investment.** For enterprises, the three waves framework is a roadmap: "You invested in AI for perception (analytics). You invested in AI for generation (chatbots, copilots). Now you need to invest in AI for agents — and agents need 10-100x more inference infrastructure." Each wave is a new buying cycle.

## How It Connects

- [Inference Economy](inference-economy.md) — Wave 3 (agentic) is the primary driver of the inference economy thesis
- [Physical AI](physical-ai.md) — Physical AI is the extension of Wave 3 into the physical world
- [Data Center AI](../markets/data-center-ai.md) — Each wave drives a new cycle of data center infrastructure investment

## Jensen's Framing

> "The first wave of AI was perception — AI learned to see, to hear, to read. The second wave was generation — AI learned to create. The third wave is agentic AI — AI that can reason, plan, and act."
> -- Jensen Huang, GTC 2025 keynote (paraphrased from keynote summaries, everestgrp.com and indianexpress.com)

> "The demand for AI infrastructure is insatiable. Every GPU we ship is absorbed immediately."
> -- Jensen Huang, Acquired FM interview (2024), on the exponential compute demand across waves

> "We have digital agents. Now we have physically embodied agents. We call them robots."
> -- Jensen Huang, GTC 2026 keynote (Data Center Frontier summary), connecting Wave 3 to physical AI

> "AI crossed an important threshold — models became good enough to be useful at scale."
> -- Jensen Huang, Stratechery interview (March 2026), on the transition from Wave 2 experimentation to Wave 3 production deployment

> "Intelligence is the ability to recognize patterns, recognize relationships, reason about it and make a prediction or plan an action."
> -- Jensen Huang, Stratechery interview (2022) — a definition that spans all three waves: perception (recognize), generation (predict), agentic (plan and act)

> "The next big thing is Physical AI, AI with a body."
> -- Jensen Huang, GTC Paris (RS Online/DesignSpark summary), on where Wave 3 leads
