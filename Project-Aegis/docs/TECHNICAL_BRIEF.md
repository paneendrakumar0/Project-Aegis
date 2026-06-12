# Project Aegis Technical Brief

## Problem Framing

Project Aegis addresses decentralized protective swarm coordination for a
simulated counter-swarm scenario. The objective is to protect ground assets
against hostile drones while minimizing dependence on centralized control or
continuous communication.

## Core Claim

A transparent decentralized baseline can protect assets in simulation by having
each friendly drone independently evaluate hostile threats, select an intercept
target, and steer toward a predicted intercept point while locally avoiding
friendly clustering.

## System Architecture

```text
Scenario Generator
        |
        v
Local Drone Policy ---> Threat Score ---> Target Decision ---> Steering Vector
        |                                                       |
        v                                                       v
Simulation Engine <----------- Engagement / Asset Impact Resolution
        |
        v
Metrics + CSV Reports + Telemetry + ROS/Isaac/Unreal Visualization
```

## Baseline Policy

Each friendly drone runs the same decision loop:

1. Sense hostile drones inside local sensor range.
2. Score each visible hostile using capability, distance to protected asset,
   time-to-threat, and intercept cost.
3. Increase priority for ground-attack hostiles inside the defined threatening
   range.
4. Discount hostiles where another friendly is clearly better positioned.
5. Steer toward a predicted intercept point with local separation behaviour.

This policy is intentionally interpretable. It gives reviewers a baseline that
can be inspected, tested, and compared against future advanced methods.

## Evidence Path

Run:

```bash
make test
make report
```

The report command writes `reports/baseline-100.csv` with per-run metrics:

- Asset survival.
- Hostile neutralization.
- Friendly availability.
- Attendance rate for urgent ground-attack threats.
- Completion time.

## Demonstration Path

Generate deterministic telemetry:

```bash
python3 -m aegis.cli --runs 1 --seed 42 --trace-jsonl reports/trace-42.jsonl
```

Open `web/index.html` only as a lightweight local viewer. The target product
demonstration path is ROS 2 bag playback plus Isaac Sim or Unreal Engine
rendering:

- ROS 2 bag recording from Aegis telemetry.
- Isaac Sim robotics-grade playback with sensor overlays.
- Unreal Engine cinematic mission video generated from the same telemetry.

## Current Limitations

- The baseline is a 2D kinematic simulation exported as 3D telemetry with a
  fixed altitude placeholder.
- Sensor classification is assumed perfect.
- Friendly losses are not yet modelled.
- Communication is not modelled beyond the communication-denied baseline.
- Adversary behaviour is direct asset-seeking with stochastic spawn geometry.

## Next Upgrades

- Add degraded perception and classification uncertainty.
- Add friendly loss and hostile air-to-air engagement modelling.
- Add multi-asset protection.
- Add communication-available and communication-denied comparison modes.
- Add benchmark policies for evaluator comparison.
- Add a formal evaluation notebook or generated PDF report.
- Add ROS 2 bridge packages and high-fidelity rendering integration.
