
TESTHOST?=test.sub.$(TESTDOMAIN)


.PHONY: lint test livetest


lint:
	pylint certbot_dns_loopia.py

test:
	pytest 

livetest:
	./test.sh $(TESTHOST)
