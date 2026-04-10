---
title: DRIVE Platform
last_updated: 2026-04-09
freshness: quarterly
category: products
---

# DRIVE Platform

## What It Is
NVIDIA DRIVE is the end-to-end platform for autonomous vehicles and advanced driver assistance systems (ADAS). It spans the full stack: in-vehicle compute (DRIVE Orin and DRIVE Thor SoCs), a sensor reference architecture (Hyperion), simulation infrastructure (DRIVE Sim on Omniverse), and software frameworks for perception, mapping, planning, and driver monitoring. Jensen positions DRIVE as "Physical AI applied to transportation" — the same AI stack that trains language models, repurposed to understand and navigate the physical world. NVIDIA does not build cars; it builds the brain, nervous system, and virtual proving ground for every car maker on the planet.

## Key Facts

### DRIVE Thor (Next-Generation SoC)
- Next-generation centralized car computer, succeeding DRIVE Orin
- Up to 2,000 TOPS (INT8 AI performance) — roughly 8x the performance of Orin
- Blackwell-generation GPU architecture integrated on a single SoC
- Designed for centralized compute: runs autonomous driving, parking, driver monitoring, in-cabin AI, and infotainment on one chip (replaces multiple ECUs)
- Supports transformer-based perception models, occupancy networks, and large foundation models on-vehicle
- First vehicles with DRIVE Thor expected 2025-2026 (design wins announced with multiple OEMs)
- Announced GTC 2022, updated specs at GTC 2024 and CES 2025

### DRIVE Orin (Current-Generation SoC)
- 254 TOPS (INT8), based on Ampere GPU + Arm CPU
- In production since 2022-2023 with multiple OEMs
- Supports Level 2+ through Level 4 autonomous driving
- Can be deployed as single chip (254 TOPS) or dual chip (508 TOPS) for higher autonomy levels
- Powers vehicles from Mercedes-Benz, JLR (Jaguar Land Rover), BYD, Li Auto, NIO, XPeng, Volvo/Polestar, Hyundai/Kia, Lucid, and others
- DRIVE Orin is the backbone of NVIDIA's current $14B+ automotive design-win pipeline (as of late 2024/early 2025 disclosure)

### DRIVE Hyperion (Sensor Reference Platform)
- Full sensor suite reference architecture: cameras, lidar, radar, ultrasonics
- **Hyperion 9** (current generation): 12 cameras, 9 radar sensors, 3 lidar sensors, 12 ultrasonics
- Paired with DRIVE Thor compute
- Open architecture — OEMs can modify the sensor configuration while maintaining compatibility with NVIDIA's software stack
- Provides a validated, tested sensor configuration so OEMs don't have to design from scratch

### DRIVE Sim (Simulation)
- Built on NVIDIA Omniverse platform (OpenUSD-based)
- Physically accurate simulation: ray-traced rendering, physics simulation, sensor models
- Generates synthetic training data and provides virtual test miles
- Can simulate rare edge cases (pedestrian darting out, unusual weather) that are dangerous or impractical to test on public roads
- Integrates with DRIVE Chauffeur (autonomous driving software) for closed-loop testing
- Cloud-based — scalable to millions of simulated miles per day

### DRIVE Software Stack
- **DRIVE Chauffeur**: end-to-end autonomous driving software (perception, prediction, planning)
- **DRIVE Concierge**: in-cabin AI assistant (conversational AI, gesture recognition)
- Moving toward foundation-model-based architectures: transformers for perception (occupancy networks), diffusion models for prediction, language models for in-cabin interaction
- **DriveOS**: real-time operating system for safety-critical compute (ASIL-D capable)
- OTA-updatable: software-defined vehicle architecture

### Key Automotive Partnerships
- **Mercedes-Benz**: DRIVE Orin for MB.OS (shipping); DRIVE Thor planned for next-gen
- **JLR (Jaguar Land Rover)**: DRIVE Orin for next-gen vehicles
- **BYD**: DRIVE Orin for multiple EV models, expanding relationship
- **Volvo / Polestar**: DRIVE Orin in production (Volvo EX90)
- **Hyundai / Kia / Genesis**: DRIVE platform across multiple brands
- **Li Auto, NIO, XPeng**: Major Chinese EV makers using DRIVE Orin
- **Lucid Motors**: DRIVE platform
- **Robotaxi companies**: Waymo, Zoox, Cruise (various NVIDIA compute relationships)
- **Trucking**: DRIVE platform used by autonomous trucking companies (Aurora, Kodiak, TuSimple)
- $14B+ automotive design-win pipeline (6-year revenue pipeline disclosed in NVIDIA earnings through 2024)

