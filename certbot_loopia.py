import logging
import itertools
import re
import zope.interface

from certbot.plugins.dns_common import base_domain_name_guesses, DNSAuthenticator
from certbot.interfaces import IAuthenticator, IPluginFactory
from datetime import datetime, timedelta
from loopialib import DnsRecord, Loopia, split_domain
from time import sleep


logger = logging.getLogger(__name__)


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class LoopiaAuthenticator(DNSAuthenticator):
    """
    Loopia DNS ACME authenticator.

    Super!
    """

    #: Short description of plugin
    description = __doc__.strip().split("\n", 1)[0]

    #: TTL for the validation TXT record
    ttl = 30

    def __init__(self, *args, **kwargs):
        super(LoopiaAuthenticator, self).__init__(*args, **kwargs)
        self._client = None
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=15 * 60):
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
        domain_parts = split_domain(validation_name)

        dns_record = DnsRecord("TXT", ttl=self.ttl, data=validation)

        logger.debug(
            "Creating TXT record for {} on subdomain {}".format(*domain_parts))
        loopia.add_zone_record(dns_record, *domain_parts)

    def _cleanup(self, domain, validation_name, validation):
        loopia = self._get_loopia_client()
        domain_parts = split_domain(validation_name)
        dns_record = DnsRecord("TXT", ttl=self.ttl, data=validation)

        records = loopia.get_zone_records(*domain_parts)
        delete_subdomain = True
        for record in records:
            # Make sure the record we delete actually matches the one we created
            if dns_record.replace(id=record.id) == record:
                logger.debug("Removing zone record {}".format(record))
                loopia.remove_zone_record(record.id, *domain_parts)
            else:
                # This happens if there are other zone records on the current
                # sub domain.
                delete_subdomain = False

                msg = "Record {} prevents the subdomain from being deleted"
                logger.debug(msg.format(record))

        # Delete subdomain if we emptied it completely
        if delete_subdomain:
            msg = "Removing subdomain {1} on subdomain {0}"
            logger.debug(msg.format(*domain_parts))
            loopia.remove_subdomain(*domain_parts)
