"""
Tests for certbot-dns-loopia
"""
# pylint: disable=protected-access,too-few-public-methods
from argparse import Namespace
from unittest.mock import MagicMock
from tldextract import TLDExtract
from loopialib import DnsRecord, Loopia
from certbot_dns_loopia import LoopiaAuthenticator
from certbot.configuration import NamespaceConfig


# This config just sets all parameters to some value. It's just to make sure
# that the DNSAuthenticator constructor has all the parameters it might need
class PluginConfig(NamespaceConfig):
    """
    PluginConfig with test variables
    """

    def __init__(self) -> None:
        super().__init__(MagicMock())

    verb = "certonly"
    config_dir = "/tmp/cfg"
    work_dir = "/tmp/work"
    logs_dir = "tmp/log"
    cert_path = "./cert.pem"
    fullchain_path = "./chain.pem"
    chain_path = "./chain.pem"
    server = "https://acme-v02.api.letsencrypt.org/directory"


class LoopiaTestAuthenticator(LoopiaAuthenticator):
    """
    Testing using mock objects
    """

    def __init__(self, client: Loopia) -> None:
        super().__init__(config=PluginConfig(), name="dns-loopia")
        self._test_client = client

    def _get_loopia_client(self) -> Loopia:
        return self._test_client


def test_perform_cleanup_cycle() -> None:
    """
    Performs a full cycle including cleanup
    """
    domain = "*.runfalk.se"  # Unused
    validation_domain = "_acme-challenge.runfalk.se"
    validation_key = "thisgoesinthetetxtrecord"

    tld_extract = TLDExtract(suffix_list_urls=())
    domain_parts = tld_extract(validation_domain)

    dns_record = DnsRecord(
        "TXT",
        ttl=LoopiaAuthenticator.ttl,
        data=validation_key
    )

    loopia_mock = MagicMock()

    auth = LoopiaTestAuthenticator(loopia_mock)

    auth._perform(domain, validation_domain, validation_key)

    loopia_mock.add_zone_record.assert_called_with(
        record=dns_record,
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
    record_id = 20200305
    loopia_mock.get_zone_records.return_value = [
        DnsRecord("TXT", id=record_id, ttl=auth.ttl, data=validation_key),
    ]
    auth._cleanup(domain, validation_domain, validation_key)

    loopia_mock.remove_zone_record.assert_called_with(
        id=record_id,
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
    loopia_mock.remove_subdomain.assert_called_with(
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