## Strategic Significance

DRIVE is Jensen's "zero-billion-dollar market" bet on autonomous transportation, and it exemplifies several core principles from his framework.

**Why this matters in Jensen's framework:**

1. **Platform, not product.** NVIDIA does not sell a self-driving car feature. It sells the entire platform — SoC hardware, sensor reference design, simulation infrastructure, software stack, and OTA update capability. This is the stack-thinking approach: own every layer so the OEM's switching cost is total, not incremental. An OEM using DRIVE Thor + Hyperion + DRIVE Sim + DRIVE Chauffeur has zero practical ability to switch to a competitor mid-program.

2. **Zero-billion-dollar market patience.** NVIDIA invested in automotive AI for over a decade before meaningful revenue. The automotive design-win pipeline ($14B+) represents revenue that will be recognized over 6+ years. This is the pattern: invest in a market that "doesn't exist yet" because the reasoning chain says it must emerge. Autonomous driving is the logical endpoint of AI + transportation.

3. **Simulation is the moat.** The hardest problem in autonomous driving isn't building a perception model — it's validating that the model works in every possible scenario. DRIVE Sim, built on Omniverse, generates physically accurate synthetic worlds at scale. This is infrastructure that gets better with more data and more compute — a flywheel. Competitors can match NVIDIA's SoC specs; matching the simulation infrastructure is a multi-year effort.

4. **Centralized compute thesis.** DRIVE Thor's 2,000 TOPS in a single SoC is designed to consolidate every compute function in the car: ADAS, autonomous driving, parking, cabin monitoring, infotainment. This is the "software-defined vehicle" — one brain replacing dozens of ECUs. The revenue per vehicle increases dramatically when NVIDIA's SoC runs everything, not just one function.

5. **Physical AI bridgehead.** Automotive is NVIDIA's first at-scale deployment of Physical AI — AI systems that must understand and interact with the physical world. The technologies developed for DRIVE (world models, simulation-to-reality transfer, embodied AI) transfer directly to robotics. The car is the first robot.

6. **Recurring revenue architecture.** Software-defined vehicles with OTA updates create a recurring revenue opportunity. NVIDIA can sell the initial SoC hardware, then generate ongoing revenue through software updates, new features, and cloud simulation services.

## How It Connects
- [Omniverse](../software/omniverse.md) — DRIVE Sim is built on the Omniverse simulation platform
- [Isaac & Cosmos](../software/isaac-cosmos.md) — shared Physical AI simulation technology; Cosmos world foundation models apply to both driving and robotics
- [Automotive & AV Market](../markets/automotive-av.md) — market dynamics, competitive landscape, revenue pipeline
- [Physical AI](../concepts/physical-ai.md) — DRIVE is the automotive instantiation of the Physical AI thesis
- [Robotics Platforms](robotics-platforms.md) — shared SoC lineage (Orin/Thor) and simulation technology between auto and robotics

## Jensen's Framing

On autonomous vehicles as AI factories on wheels (GTC 2024):

> "A self-driving car is an AI that has a body. It perceives the world, it reasons about the world, it plans, and it acts — in real time, at 60 miles an hour, with human lives at stake. This is the hardest AI problem in the world. And we've been working on it for over a decade."

On DRIVE Thor's centralized compute (CES 2025):

> "One chip runs the entire car. Autonomous driving, parking, cabin monitoring, infotainment — all on one computer. DRIVE Thor is the brain of the software-defined vehicle."

On simulation:

> "You can't test autonomous vehicles only on public roads. You need to simulate billions of miles, billions of scenarios. DRIVE Sim lets you test the untestable — the rare, dangerous, never-before-seen situations that determine whether your car is truly safe. Simulation is how we compress decades of testing into days."

On the automotive pipeline:

> "We have a $14 billion automotive design-win pipeline. That's not revenue today — it's revenue over the next six years. We're playing the long game. Every major car maker in the world is designing their next-generation vehicles on NVIDIA DRIVE."

On Physical AI applied to transportation:

> "The era of Physical AI is here. AI is moving from the digital world into the physical world. And the first — and most important — physical AI application is the autonomous vehicle."
