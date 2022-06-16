"""
Tests for certbot-dns-loopia
"""
# pylint: disable=protected-access,too-few-public-methods
from unittest.mock import MagicMock

from certbot.configuration import NamespaceConfig
from tldextract import TLDExtract

from certbot_dns_loopia._internal.dns_loopia import Authenticator, LoopiaClient, DnsRecord

mock_namespace = MagicMock()
mock_namespace.config_dir = "/tmp"
mock_namespace.work_dir = "/tmp"
mock_namespace.logs_dir = "/tmp"


# This config just sets all parameters to some value. It's just to make sure
# that the DNSAuthenticator constructor has all the parameters it might need
class PluginConfig(NamespaceConfig):
    """
    PluginConfig with test variables
    """

    def __init__(self) -> None:
        super().__init__(mock_namespace)

    verb = "certonly"
    config_dir = "/tmp/cfg"
    work_dir = "/tmp/work"
    logs_dir = "tmp/log"
    cert_path = "./cert.pem"
    fullchain_path = "./chain.pem"
    chain_path = "./chain.pem"
    server = "https://acme-v02.api.letsencrypt.org/directory"


class TestAuthenticator(Authenticator):
    """
    Testing using mock objects
    """

    def __init__(self, client: LoopiaClient) -> None:
        super().__init__(config=PluginConfig(), name="dns-loopia")
        self._test_client = client

    def _get_loopia_client(self) -> LoopiaClient:
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
        Authenticator.txt_record_type,
        ttl=Authenticator.ttl,
        rdata=validation_key
    )

    loopia_mock = MagicMock()

    auth = TestAuthenticator(loopia_mock)

    auth._perform(domain, validation_domain, validation_key)

    loopia_mock.add_zone_record.assert_called_with(
        dns_record=dns_record,
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
    record_id = 20200305
    loopia_mock.get_zone_records.return_value = [
        DnsRecord(
            Authenticator.txt_record_type,
            record_id=record_id,
            ttl=auth.ttl,
            rdata=validation_key,
        ),
    ]
    auth._cleanup(domain, validation_domain, validation_key)

    loopia_mock.remove_zone_record.assert_called_with(
        record_id=record_id,
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
    loopia_mock.remove_subdomain.assert_called_with(
        domain=domain_parts.registered_domain,
        subdomain=domain_parts.subdomain,
    )
