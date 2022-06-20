
TESTHOST?=test.sub.$(TESTDOMAIN)


.PHONY: lint test livetest typecheck


lint:
	./scripts/lint.sh

test:
	pytest 

livetest:
	./scripts/test.sh $(TESTHOST)

typecheck:
	mypy .
