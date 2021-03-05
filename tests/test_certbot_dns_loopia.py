import pytest
from certbot_dns_loopia import LoopiaAuthenticator, DnsRecord, DEFAULT_TTL, split_domain
from unittest.mock import MagicMock

# This config just sets all parameters to some value. It's just to make sure
# that the DNSAuthenticator constructor has all the parameters it might need
class PluginConfig:
    verb = "certonly"
    config_dir = "/tmp/cfg"
    work_dir = "/tmp/work"
    logs_dir = "tmp/log"
    cert_path = "./cert.pem"
    fullchain_path = "./chain.pem"
    chain_path = "./chain.pem"
    server = "https://acme-v02.api.letsencrypt.org/directory"


class LoopiaTestAuthenticator(LoopiaAuthenticator):
    def __init__(self, client):
        super().__init__(config=PluginConfig, name="dns-loopia")
        self._test_client = client
    def _get_loopia_client(self):
        return self._test_client


class test_perform_cleanup_cycle():
    domain = "*.runfalk.se"  # Unused
    validation_domain = "_acme-challenge.runfalk.se"
    validation_key = "thisgoesinthetetxtrecord"
    domain_parts = split_domain(validation_domain)

    dns_record = DnsRecord("TXT", ttl=DEFAULT_TTL, data=validation_key)

    loopia_mock = MagicMock()

    auth = LoopiaTestAuthenticator(loopia_mock)

    auth._perform(domain, validation_domain, validation_key)

    loopia_mock.add_zone_record.assert_called_with(
        dns_record,
        domain_parts[0],
        domain_parts[1]
    )
    record_id = 20200305
    loopia_mock.get_zone_records.return_value = [
        DnsRecord("TXT", id=record_id, ttl=auth.ttl, data=validation_key),
    ]
    auth._cleanup(domain, validation_domain, validation_key)

    loopia_mock.remove_zone_record.assert_called_with(
        record_id,
        domain_parts[0],
        domain_parts[1],
    )
    # loopia_mock.remove_subdomain.assert_called_with(
    #     domain_parts[0],
    #     domain_parts[1],
    # )
