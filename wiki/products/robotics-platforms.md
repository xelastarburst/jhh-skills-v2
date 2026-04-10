---
title: Robotics Platforms
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# Robotics Platforms

## What It Is
NVIDIA's robotics platform is the hardware and software stack for autonomous machines — from warehouse AMRs to surgical robots to humanoids. It spans edge compute modules (Jetson Orin, Jetson Thor), industrial-grade systems (IGX Orin), reference robot designs (Isaac Nova), simulation and training infrastructure (Isaac Sim, Isaac Lab, Cosmos), and a humanoid foundation model (Project GR00T). Jensen's thesis: every robot needs a brain (Jetson), a training ground (Isaac Sim), and a world model (Cosmos). NVIDIA provides all three. This is "CUDA for robots" — the goal is to make NVIDIA's platform the default compute and software layer for the entire robotics industry, just as CUDA became the default for AI research.

## Key Facts

### Jetson Thor (Next-Generation Robotics SoC)
- Next-gen robotics compute module, successor to Jetson Orin
- Based on NVIDIA Thor SoC: same silicon lineage as DRIVE Thor automotive SoC
- Up to 800 TOPS (INT8 AI performance) — a massive step up from Orin's 275 TOPS
- Blackwell-generation GPU architecture + Arm Grace CPU cores
- Designed for humanoid robots, advanced manipulation, and autonomous mobile robots
- Supports large foundation models on-device: can run multi-billion-parameter transformer models at the edge
- Transformer Engine for efficient transformer inference
- Functional safety capable for industrial/collaborative robot applications
- Announced GTC 2024; expected availability 2025

### Jetson Orin (Current-Generation, In Production)
- **Jetson AGX Orin**: flagship module, 275 TOPS (INT8), Ampere GPU + 12-core Arm Cortex-A78AE CPU
- 64 GB LPDDR5 memory, 204.8 GB/s memory bandwidth (AGX Orin 64GB variant)
- Power configurable: 15W to 60W
- **Jetson Orin NX**: mid-range, up to 100 TOPS, 8/16 GB LPDDR5
- **Jetson Orin Nano**: entry-level, up to 40 TOPS (INT8), 4/8 GB LPDDR5
- Supported by JetPack SDK (CUDA, cuDNN, TensorRT, VPI, multimedia APIs)
- Widely deployed: over 1,000 partners and customers building on Jetson Orin as of 2024
- Used in delivery robots, warehouse AMRs, agricultural robots, inspection drones, retail automation

### IGX Orin (Industrial Edge AI)
- Industrial-grade edge AI platform for environments requiring functional safety
- Based on Jetson Orin compute with additional safety and security features
- **IGX Orin Developer Kit**: Jetson AGX Orin + ConnectX-7 SmartNIC + enterprise-grade enclosure
- Designed for medical devices, industrial inspection, manufacturing quality control
- Supports NVIDIA Holoscan SDK for streaming AI pipelines (especially medical/industrial sensor data)
- Pre-certified for functional safety standards (ISO 13849, IEC 62443)
- Long lifecycle support (10+ years) for industrial deployments

### Isaac Nova Orin (Reference Robot Platform)
- Reference hardware and software platform for autonomous mobile robots (AMRs)
- Compute: Dual Jetson AGX Orin modules (550 TOPS combined)
- Sensors: 2x front stereo cameras, 2x rear stereo cameras, 3D lidar (optional), 2D safety lidars, IMU
- Pre-integrated with Isaac ROS software stack
- Open design: OEMs can customize chassis, sensors, and software while keeping the validated compute/perception stack
- Targets warehouse logistics, manufacturing floor transport, last-mile delivery
- Announced GTC 2024

### Project GR00T (Humanoid Foundation Model)
- Foundation model for humanoid robot learning: takes multimodal input (language, video, demonstration) and outputs robot actions
- Stands for "Generalist Robot 00 Technology"
- Architecture: large multimodal transformer trained on human motion data, simulation data, and language instructions
- Training pipeline: human demonstration capture -> Isaac Sim simulation -> Cosmos world model for data augmentation -> GR00T model training -> sim-to-real transfer -> real robot deployment
- Designed to work across different humanoid form factors — not tied to one robot manufacturer
- Announced GTC 2024, with ongoing development through 2025-2026
- Humanoid robot partners working with GR00T: Agility Robotics (Digit), Apptronik (Apollo), Boston Dynamics, 1X Technologies (NEO), Figure AI (Figure 02), Sanctuary AI, Unitree, XPENG Robotics, and others
- Jensen positions this as the "ChatGPT moment for robots" — a general-purpose model that makes robots useful across diverse tasks

### Isaac Sim / Isaac Lab / Cosmos (Software Ecosystem)
- **Isaac Sim**: GPU-accelerated, physically accurate robot simulation built on Omniverse (OpenUSD)
- **Isaac Lab**: reinforcement learning and robot learning framework built on Isaac Sim (successor to Isaac Gym, which trained robot policies 1000x faster than real-time)
- **Cosmos**: world foundation model for generating synthetic training environments and predicting physical outcomes; generates diverse, photorealistic synthetic data for robot training
- **Isaac ROS**: hardware-accelerated ROS 2 packages for perception, navigation, and manipulation; runs on Jetson
- **Isaac Manipulator**: perception and motion planning for robot arms
- **Isaac Perceptor**: 3D perception stack for mobile robots (stereo vision, lidar fusion, mapping)
- The full pipeline: train in Isaac Sim -> augment with Cosmos -> deploy on Jetson with Isaac ROS

