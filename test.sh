#!/bin/bash
mkdir -p tmp/etc/
mkdir -p tmp/log/
mkdir -p tmp/run/

chmod 600 credentials.ini

certbot certonly \
    --text \
    --config-dir tmp/etc/ \
    --logs-dir tmp/log/ \
    --work-dir tmp/run/ \
    --test-cert \
    --dry-run \
    --authenticator dns-loopia \
    --dns-loopia-credentials credentials.ini \
    --dns-loopia-propagation-seconds 60 \
    -d $1
