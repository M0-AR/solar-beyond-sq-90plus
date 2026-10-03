.PHONY: setup bench live lab test exps clean

setup:
	pip install -r requirements.txt

bench:
	python -m src.benchmarks

live:
	python -m src.validate_live

test:
	pytest -q

exps:
	for f in experiments/*.py; do echo "== $$f"; python "$$f" || exit 1; done

lab:
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

clean:
	rm -rf results/* figures/* __pycache__ .pytest_cache
