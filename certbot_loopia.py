import logging
import itertools
import re
import zope.interface

from acme.challenges import DNS01
from acme.dns_resolver import DNS_AVAILABLE
from acme.errors import DependencyError
from acme.jose.b64 import b64encode
from certbot.plugins.common import Plugin
from certbot.interfaces import IAuthenticator, IPluginFactory
from datetime import datetime, timedelta
from loopialib import DnsRecord, Loopia
from time import sleep

logger = logging.getLogger(__name__)


def parse_time(time):
    pattern = r"^(?:(?P<d>\d+)d)?(?:(?P<h>\d+)h)?(?:(?P<m>\d+)m)?(?:(?P<s>\d+)s?)?$"
    multipliers = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1,
    }

    match = re.match(pattern, time)
    if match is None:
        raise ValueError("Invalid time format")

    return sum(
        int(v) * multipliers[k]
        for k, v in match.groupdict().items()
        if v is not None)


class Domain(object):
    def __init__(self, subdomain=None, name=None, top_domain=None):
        self.subdomain = subdomain
        self.name = name
        self.top_domain = top_domain

    @classmethod
    def from_str(cls, domain):
        parts = domain.split(".")

        # TODO: Does not handle .co.uk style top domains
        subdomain = ".".join(parts[:-2]) or None
        name = parts[-2]
        top_domain = parts[-1]

        return cls(subdomain, name, top_domain)

    @property
    def domain(self):
        return "{}.{}".format(self.name, self.top_domain)

    def __str__(self):
        if self.subdomain is None:
            return self.domain
        return "{}.{}".format(self.subdomain, self.domain)


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class LoopiaAuthenticator(Plugin):
    """
    Loopia DNS ACME authenticator.

    Super!
    """

    #: Short description of plugin
    description = __doc__.strip().split("\n", 1)[0]

    @classmethod
    def add_parser_arguments(cls, add):
        add("user", action="store", help="Loopia API username.")
        add("password", action="store", help="Loopia API password.")
        add(
            "time-limit",
            action="store",
            default="30m",
            help="Time limit for retries on local challenge verification.")
        add(
            "time-delay",
            action="store",
            default="1m",
            help="Time before trying to verify challange locally.")
        add(
            "retry-interval",
            action="store",
            default="30s",
            help="Time between each localverification retry.")

    @property
    def time_limit(self):
        return parse_time(self.conf("time-limit"))

    @property
    def time_delay(self):
        return parse_time(self.conf("time-delay"))

    @property
    def retry_interval(self):
        return parse_time(self.conf("retry-interval"))

    @property
    def _can_self_verify(self):
        return DNS_AVAILABLE

    def prepare(self):
        """
        Initializer for plugin
        """

        user = self.conf("user")
        password = self.conf("password")

        if not user:
            raise KeyError("Username not defined. Call with --{ns}{opt}".format(
                ns=self.option_namespace,
                opt="user"))

        if not password:
            raise KeyError("Password not defined. Call with --{ns}{opt}".format(
                ns=self.option_namespace,
                opt="password"))

        # Verify correctness of other options
        try:
            self.time_limit
        except ValueError:
            raise ValueError("Invalid format for time limit.")

        try:
            self.time_delay
        except ValueError:
            raise ValueError("Invalid format for time delay.")

        try:
            self.retry_interval
        except ValueError:
            raise ValueError("Invalid format for retry interval.")

        self.loopia = Loopia(self.conf("user"), self.conf("password"))

    def more_info(self):
        """
        More in-depth description of the plugin.
        """

        return "\n".join(line[4:] for line in __doc__.strip().split("\n"))

    def get_chall_pref(self, domain):
        """
        Return a list of all supported challenge types of this plugin.
        """

        return [DNS01]

    def verify_challenge(self, achall, response):
        """
        Verify that the given authentication challange has been completed.
        """

        try:
            verification_status = response.simple_verify(
                achall.chall,
                achall.domain,
                achall.account_key.public_key())
        except DependencyError:
            logger.warning(
                "Self verification requires optional "
                "dependency `dnspython` to be installed.")
            raise
        else:
            if verification_status:
                logger.info("Verification successful")
                return True
            else:
                logger.warning("Self-verify of challenge failed.")

        return False

    def perform_challenge(self, achall):
        """
        Complete a given authentication challenge.

        :param achall: A DNS01 challenge
        :return: A challenge response object
        """

        response, token = achall.response_and_validation()

        chall_domain = Domain.from_str(achall.validation_domain_name(achall.domain))

        logger.info("Creating record for {} with token {}".format(
            chall_domain, token))

        dns_record = DnsRecord("TXT", ttl=30, data=token)

        self.loopia.add_zone_record(
            dns_record, chall_domain.domain, chall_domain.subdomain)

        # Verify the result of adding the zone record. If the verification fails
        # it will retry twice after a delay since changes may not have
        # propagated yet.
        if not self._can_self_verify:
            logger.info((
                "Self-verification is unavailable. Trying to authenticate in "
                "{} seconds.").format(self.time_delay))
            sleep(self.time_delay)
            return response

        start_time = datetime.now()
        max_time = start_time + timedelta(seconds=self.time_limit)
        for i in itertools.count():
            logger.debug("Self-verification try #{}".format(i + 1))

            current_time = datetime.now()
            if i == 0:
                sleep(self.time_delay)
            else:
                # Sleep for the remaining time of the
                delay = self.retry_interval - (
                    current_time - start_time).total_seconds()
                sleep(0 if delay < 0 else delay)

            if self.verify_challenge(achall, response):
                break
            elif current_time < max_time:
                seconds = 30 * (i + 1)
                logger.info(
                    "Retrying self-verification in {} seconds.".format(seconds))
                sleep(seconds)
            else:
                # It is possible that the DNS change did not propagate
                # yet, in which case we will make the authentication fail.
                logger.warning(
                    "Unable to verify that the challenge was completed.")
                return


        return response

    def perform(self, achalls):
        """
        Call perform_challenge for all challenges in achalls and return the
        responses as a list.

        :param achalls: List of challenges to authenticate.
        :return: List of challenge responses
        """

        return [self.perform_challenge(achall) for achall in achalls]

    def cleanup_challenge(self, achall):
        """
        Restore the side-effects of completing the given challenge. It is
        possible to run this function despite all stepss in the challenge not
        completing.

        :param achall: Authentication challenge to cleanup after
        """

        chall_domain = Domain.from_str(
            achall.validation_domain_name(achall.domain))

        logger.info("Cleaning up challenge domain {}".format(chall_domain))

        records = self.loopia.get_zone_records(
            chall_domain.domain, chall_domain.subdomain)
        for record in records:
            logger.debug("Removing zone record {}".format(record))
            self.loopia.remove_zone_record(
                record.id, chall_domain.domain, chall_domain.subdomain)

        logger.debug("Removing subdomain {}".format(chall_domain.subdomain))
        self.loopia.remove_subdomain(
            chall_domain.domain, chall_domain.subdomain)

    def cleanup(self, achalls):
        """
        Call cleanup_challenge for all challenges in achalls.

        :param achalls: List of authentication challenges to cleanup after.
        """
        for achall in achalls:
            self.cleanup_challenge(achall)
