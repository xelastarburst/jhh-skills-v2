---
title: Robotics & Physical AI
last_updated: 2026-04-09
freshness: quarterly
category: markets
---

# Robotics & Physical AI

## What It Is

Physical AI is Jensen's term for artificial intelligence that operates in the physical world — AI with a body. At the whiteboard, he draws the progression: first we had perception AI (image recognition, speech), then generative AI (language models, image generation), and now Physical AI (robots, autonomous vehicles, industrial automation). The key insight is that Physical AI requires something the first two waves did not: understanding of physics — friction, inertia, gravity, cause and effect. This is why simulation (Omniverse), world models (Cosmos), and embodied compute (Jetson) become critical. NVIDIA's bet is that the robotics market will follow the same curve as AI in software — starting at zero and scaling exponentially — and that NVIDIA will own the full stack from training to simulation to deployment.

## Key Facts

- **Humanoid robot companies using NVIDIA technology:**
  - **Figure AI:** Using NVIDIA GPUs and Isaac for Figure 01/02 humanoid robots; raised over $1B in funding
  - **1X Technologies (formerly Halodi):** NEO humanoid robot, NVIDIA-powered perception and planning
  - **Agility Robotics:** Digit humanoid robot deployed in Amazon warehouses, NVIDIA Jetson-powered
  - **Apptronik:** Apollo humanoid robot, partnering with NVIDIA on GR00T
  - **Tesla Optimus:** Tesla's humanoid robot program (uses custom compute but competes in the same market)
  - **Unitree:** Chinese robotics company, H1/G1 humanoid robots, uses NVIDIA Jetson
  - **Fourier Intelligence, UBTECH, Sanctuary AI:** Additional humanoid robot developers in NVIDIA's ecosystem
- **NVIDIA robotics product stack:**
  - **Jetson Orin / Jetson Thor:** Edge AI compute modules for robots (Jetson Thor is the next-gen, Blackwell-derived platform for humanoid robots, announced GTC 2024)
  - **Isaac Sim:** Omniverse-based robotics simulation platform for training robot AI in photorealistic, physics-accurate virtual environments
  - **Isaac ROS:** GPU-accelerated ROS (Robot Operating System) packages for perception, navigation, and manipulation
  - **Cosmos:** World foundation models that generate synthetic physical-world data for training robot AI — "learns the physics of the world"
  - **GR00T (Generalist Robot 00 Technology):** Foundation model for humanoid robots, announced GTC 2024; trains robots to understand natural language instructions and learn physical skills via imitation
  - **Isaac Lab:** Reinforcement learning framework for robot training in simulation
- **Market sizing:**
  - Global robotics market (industrial + service + humanoid): estimated at $60-80B in 2025, projected to grow to $200-300B+ by 2030 (varies by analyst)
  - Humanoid robot market specifically: effectively a zero-billion-dollar market in 2024, with Goldman Sachs projecting $38B by 2035 and some bullish estimates reaching $150B+
  - Physical AI compute (the NVIDIA-addressable portion): Jensen has framed this as a future market comparable in scale to data center AI, but it is in the earliest stages
- **Investment trends:** Robotics and Physical AI venture funding surged in 2024-2025. Figure AI raised $675M at a $2.6B valuation (early 2024), then reportedly raised additional funding in 2025. 1X raised $100M+ Series B. Amazon deployed 750,000+ robots across its logistics network (primarily non-humanoid). Total VC investment in robotics exceeded $10B in 2024.
- **Industrial robotics:** Beyond humanoids, NVIDIA Isaac and Jetson serve the massive existing industrial robotics market — warehouse automation (Amazon, Ocado), manufacturing (Foxconn, BMW, Siemens), inspection, and logistics. This is current revenue, not future speculation.

## Strategic Significance

Robotics and Physical AI is Jensen's biggest "zero-billion-dollar market" bet since CUDA. The reasoning chain is explicit:

