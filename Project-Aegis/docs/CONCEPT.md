# System Concept

## Mission

Project Aegis models a friendly autonomous drone swarm assigned to protect one
or more ground assets from hostile drones. Each friendly drone acts from local
state only: visible hostiles, visible friendlies, visible assets, and its own
remaining capability. Communication can improve performance later, but the core
policy must work without it.

## Safety Scope

This project is a bounded simulation and evaluation environment. It focuses on:

- Swarm coordination research.
- Defensive asset-protection modelling.
- Scenario generation and statistical evaluation.
- Operator-facing visualization.

It deliberately excludes deployable weapon-control integrations, real-world
targeting pipelines, sensor-fusion implementation for live platforms, and
instructions for physical neutralization.

## Algorithmic Approach

The baseline policy combines three ideas:

1. Threat scoring: hostile drones are ranked by their capability, distance to
   protected assets, time-to-threat, and whether they are unattended.
2. Local deconfliction: each friendly drone discounts targets that nearby
   friendlies are already better positioned to intercept.
3. Intercept steering: the selected drone moves toward a predicted intercept
   point while maintaining separation from friendly drones and assets.

This gives evaluators a transparent baseline before adding more advanced
methods such as auction-style task allocation, receding-horizon control, or
reinforcement learning.

## Evaluation Metrics

- Asset survival rate.
- Hostile neutralization rate.
- Ground-attack hostile attendance rate inside threatening range.
- Average time-to-intercept.
- Friendly loss rate.
- Scenario completion time.

## Demonstration Modes

- Headless stochastic runs for statistical evidence.
- Deterministic seeded runs for reproducible debugging.
- Browser visualization for live explanation of swarm behavior.
