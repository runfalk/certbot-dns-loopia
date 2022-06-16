#!/usr/bin/env bash

set -e
set -x

pylint certbot_dns_loopia/ tests/
