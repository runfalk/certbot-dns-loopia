import pytest

from certbot_dns_loopia._internal.dns_loopia import DnsRecord


def test_type_validation() -> None:
    # Does not raise
    DnsRecord(type="TXT")

    # Raises
    with pytest.raises(ValueError):
        DnsRecord(type=1)  # type: ignore


def test_ttl_validation() -> None:
    # Does not raise
    DnsRecord(type="TXT", ttl=10)

    # Raises
    with pytest.raises(ValueError):
        DnsRecord(type="TXT", ttl="Error")  # type: ignore


def test_priority_validation() -> None:
    # Does not raise
    DnsRecord(type="TXT", priority=1)

    # Raises
    with pytest.raises(ValueError):
        DnsRecord(type="TXT", priority="First")  # type: ignore


def test_rdata_validation() -> None:
    # Does not raise
    DnsRecord(type="TXT", rdata="Some data")

    # Raises
    with pytest.raises(ValueError):
        DnsRecord(type="TXT", rdata=1337)  # type: ignore


def test_record_id_validation() -> None:
    # Does not raise
    DnsRecord(type="TXT", record_id=500)

    # Raises
    with pytest.raises(ValueError):
        DnsRecord(type="TXT", record_id="NONE")  # type: ignore


def test_that_equals_ignores_record_id() -> None:
    dns_record_1 = DnsRecord(
        type="TXT",
        ttl=3600,
        priority=10,
        rdata="Many info. Such data. Wow.",
        record_id=150,
    )

    dns_record_2 = DnsRecord(
        type="TXT",
        ttl=3600,
        priority=10,
        rdata="Many info. Such data. Wow.",
        record_id=795,
    )

    assert dns_record_1 == dns_record_2


def test_that_equals_fails_when_types_mismatch() -> None:
    dns_record_1 = DnsRecord(
        type="TXT",
        ttl=3600,
        priority=10,
        rdata="Many info. Such data. Wow.",
        record_id=150,
    )

    assert dns_record_1 != "foo"
