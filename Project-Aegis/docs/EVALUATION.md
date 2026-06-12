# Evaluation Protocol

## Purpose

The simulator should support evidence-backed claims about decentralized swarm
coordination. A demonstration run is useful for explanation, but the primary
evidence should come from repeated stochastic runs.

## Baseline Command

```bash
python3 -m aegis.cli --runs 100 --seed 42 --csv reports/baseline-100.csv
```

## Metrics To Report

- Success rate: all protected assets survive and all hostiles are neutralized.
- Asset survival rate: fraction of protected assets still alive at run end.
- Hostile neutralization rate: fraction of hostile drones neutralized.
- Attendance rate: fraction of ground-attack threats inside threatening range
  that are covered by an interceptor or reachable intercept path.
- Scenario duration: elapsed simulation time until terminal condition.

## Review Discipline

For a formal technical review, report at least three batches:

- Balanced: equal or near-equal friendly and hostile counts.
- Saturation: hostiles outnumber friendlies.
- Degraded perception: reduced friendly sensor range.

Each batch should use a fixed seed range and store CSV output so results are
reproducible.
