clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

run:
	./bixi_pc

check: unittest

unittest:
	python -m unittest >> test-results.txt

.PHONY: run check unittest clean
