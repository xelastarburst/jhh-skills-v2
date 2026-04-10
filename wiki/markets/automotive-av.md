---
title: Automotive & AV
last_updated: 2026-04-09
freshness: quarterly
category: markets
---

# Automotive & AV

## What It Is

Automotive is NVIDIA's longest-running platform play outside of gaming — a market where 7-year design cycles create deep lock-in but require patience. At the whiteboard, Jensen frames automotive not as a chip business but as a three-computer problem: one computer to train the AI (data center), one computer to simulate the driving world (Omniverse), and one computer in the car to run inference in real time (DRIVE). NVIDIA provides all three. The market spans the spectrum from Level 2+ ADAS (advanced driver assistance — lane keeping, adaptive cruise, parking) to full Level 4 autonomous driving, with the economics shifting from selling chips to selling software-defined vehicle platforms.

## Key Facts

- **NVIDIA Automotive revenue, FY2025:** $1.55 billion for the full fiscal year, up ~55% year-over-year from $1.09B in FY2024. (Source: NVIDIA FY2025 earnings)
- **Q4 FY2025:** Automotive revenue was $570 million, up 103% YoY — the fastest-growing non-data-center segment.
- **Design win pipeline:** Jensen has cited a $14B+ automotive design win pipeline (total contract value over multi-year engagements). This represents contracted future revenue from OEMs that have selected NVIDIA DRIVE for upcoming vehicle programs.
- **Key OEM partnerships:**
  - **Mercedes-Benz:** DRIVE Orin for next-gen ADAS across lineup; advanced co-development for software-defined vehicle architecture
  - **BYD:** DRIVE Orin and DRIVE Thor for upcoming BYD models; one of the world's largest EV makers
  - **Volvo / Polestar:** DRIVE Orin-based ADAS across Volvo's EX90 and future models
  - **Hyundai / Kia:** NVIDIA DRIVE partnership for next-gen autonomous driving across brands
  - **JLR (Jaguar Land Rover):** DRIVE Orin for upcoming electric vehicles
  - **GM (General Motors):** Expanded partnership announced at GTC 2025 for next-gen AV and simulation
  - **NIO, Li Auto, XPeng:** Chinese EV makers deploying DRIVE Orin at scale
  - **Waymo, Zoox, Aurora:** Robotaxi and AV companies using NVIDIA compute for their autonomous stacks
  - **Toyota, Honda:** Partnerships for ADAS and next-gen vehicle compute
- **Product progression:** DRIVE Orin (current generation, 254 TOPS) is in production vehicles today. DRIVE Thor (next generation, 2000 TOPS, Blackwell-derived architecture) is sampling to partners and expected in vehicles from 2025-2026 model years onward.
- **Software stack:** NVIDIA DRIVE includes a full software-defined vehicle platform — DRIVE OS (safety-certified operating system), DriveWorks (middleware), DRIVE AV (perception, planning), DRIVE IX (in-cabin AI), and DRIVE Sim (Omniverse-based simulation).
- **Simulation advantage:** NVIDIA DRIVE Sim, built on Omniverse, enables OEMs to simulate billions of miles of driving scenarios using synthetic data. This is a critical competitive moat — simulation replaces expensive real-world testing.
- **Halos safety system:** Announced at GTC 2025, Halos is an end-to-end safety architecture for autonomous vehicles, integrating NVIDIA hardware, software, and sensor fusion.
- **Regulatory landscape:** L2+ ADAS is widely deployed globally. L3 conditional automation is approved in limited markets (Germany, Nevada, others). L4 robotaxi operations are expanding in the US (San Francisco, Phoenix, Austin) and China. Regulatory progress is accelerating but remains geography-specific.

## Strategic Significance

Automotive embodies Jensen's favorite strategic pattern: platform economics with long-term compounding.

**1. Seven-year design cycles create deep lock-in.** An OEM that selects NVIDIA DRIVE for a new vehicle platform commits engineering resources, software development, validation testing, and safety certification — all built around NVIDIA's architecture. Switching to a competitor mid-program is extraordinarily expensive. This is why the $14B+ design win pipeline is strategically significant: it represents years of contracted future revenue with high switching costs.

**2. Three-computer model maximizes wallet share.** For every dollar of DRIVE silicon in the car, NVIDIA captures additional revenue from data center GPUs for training, Omniverse licenses for simulation, and AI Enterprise software for fleet management. The automotive customer buys from NVIDIA three times: train, simulate, deploy.

**3. Software-defined vehicles shift the revenue model.** Traditional automotive chips are one-time ASP. Software-defined vehicles enable over-the-air updates, feature unlocks, and subscription services — all running on NVIDIA compute. Jensen's framing: the car becomes a software platform, and NVIDIA captures recurring revenue as the platform beneath the platform.

**4. Physical AI proving ground.** Autonomous driving is the highest-stakes application of Physical AI — AI that must understand physics, predict behavior, and act in the real world with safety-critical reliability. Everything NVIDIA learns from AV (simulation, sensor fusion, real-time inference, safety certification) transfers directly to robotics, industrial automation, and humanoid robots. Automotive is the training ground for Physical AI broadly.

**5. Simulation as strategic moat.** DRIVE Sim built on Omniverse creates a unique competitive advantage: NVIDIA is the only company offering the full pipeline from synthetic data generation (Cosmos world models) to physics-accurate simulation (Omniverse) to in-vehicle inference (DRIVE). Competitors selling only chips cannot replicate this end-to-end workflow.

## How It Connects

- [DRIVE Platform](../products/drive-platform.md) — DRIVE Orin, DRIVE Thor, and the full AV software stack
- [Omniverse](../software/omniverse.md) — Powers DRIVE Sim for autonomous vehicle simulation
- [Physical AI](../concepts/physical-ai.md) — Automotive is the most mature application of Physical AI
- [Isaac & Cosmos](../software/isaac-cosmos.md) — Cosmos world models generate synthetic driving data for AV training
- [Robotics & Physical AI](robotics-physical-ai.md) — AV technology transfers directly to robotics

## Jensen's Framing

At **GTC 2025**, Jensen announced the GM partnership and the Halos safety system, framing automotive as Physical AI applied to transportation:

> "The car is the first robot. It perceives the world, it reasons about the world, it plans and acts. Everything we are building for autonomous vehicles — the simulation, the training, the inference — applies directly to every other kind of robot."

At **CES 2026**, Jensen demonstrated Cosmos world models generating synthetic driving scenarios:

> "Cosmos reasons about edge scenarios, breaks them down into familiar physical interactions. We can generate millions of miles of driving data — rare events, corner cases, dangerous situations — without putting a single car on the road. This is how you train an autonomous vehicle. This is how you turn compute into data."
> (Source: CES 2026 keynote transcript via Rev.com)

Jensen has consistently framed the automotive opportunity as a platform story, not a chip story: "We don't sell chips to car companies. We sell them a computer for the car, a computer for the data center, and a computer for the simulation. The platform is the product." This three-computer framing appears repeatedly in GTC keynotes from 2024-2026.

On the design win pipeline, Jensen emphasizes the compounding nature: "Automotive is a long-cycle business. You win today, you ship in five years, you collect revenue for seven years. The pipeline we have built is the foundation for a decade of automotive growth."
