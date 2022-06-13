"""
Contains the Loopia DNS ACME authenticator class.
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Tuple, get_type_hints
from xmlrpc.client import ServerProxy

from tldextract import TLDExtract
from certbot.plugins.dns_common import DNSAuthenticator, CredentialsConfiguration
from certbot.configuration import NamespaceConfig
from loopialib import Loopia

logger = logging.getLogger(__name__)


# class StrEnum(str, Enum):
#     pass


class RecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CERT = "CERT"
    CNAME = "CNAME"
    HINFO = "HINFO"
    HIP = "HIP"
    IPSECKEY = "IPSECKEY"
    LOC = "LOC"
    MX = "MX"
    NAPTR = "NAPTR"
    NS = "NS"
    SRV = "SRV"
    SSHFP = "SSHFP"
    TXT = "TXT"


@dataclass(frozen=True)
class DnsRecord:
    type: RecordType
    ttl: int = 3600
    priority: int = 0
    rdata: str = ""
    record_id: int = 0

    def __post_init__(self):
        type_hints = get_type_hints(self)
        for name, type_hint in type_hints.items():
            value = getattr(self, name)
            if not isinstance(value, type_hint):
                raise ValueError(f"Expected attribute '{name}' to be of type {type_hint}, but value was {value}")


class LoopiaClient:
    """Loopia XML-RPC API client used to get/add/remove DNS zone records."""
    URL = "https://api.loopia.se/RPCSERV"
    ENCODING = "utf-8"

    def __init__(self, user: str, password: str) -> None:
        self.__user = user
        self.__password = password
        self.__xmlrpc_server_proxy = ServerProxy(uri=LoopiaClient.URL, encoding=LoopiaClient.ENCODING)

    @property
    def __credentials(self) -> Tuple[str, str]:
        return self.__user, self.__password

    def get_zone_records(self, domain: str, subdomain: str = "@") -> Tuple[DnsRecord, ...]:
        records = self.__xmlrpc_server_proxy.getZoneRecords(*self.__credentials, domain, subdomain)

        return tuple(
            DnsRecord(**record)
            for record
            in records
        )

    def add_zone_record(self, dns_record: DnsRecord, domain: str, subdomain: str = "@"):
        if dns_record.id != 0:
            raise ValueError("Record must not have an ID")


if __name__ == "__main__":
    c = LoopiaClient("tornstrom@loopiaapi", "whydissohard")
    recors = c.get_zone_records(domain="xn--trnstrm-90af.se")
    print(recors)
    # r = DnsRecord(
    #     type=RecordType.TXT,
    #     data=1
    # )
    # print(r.type.value)


class LoopiaAuthenticator(DNSAuthenticator):
    """
    Loopia DNS ACME authenticator.

    This Authenticator uses the Loopia API to fulfill a dns-01 challenge.
    """

    #: Short description of plugin
    description = __doc__.strip().split("\n", 1)[0]

    #: TTL for the validation TXT record
    ttl = 30

    def __init__(self, config: NamespaceConfig, name: str) -> None:
        super().__init__(config, name)
        self.credentials: Optional[CredentialsConfiguration] = None

        # Use empty tuple for param to prevent tldextract from performing live
        # HTTP request to update the TLD list
        self._tld_extract = TLDExtract(suffix_list_urls=())

    @classmethod
    def add_parser_arguments(
            cls,
            add: Callable[..., None],
            default_propagation_seconds: int = 15 * 60,
    ) -> None:
        super(LoopiaAuthenticator, cls).add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="Loopia API credentials INI file.")

    def more_info(self) -> str:
        """
        More in-depth description of the plugin.
        """

        return "\n".join(line[4:] for line in __doc__.strip().split("\n"))

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Loopia credentials INI file",
            {
                "user": "API username for Loopia account",
                "password": "API password for Loopia account",
            },
        )

    def _get_loopia_client(self) -> Loopia:
        assert self.credentials, "Credentials not set"

        return Loopia(
            self.credentials.conf("user"),
            self.credentials.conf("password"),
        )

    def _perform(
            self,
            domain: str,
            validation_name: str,
            validation: str,
    ) -> None:
        loopia = self._get_loopia_client()
        domain_parts = self._tld_extract(validation_name)

        dns_record = DnsRecord(RecordType.TXT, ttl=self.ttl, data=validation)

        msg = "Creating TXT record for %s on subdomain %s"
        logger.debug(msg, domain_parts.registered_domain, domain_parts.subdomain)

        loopia.add_zone_record(
            record=dns_record,
            domain=domain_parts.registered_domain,
            subdomain=domain_parts.subdomain or None,
        )

    def _cleanup(
            self,
            domain: str,
            validation_name: str,
            validation: str,
    ) -> None:
        loopia = self._get_loopia_client()
        domain_parts = self._tld_extract(validation_name)
        dns_record = DnsRecord(RecordType.TXT, ttl=self.ttl, data=validation)

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
