---
title: Isaac & Cosmos
last_updated: 2026-04-09
freshness: quarterly
category: software
---

# Isaac & Cosmos

## What It Is
Isaac and Cosmos together form NVIDIA's end-to-end pipeline for physical AI — from simulation to real-world deployment. Isaac is the robotics platform: Isaac Sim for high-fidelity robot simulation, Isaac ROS for deploying perception and navigation on real robots, and Isaac Lab for reinforcement learning. Cosmos is the newer, more ambitious piece: world foundation models that learn the physics and visual dynamics of the real world from video data, enabling AI systems to understand friction, inertia, occlusion, and cause-and-effect. In Jensen's vision, Cosmos models generate the synthetic training data and scenarios that Isaac Sim uses to train robot policies, closing the simulation-to-reality gap that has historically been the hardest problem in robotics.

## Key Facts
- **Isaac Sim**:
  - Built on NVIDIA Omniverse (OpenUSD-based)
  - Physically accurate simulation: rigid body, articulated body, deformable body, fluid dynamics via PhysX 5
  - High-fidelity rendering via RTX ray tracing for synthetic data generation (SyntheticData pipeline)
  - Domain randomization for sim-to-real transfer (lighting, textures, object placement, physics parameters)
  - Supports ROS 2 bridge for direct integration with robot software stacks
  - Pre-built robot assets: manipulators (Franka, UR5/10, Kuka), mobile robots, humanoids
  - Cloud-available via Omniverse Cloud and NVIDIA DGX Cloud
- **Isaac ROS**:
  - Hardware-accelerated ROS 2 packages for NVIDIA Jetson and GPU platforms
  - Modules for visual SLAM, stereo depth, object detection/pose estimation, path planning
  - NITROS (NVIDIA Isaac Transport for ROS) for zero-copy GPU-accelerated data transport
  - Provides the bridge from simulation-trained models to real-world deployment
- **Isaac Lab** (formerly Orbit):
  - GPU-accelerated reinforcement learning environment built on Isaac Sim
  - Supports thousands of parallel simulation instances for massive RL training
  - Locomotion, manipulation, and navigation benchmark tasks
  - Integration with RL frameworks (Stable Baselines3, rl_games, RSL-rl)
- **Cosmos World Foundation Models**:
  - Announced at CES 2025, expanded through 2025-2026
  - Video generation/prediction models that learn physical world dynamics from large-scale video data
  - Understand physics: gravity, friction, inertia, collisions, fluid dynamics, cause-and-effect
  - Multiple model sizes and architectures for different use cases (video prediction, scene understanding, action-conditioned generation)
  - Open model weights for research and customization via NVIDIA NGC
  - Can generate realistic edge-case scenarios for training (e.g., rare traffic situations for AVs, unusual object configurations for manipulation)
  - Trained on massive proprietary + licensed video datasets
- **Simulation-to-Reality Pipeline**:
  - Design robot in CAD (imported via USD) -> Simulate in Isaac Sim -> Train policies with Isaac Lab -> Generate edge cases with Cosmos -> Deploy with Isaac ROS -> Collect real-world data -> Improve simulation fidelity -> Repeat

## Strategic Significance
Isaac + Cosmos is how Jensen makes the physical AI thesis tangible and commercially real:

1. **Solving the data problem for physical AI.** The fundamental bottleneck in robotics is not algorithms — it is data. You cannot collect enough real-world training data for every scenario a robot will encounter. Cosmos generates realistic synthetic scenarios (the "long tail" of edge cases), and Isaac Sim provides the physics-accurate environment to train on them. This is Jensen's answer to the question "how do you train a robot?"

2. **Cosmos creates a new model category.** Jensen positions world foundation models as the third category of foundation model after language models and image/video generation models. "LLMs understand words. Diffusion models understand pixels. World foundation models understand physics." If this category takes hold, NVIDIA defines and leads it from day one.

3. **Complete pipeline lock-in.** Isaac Sim (simulation) + Isaac Lab (training) + Cosmos (synthetic data) + Isaac ROS (deployment) + Jetson (edge hardware) = every stage of the robotics development pipeline runs on NVIDIA. There is no equivalent end-to-end stack from any competitor.

4. **Flywheel with Omniverse.** Isaac Sim is built on Omniverse. Cosmos models can feed into Omniverse environments. Real-world data improves both. This creates a virtuous cycle where each component makes the others more valuable.

5. **Enabling the robotics market NVIDIA needs.** NVIDIA sells Jetson hardware for robot deployment. But that market only scales if robots actually work in the real world. Isaac + Cosmos is NVIDIA's investment in making robotics actually viable, thereby creating the market for its own edge hardware.

## How It Connects
- [Omniverse](omniverse.md) — Isaac Sim is built on Omniverse; Cosmos generates environments for Omniverse
- [Robotics Platforms](../products/robotics-platforms.md) — Jetson Thor / IGX are the deployment hardware for Isaac-trained robots
- [Physical AI](../concepts/physical-ai.md) — Isaac + Cosmos is the implementation of the physical AI thesis
- [Robotics & Physical AI Market](../markets/robotics-physical-ai.md) — Isaac + Cosmos enables the market NVIDIA is targeting
- [DRIVE Platform](../products/drive-platform.md) — DRIVE Sim shares the Omniverse foundation; Cosmos generates AV training scenarios

## Jensen's Framing
Jensen's language around Isaac and Cosmos draws heavily on the physical AI thesis he has been building since GTC 2024:

> "We now have AI that can understand language. We have AI that can generate images and video. The next frontier is AI that understands the physical world — that understands friction, inertia, cause and effect. That's what Cosmos is."
> -- Jensen Huang, GTC 2025 keynote (paraphrased)

At CES 2025, introducing Cosmos, Jensen framed it as solving the fundamental data bottleneck: "To train a robot, you need to show it the world. But you can't show it every possible scenario in the real world. Cosmos generates physically plausible worlds — it reasons about edge cases, about rare events, about the long tail of reality. It's the world's first world foundation model."

Jensen connects this directly to the robotics business opportunity: "The robotics industry is a multi-trillion dollar opportunity. But it's been held back by one thing: the cost and difficulty of training robots to operate in the real world. Isaac and Cosmos together solve that problem. They let you build, train, and test a robot entirely in simulation, then deploy it with confidence."

On the simulation-to-reality gap, Jensen emphasizes that Cosmos is the bridge: "The gap between simulation and reality has always been the hardest problem. Cosmos closes that gap by learning what the real world actually looks like, how it actually behaves. It brings realism to simulation that was never possible before."
