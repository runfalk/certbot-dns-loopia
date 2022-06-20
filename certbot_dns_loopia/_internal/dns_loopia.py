"""
Contains the Loopia DNS ACME authenticator class.
"""
import logging
import xmlrpc.client
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, Tuple, get_type_hints, Any, TypeVar, cast, Mapping, List
from xmlrpc.client import ServerProxy

from certbot.configuration import NamespaceConfig
from certbot.errors import PluginError
from certbot.plugins.dns_common import DNSAuthenticator, CredentialsConfiguration
from tldextract import TLDExtract

logger = logging.getLogger(__name__)


@dataclass(frozen=True, eq=False)
class DnsRecord:
    """
    Matches the "record_obj" as defined in the Loopia API spec.
    See https://www.loopia.se/api/record_obj/

    The names of the properties exactly match the API spec, to
    enable seamless usage with the API.
    """
    type: str
    ttl: int = 3600
    priority: int = 0
    rdata: str = ""
    record_id: int = 0

    def __post_init__(self) -> None:
        type_hints = get_type_hints(self)

        for name, type_hint in type_hints.items():
            value = getattr(self, name)

            if not isinstance(value, type_hint):
                raise ValueError(
                    f"Expected attribute '{name}' to be of type "
                    f"{type_hint}, but value was {value}"
                )

    def __eq__(self, other: object) -> bool:
        """
        Special equals operator implementation that does not compare record ID.
        """
        if not isinstance(other, DnsRecord):
            return False

        return (
                self.type == other.type and
                self.ttl == other.ttl and
                self.priority == other.priority and
                self.rdata == other.rdata
        )


FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])


def reraise_xmlprc_fault(function_to_wrap: FunctionT) -> FunctionT:
    """
    Simple decorator function that wraps the supplied function in
    a try-except that handles xmlrpc client faults.
    """

    @wraps(function_to_wrap)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        try:
            return function_to_wrap(*args, **kwargs)
        except xmlrpc.client.Fault as error:
            error_msg = f"Loopia responded with: '{error.faultString}'"
            raise PluginError(error_msg) from error

    return cast(FunctionT, decorated)


class LoopiaClient:
    """Loopia XML-RPC API client used to get/add/remove DNS zone records."""
    url = "https://api.loopia.se/RPCSERV"
    encoding = "utf-8"

    def __init__(self, user: str, password: str) -> None:
        self.__user = user
        self.__password = password
        self.__api = ServerProxy(uri=LoopiaClient.url, encoding=LoopiaClient.encoding)

    @property
    def __credentials(self) -> Tuple[str, str]:
        return self.__user, self.__password

    @reraise_xmlprc_fault
    def get_zone_records(
            self,
            domain: str,
            subdomain: Optional[str] = "@",
    ) -> Tuple[DnsRecord, ...]:
        """Returns all zone records for the provided domain/subdomain."""
        records = self.__api.getZoneRecords(*self.__credentials, domain, subdomain)
        records = cast(List[Mapping[Any, Any]], records)

        return tuple(
            DnsRecord(**record)
            for record
            in records
        )

    @reraise_xmlprc_fault
    def add_zone_record(
            self,
            dns_record: DnsRecord,
            domain: str,
            subdomain: Optional[str] = "@",
    ) -> None:
        """Adds a new zone record to the provided domain/subdomain."""
        if dns_record.record_id != 0:
            raise ValueError("Record must not have an ID")

        self.__api.addZoneRecord(
            *self.__credentials,
            domain,
            subdomain,
            dns_record.__dict__,
        )

    @reraise_xmlprc_fault
    def remove_zone_record(
            self,
            record_id: int,
            domain: str,
            subdomain: Optional[str] = "@",
    ) -> None:
        """Removes zone record by provided ID for provided domain/subdomain."""
        self.__api.removeZoneRecord(
            *self.__credentials,
            domain,
            subdomain,
            record_id,
        )

    @reraise_xmlprc_fault
    def remove_subdomain(self, domain: str, subdomain: Optional[str] = "@") -> None:
        """Removes the provided subdomain for the provided domain."""
        self.__api.removeSubdomain(
            *self.__credentials,
            domain,
            subdomain,
        )


class Authenticator(DNSAuthenticator):
    """
    Loopia DNS ACME authenticator.

    This Authenticator uses the Loopia API to fulfill a dns-01 challenge.
    """

    #: Short description of plugin
    description = __doc__.strip().split("\n", 1)[0]

    #: TTL for the validation TXT record
    ttl = 30

    txt_record_type = "TXT"

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
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds)
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

    def _get_loopia_client(self) -> LoopiaClient:
        assert self.credentials, "Credentials not set"

        return LoopiaClient(
            user=self.credentials.conf("user"),
            password=self.credentials.conf("password"),
        )

    def _perform(
            self,
            domain: str,
            validation_name: str,
            validation: str,
    ) -> None:
        loopia_client = self._get_loopia_client()
        domain_parts = self._tld_extract(validation_name)

        dns_record = DnsRecord(self.txt_record_type, ttl=self.ttl, rdata=validation)

        msg = "Creating TXT record for %s on subdomain %s"
        logger.debug(msg, domain_parts.registered_domain, domain_parts.subdomain)

        loopia_client.add_zone_record(
            dns_record=dns_record,
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
        target_dns_record = DnsRecord(self.txt_record_type, ttl=self.ttl, rdata=validation)

        records = loopia.get_zone_records(
            domain=domain_parts.registered_domain,
            subdomain=domain_parts.subdomain or None,
        )

        remove_subdomain = True
        for current_record in records:
            # Make sure the record we delete actually matches the created
            if current_record == target_dns_record:
                logger.debug("Removing zone record %s", current_record)
                loopia.remove_zone_record(
                    record_id=current_record.record_id,
                    domain=domain_parts.registered_domain,
                    subdomain=domain_parts.subdomain or None,
                )
            else:
                # This happens if there are other zone records on the current
                # subdomain.
                remove_subdomain = False

                msg = "Record %s prevents the subdomain from being deleted"
                logger.debug(msg, current_record)

        # Delete subdomain if we emptied it completely
        if remove_subdomain:
            msg = "Removing subdomain %s on domain %s"
            logger.debug(msg, domain_parts.subdomain, domain_parts.registered_domain)
            loopia.remove_subdomain(
                domain=domain_parts.registered_domain,
                subdomain=domain_parts.subdomain,
            )
