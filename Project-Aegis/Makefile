.PHONY: test smoke report trace scenario-trace media gazebo-scene

test:
	python3 -m pytest

smoke:
	python3 -m aegis.cli --runs 10 --seed 100

report:
	mkdir -p reports
	python3 -m aegis.cli --runs 100 --seed 42 --csv reports/baseline-100.csv

trace:
	mkdir -p reports
	python3 -m aegis.cli --runs 1 --seed 42 --trace-jsonl reports/trace-42.jsonl

scenario-trace:
	mkdir -p reports
	python3 -m aegis.cli --runs 1 --seed 42 --scenario-config scenarios/baseline_asset_defense.json --trace-jsonl reports/baseline-scenario-trace.jsonl

media: scenario-trace
	python3 tools/render_trace_media.py --trace reports/baseline-scenario-trace.jsonl --out-dir assets/media

gazebo-scene: scenario-trace
	python3 tools/export_gazebo_scene.py --trace reports/baseline-scenario-trace.jsonl
