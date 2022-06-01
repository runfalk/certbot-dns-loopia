"""
Contains the Loopia DNS ACME authenticator class.
"""
import logging

from tldextract import TLDExtract
from certbot.plugins.dns_common import DNSAuthenticator
from loopialib import DnsRecord, Loopia

logger = logging.getLogger(__name__)


class LoopiaAuthenticator(DNSAuthenticator):
    """
    Loopia DNS ACME authenticator.

    This Authenticator uses the Loopia API to fulfill a dns-01 challenge.
    """

    #: Short description of plugin
    description = __doc__.strip().split("\n", 1)[0]

    #: TTL for the validation TXT record
    ttl = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = None
        self.credentials = None

        # Use empty tuple for param to prevent tldextract from performing live
        # HTTP request to update the TLD list
        self._tld_extract = TLDExtract(suffix_list_urls=())

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=15*60):
        super(LoopiaAuthenticator, cls).add_parser_arguments(
            add, default_propagation_seconds)
        add("credentials", help="Loopia API credentials INI file.")

    def more_info(self):
        """
        More in-depth description of the plugin.
        """

        return "\n".join(line[4:] for line in __doc__.strip().split("\n"))

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Loopia credentials INI file",
            {
                "user": "API username for Loopia account",
                "password": "API password for Loopia account",
            },
        )

    def _get_loopia_client(self):
        return Loopia(
            self.credentials.conf("user"),
            self.credentials.conf("password"))

    def _perform(self, domain, validation_name, validation):
        loopia = self._get_loopia_client()
        domain_parts = self._tld_extract(validation_name)

        dns_record = DnsRecord("TXT", ttl=self.ttl, data=validation)

        msg = "Creating TXT record for %s on subdomain %s"
        logger.debug(msg, domain_parts.registered_domain, domain_parts.subdomain)

        loopia.add_zone_record(
            record=dns_record,
            domain=domain_parts.registered_domain,
            subdomain=domain_parts.subdomain or None,
        )

    def _cleanup(self, domain, validation_name, validation):
        loopia = self._get_loopia_client()
        domain_parts = self._tld_extract(validation_name)
        dns_record = DnsRecord("TXT", ttl=self.ttl, data=validation)

        records = loopia.get_zone_records(
            domain=domain_parts.registered_domain,
            subdomain=domain_parts.subdomain or None,
        )

        delete_subdomain = True
        for record in records:
            # Make sure the record we delete actually matches the created
            if dns_record.replace(id=record.id) == record:
                logger.debug("Removing zone record %s", record)
                loopia.remove_zone_record(
                    id=record.id,
                    domain=domain_parts.registered_domain,
                    subdomain=domain_parts.subdomain or None,
                )
            else:
                # This happens if there are other zone records on the current
                # sub domain.
                delete_subdomain = False

                msg = "Record {} prevents the subdomain from being deleted"
                logger.debug(msg, record)

        # Delete subdomain if we emptied it completely
        if delete_subdomain:
            msg = "Removing subdomain %s on subdomain %s"
            logger.debug(msg, domain_parts[1], domain_parts[0])
            loopia.remove_subdomain(
                domain=domain_parts.registered_domain,
                subdomain=domain_parts.subdomain,
            )
