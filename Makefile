COVERAGE_COMMAND=

test:
	$(COVERAGE_COMMAND) pytest tests/tests/tests.py

coverage:
	+make test COVERAGE_COMMAND='coverage run -m'