## Strategic Significance

Robotics is Jensen's next "zero-billion-dollar market" — and possibly the biggest. The reasoning chain mirrors the CUDA bet: establish the platform early, build install base, create ecosystem lock-in, then capture value as the market explodes.

**Why this matters in Jensen's framework:**

1. **"Every robot needs a brain."** There are an estimated 3-4 million industrial robots deployed worldwide and tens of millions of potential autonomous machines (warehouses, farms, hospitals, construction, homes). Each one needs edge AI compute. Jetson is positioned to be the default robotics compute platform — "CUDA for robots." If Jetson becomes to robots what Qualcomm Snapdragon is to phones, the TAM is enormous.

2. **Platform economics, not component sales.** NVIDIA isn't selling a chip — it's selling the entire development and deployment platform: Jetson hardware + Isaac Sim for training + Isaac ROS for deployment + Cosmos for world modeling + GR00T for humanoid intelligence. A robotics company that adopts this full stack has switching costs at every layer. The training data was generated in Isaac Sim. The policies were validated in Cosmos. The deployment runs on Jetson. You can't swap out one layer without revalidating the entire pipeline.

3. **GR00T is the foundation model play.** Just as ChatGPT demonstrated that a single foundation model could handle diverse language tasks, GR00T aims to show that a single foundation model can handle diverse physical manipulation tasks. If GR00T works, it becomes the "model layer" of the robotics stack — and every humanoid robot company needs access to it. This is the NIM/NeMo pattern applied to Physical AI: NVIDIA trains the foundation model, then licenses it as a microservice.

4. **Simulation-to-reality is the flywheel.** Robot training requires vast amounts of diverse, physically accurate data. Collecting this in the real world is slow, expensive, and dangerous. Isaac Sim + Cosmos generate unlimited synthetic training data. Better simulation -> better robot policies -> more robot deployments -> more real-world data -> better simulation. This is a data flywheel that compounds with scale.

5. **Humanoid robots are the "speed of light" opportunity.** If humanoid robots eventually reach human-level physical capability, the TAM is the entire labor market. Jensen sizes this against the theoretical maximum, not the current market. The current market for humanoid robots is approximately zero. The theoretical maximum is hundreds of millions of units. That gap IS the opportunity.

6. **Shared silicon with automotive.** Jetson Thor and DRIVE Thor share the same SoC lineage. This is Jensen's "one architecture" approach: amortize R&D across automotive and robotics, give both markets the benefit of scale, and create a unified software platform (Isaac + DRIVE) for all Physical AI applications.

## How It Connects
- [Isaac & Cosmos](../software/isaac-cosmos.md) — the simulation and world model software that trains robots on NVIDIA hardware
- [Physical AI](../concepts/physical-ai.md) — robotics platforms are the hardware instantiation of the Physical AI thesis
- [Robotics & Physical AI Market](../markets/robotics-physical-ai.md) — market dynamics, humanoid robot economics, deployment trends
- [DRIVE Platform](drive-platform.md) — shared SoC architecture (Orin/Thor) and Physical AI approach between auto and robotics
- [Omniverse](../software/omniverse.md) — Isaac Sim is built on Omniverse; digital twin technology for robot workcells
- [CUDA Ecosystem](../software/cuda-ecosystem.md) — Jetson runs the full CUDA stack; JetPack SDK is the robot developer's toolkit

## Jensen's Framing

On the robotics opportunity (GTC 2024):

> "The next wave of AI is Physical AI — AI that understands the physical world. We have digital agents. Now we will have physically embodied agents. We call them robots. And every robot, every autonomous machine, needs a brain. We built it. It's called Jetson."

On Project GR00T (GTC 2024):

> "GR00T is a foundation model for humanoid robots. It takes multimodal instructions and produces actions. Just like large language models learned to understand and generate language, GR00T learns to understand and generate physical actions. This is the ChatGPT moment for robotics."

On simulation as the training ground:

> "You can't train a robot by crashing it into walls a million times. You train it in simulation — Isaac Sim generates physically accurate worlds, Cosmos generates the diversity. A robot can experience a lifetime of learning in a day of simulation. Then you transfer that knowledge to the real world. Simulation is the gym. The real world is the game."

On humanoid robots and the labor market (GTC 2025/CES 2025):

> "The market for humanoid robots will be the largest technology market the world has ever seen. Think about it — what is the addressable market for a general-purpose worker that can go anywhere a human can go, do anything a human can do? It's the entire economy."

On platform economics:

> "We're not building a robot. We're building the platform that every robot maker builds on. Just like we didn't build the self-driving car — we built the platform that every car maker uses. One architecture, one software stack, from factory floor to humanoid."
