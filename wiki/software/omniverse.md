---
title: Omniverse
last_updated: 2026-04-09
freshness: quarterly
category: software
---

# Omniverse

## What It Is
Omniverse is NVIDIA's platform for building and operating 3D simulation environments and digital twins, built on the foundation of OpenUSD (Universal Scene Description, originally developed by Pixar). In Jensen's framework, Omniverse is the "simulation computer" — the second of three computers every enterprise will need. It is where you build a physically accurate virtual replica of a factory, a warehouse, a city, or a robot's operating environment, then use that digital twin to simulate, optimize, and validate before deploying changes in the real world. Omniverse connects 3D design tools, physics simulation, and AI in a single platform with real-time collaboration.

## Key Facts
- **Core Platform**:
  - Built on OpenUSD — NVIDIA is a lead contributor to the OpenUSD Alliance (with Pixar, Apple, Adobe, Autodesk)
  - Omniverse Kit: SDK for building custom Omniverse applications and extensions
  - Omniverse Nucleus: collaboration engine for shared USD scenes
  - Omniverse Connectors: plugins linking 3D tools (Autodesk Maya/3ds Max, Blender, Siemens NX, Unreal Engine, etc.) into a shared USD pipeline
- **Omniverse Cloud**:
  - Cloud-native version running on NVIDIA GPU infrastructure
  - Available through major cloud partners (Azure, GCP)
  - Enables streaming digital twin experiences without local GPU clusters
  - APIs for integrating simulation into enterprise workflows
- **Physics and Rendering**:
  - PhysX 5 for rigid body, soft body, fluid, and particle simulation
  - RTX ray tracing and path tracing for physically accurate rendering
  - Flow for fire, smoke, and combustion simulation
  - Omniverse Audio2Face for facial animation from audio
- **Key Industry Deployments**:
  - **BMW**: Digital twin of entire factory production lines; simulates layout changes, robot paths, and logistics before physical deployment. Reported 30% reduction in planning time.
  - **Siemens**: Integration with Siemens Xcelerator platform; Siemens NX connector for industrial digital twins
  - **Lowe's**: Store layout optimization using digital twins
  - **Amazon**: Warehouse robotics simulation
  - **Heavy.AI / WPP**: Creative production pipelines
  - **Foxconn**: Factory digital twins for electronics manufacturing
- **Simulation Integrations**:
  - Isaac Sim: robot simulation built on Omniverse
  - DRIVE Sim: autonomous vehicle simulation built on Omniverse
  - Earth-2: climate digital twin built on Omniverse
  - Modulus: physics-ML framework for building neural network surrogates of physical systems

## Strategic Significance
Omniverse is central to Jensen's "three computers" thesis and to his physical AI vision:

1. **The "three computers" framework.** Jensen says every major enterprise and every robotics company will need three computers: one for training AI (DGX), one for simulation and digital twins (Omniverse), and one for deployment (in the robot, the vehicle, the edge device). Omniverse is the second computer. This framing triples the addressable market beyond training infrastructure alone.

2. **Digital twins create a data flywheel.** Simulate a factory layout in Omniverse, deploy the optimized layout, collect real-world data, feed it back into the simulation to improve accuracy. Each cycle makes the twin more valuable and the enterprise more dependent on the platform.

3. **OpenUSD as the universal interchange.** By championing OpenUSD, NVIDIA positions Omniverse as the hub of a "3D internet" — the interchange format that connects all 3D tools. If USD becomes the standard (and NVIDIA is investing heavily to make it so), then Omniverse becomes the operating system for 3D collaboration across industries.

4. **Omniverse enables physical AI.** You cannot train a robot or autonomous vehicle in the real world alone — it is too slow, too dangerous, too expensive. Omniverse provides the synthetic environments (via Isaac Sim and DRIVE Sim) needed to train physical AI at scale. This makes Omniverse a prerequisite for the entire physical AI market.

5. **Enterprise software revenue and stickiness.** Omniverse Enterprise is a subscription product. Once a factory runs on digital twins, switching costs are enormous — every connector, every custom extension, every trained operator represents investment in the NVIDIA stack.

## How It Connects
- [Isaac & Cosmos](isaac-cosmos.md) — Isaac Sim runs on Omniverse for robot simulation
- [DRIVE Platform](../products/drive-platform.md) — DRIVE Sim runs on Omniverse for AV simulation
- [Physical AI](../concepts/physical-ai.md) — Omniverse provides the simulation environment for physical AI
- [AI Factories](../concepts/ai-factories.md) — Omniverse is the "second computer" in the AI factory vision
- [Domain-Specific Software](domain-specific.md) — Earth-2 climate simulation built on Omniverse

## Jensen's Framing
The "three computers" framework is one of Jensen's most repeated conceptual structures, first crystallized at GTC 2024-2025:

> "Every robotics company, every autonomous vehicle company, every company that operates in the physical world is going to need three computers. A computer to train AI — that's NVIDIA DGX. A computer to simulate — that's NVIDIA Omniverse. And a computer to deploy — that's NVIDIA Jetson, DRIVE, or IGX."
> -- Jensen Huang, GTC 2025 keynote (paraphrased)

Jensen also frames Omniverse through the lens of cost avoidance: "It costs nothing to crash a car in simulation. It costs nothing to redesign a factory in a digital twin. But it costs everything to get it wrong in the real world." He positions digital twins not as visualization toys but as essential operational infrastructure.

On OpenUSD, Jensen has drawn a direct parallel to HTML: "USD will be for 3D worlds what HTML was for 2D documents — the universal format that connects everything. And Omniverse is the browser."
