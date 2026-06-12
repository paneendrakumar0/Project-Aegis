.PHONY: test smoke report

test:
	python3 -m pytest

smoke:
	python3 -m aegis.cli --runs 10 --seed 100

report:
	mkdir -p reports
	python3 -m aegis.cli --runs 100 --seed 42 --csv reports/baseline-100.csv