**1. The full-stack play is the bet.** Jensen's reasoning: AI that operates in the physical world needs (a) training compute (data center GPUs), (b) simulation (Omniverse + Isaac Sim), (c) world models (Cosmos), (d) a foundation model (GR00T), and (e) edge compute for deployment (Jetson). NVIDIA is the only company building all five layers. This is stack thinking at its most ambitious — own every layer of the Physical AI stack the way NVIDIA owns every layer of the AI training stack.

**2. Zero-billion-dollar market with inevitable emergence.** The conditions for Physical AI are converging: (a) foundation models can now understand language and images (perception solved), (b) simulation environments are photorealistic and physics-accurate (Omniverse), (c) world models can generate synthetic physical-world training data (Cosmos), (d) edge compute is powerful enough for real-time inference (Jetson Thor). Each condition was missing even 2-3 years ago. Jensen's test: are the conditions emerging or receding? They are clearly emerging.

**3. Simulation-to-reality pipeline is the moat.** The critical bottleneck in robotics is training data — you cannot crash a humanoid robot 10 million times in the real world to teach it to walk. Simulation solves this. NVIDIA's Omniverse + Isaac Sim + Cosmos pipeline lets robot developers train in simulation, generate synthetic data, and transfer learned behaviors to physical robots. This pipeline is the moat — competitors selling only chips cannot replicate it.

**4. The CUDA flywheel replays.** Jensen is running the same play as CUDA on GeForce: give away Isaac, Cosmos, and GR00T to every robotics developer. Build the install base. Make NVIDIA the default platform for Physical AI development. When the market scales (and Jensen believes it will scale to trillions), NVIDIA captures value at every layer. The short-term revenue is small; the long-term platform lock-in is decisive.

**5. Three markets collapse into one.** At GTC 2026, Jensen articulated that inference economy + agentic AI + Physical AI are converging into a single workload class. Digital agents become physical agents (robots). The same compute, the same software stack, the same NVIDIA platform serves all three. This convergence thesis is Jensen's most ambitious strategic claim.

## How It Connects

- [Robotics Platforms](../products/robotics-platforms.md) — Jetson Orin, Jetson Thor, IGX hardware
- [Isaac & Cosmos](../software/isaac-cosmos.md) — Isaac Sim, Isaac ROS, Cosmos world models, GR00T
- [Physical AI](../concepts/physical-ai.md) — The conceptual framework for AI with a body
- [Omniverse](../software/omniverse.md) — Simulation engine underlying Isaac Sim
- [Automotive & AV](automotive-av.md) — AV is the first and most mature Physical AI market
- [AI Factories](../concepts/ai-factories.md) — Physical AI training requires AI factories

## Jensen's Framing

At **GTC Paris** (2024), Jensen made the declaration that launched NVIDIA's Physical AI push:

> "The next big thing is Physical AI, AI with a body."
> (Source: RS Online/DesignSpark coverage of GTC Paris)

At **GTC 2025**, Jensen defined Physical AI in technical terms:

> "Physical AI understands friction, inertia, cause and effect. It doesn't just recognize images or generate text — it reasons about the physical world. This requires a new kind of AI training: simulation in physically accurate worlds."

At **GTC 2026**, Jensen connected Physical AI to the broader AI factory narrative:

> "We have digital agents. Now we have physically embodied agents. We call them robots."
> (Source: Data Center Frontier coverage of GTC 2026)

Jensen has framed the Physical AI Data Factory Blueprint (announced GTC 2026) as the operational playbook for robotics companies: collect real-world data, build digital twins in Omniverse, generate synthetic data with Cosmos, train robot foundation models, validate in simulation, deploy to physical robots. This is the same "three computers" framework from automotive, generalized to all of robotics.

On the market timing, Jensen has been explicit that this is a long-term bet: "Physical AI is where data center AI was ten years ago. The conditions are emerging. The market is zero today. But the reasoning chain says it must become enormous — because every physical task in the world is a candidate for automation, and automation requires intelligence."
