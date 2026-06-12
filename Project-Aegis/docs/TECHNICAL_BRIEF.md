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
Metrics + CSV Reports + Browser Visualization
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

Open `web/index.html` to show:

- Protected asset and defense region.
- Friendly interceptors.
- Ground-attack and air-threat hostiles.
- Threat rings for ground-attack hostiles.
- Live assignment lines and attendance metrics.

## Current Limitations

- The baseline is a 2D kinematic simulation.
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
