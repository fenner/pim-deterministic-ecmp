# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Jenkins one-at-a-time hash for PIM source/group/router ID selection."""

from ipaddress import IPv4Address


def jenkins_one_at_a_time(key: bytes) -> int:
    """Hash bytes using the C implementation's unsigned 32-bit arithmetic."""
    mask = 0xFFFFFFFF
    value = 0
    for byte in key:
        value = (value + byte) & mask
        value = (value + (value << 10)) & mask
        value ^= value >> 6

    value = (value + (value << 3)) & mask
    value ^= value >> 11
    return (value + (value << 15)) & mask


def pim_rpf_sg_calculate_hash(
    source: str, group: str, router_id: str
) -> int:
    """Hash source, group, and router ID IPv4 addresses in network byte order."""
    key = b"".join(IPv4Address(address).packed
                   for address in (source, group, router_id))
    return jenkins_one_at_a_time(key)


if __name__ == "__main__":
    print(pim_rpf_sg_calculate_hash("192.0.0.2", "224.1.1.1", "10.0.0.1"))
