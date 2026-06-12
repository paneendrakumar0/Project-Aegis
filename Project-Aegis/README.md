# Project Aegis

Project Aegis is a simulation-first research prototype for decentralized
counter-swarm protection of ground assets. It is designed around the BEL
SIH25164 problem statement: friendly autonomous drones protect designated
assets against hostile drone swarms using local perception, threat
prioritization, and communication-independent coordination.

This repository is intentionally scoped to modelling, simulation, evaluation,
and operator visualization. It does not provide hardware integration,
real-world targeting instructions, or deployable weapon-control logic.

## Current Objective

Build a credible, reviewable prototype that can be shown as a software
solution architecture to technical evaluators:

- Decentralized per-drone decision loop.
- Threat scoring based on asset risk, time-to-threat, and hostile capability.
- Communication-denied baseline with optional coordination hooks.
- Stochastic simulation runs across randomized scenarios.
- Metrics for asset protection, friendly losses, engagement coverage, and
  intercept quality.
- GUI for visual inspection and demonstrations.
- Tests and documentation suitable for technical review.

## Repository Layout

```text
aegis/              Core simulation and decision policy package
docs/               Concept notes, architecture, and roadmap
tests/              Unit and scenario tests
web/                Browser-based visual simulation demo
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python3 -m aegis.cli --runs 25 --seed 42
```

Open `web/index.html` in a browser for the lightweight visual demo.

## Engineering Standard

The project is developed in coherent commits, with tests run before push where
practical. The intent is to keep every commit reviewable and every claim backed
by either code, simulation output, or documentation.
