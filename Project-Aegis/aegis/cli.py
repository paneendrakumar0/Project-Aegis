from __future__ import annotations

import argparse
import csv
import sys

from aegis.config import load_scenario_config
from aegis.simulator import run_batch
from aegis.scenario import default_scenario
from aegis.simulator import run_recorded_simulation
from aegis.telemetry import write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Project Aegis stochastic simulation batches.")
    parser.add_argument("--runs", type=int, default=50, help="Number of randomized scenarios to run.")
    parser.add_argument("--seed", type=int, default=0, help="Base random seed.")
    parser.add_argument("--friendlies", type=int, default=8, help="Friendly drone count.")
    parser.add_argument("--hostiles", type=int, default=10, help="Hostile drone count.")
    parser.add_argument("--scenario-config", type=str, default="", help="Optional JSON scenario manifest.")
    parser.add_argument("--csv", type=str, default="", help="Optional path for per-run CSV output.")
    parser.add_argument("--trace-jsonl", type=str, default="", help="Optional JSONL telemetry trace for the first run.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.scenario_config:
        scenario = load_scenario_config(args.scenario_config)
        results = [run_recorded_simulation(scenario, seed=args.seed + index, record=False).result for index in range(args.runs)]
    else:
        results = run_batch(args.runs, seed=args.seed, friendly_count=args.friendlies, hostile_count=args.hostiles)

    success_rate = sum(1 for result in results if result.success) / max(len(results), 1)
    asset_survival = sum(result.assets_survived / result.assets_total for result in results) / max(len(results), 1)
    neutralization = sum(result.hostiles_neutralized / result.hostiles_total for result in results) / max(len(results), 1)
    attendance = sum(result.attendance_rate for result in results) / max(len(results), 1)

    print(f"runs={len(results)}")
    print(f"success_rate={success_rate:.3f}")
    print(f"asset_survival={asset_survival:.3f}")
    print(f"hostile_neutralization={neutralization:.3f}")
    print(f"attendance_rate={attendance:.3f}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(results[0].__dict__.keys()) + ["success"])
            writer.writeheader()
            for result in results:
                row = result.__dict__.copy()
                row["success"] = result.success
                writer.writerow(row)

    if args.trace_jsonl:
        scenario = (
            load_scenario_config(args.scenario_config)
            if args.scenario_config
            else default_scenario(seed=args.seed, friendly_count=args.friendlies, hostile_count=args.hostiles)
        )
        recorded = run_recorded_simulation(
            scenario,
            seed=args.seed,
            record=True,
        )
        write_jsonl(recorded.frames, args.trace_jsonl)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
