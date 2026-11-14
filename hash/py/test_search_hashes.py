"""Check hash compatibility, selection semantics, and allocation constraints."""

import unittest
from ipaddress import IPv4Address, IPv4Network

import numpy as np

from jenkins_hash import pim_rpf_sg_calculate_hash
from search_hashes import (
    compare, jenkins_hash, pim_hash, router_set, source_addresses, winner_stats,
    source_spans, valid_group,
)


class SearchHashesTest(unittest.TestCase):
    def test_vectorized_hashes_match_scalar_implementations(self):
        rng = np.random.default_rng(42)
        sources = rng.integers(0, 2**32, size=256, dtype=np.uint64)
        for group, router in [(0xE0010101, 0x0A000001),
                              (0xEFFFFFFF, 0xFFFFFFFF), (0, 0)]:
            expected_jenkins = [
                pim_rpf_sg_calculate_hash(str(IPv4Address(int(s))),
                                          str(IPv4Address(group)),
                                          str(IPv4Address(router)))
                for s in sources
            ]

            def stage(g, c):
                return (1103515245 * ((1103515245 * g + 12345) ^ c) + 12345) % 2**31

            expected_pim = [stage(router, stage(group, int(s))) for s in sources]
            np.testing.assert_array_equal(jenkins_hash(sources, group, router),
                                          expected_jenkins)
            np.testing.assert_array_equal(pim_hash(sources, group, router), expected_pim)

    def test_ties_are_not_assigned_to_first_router(self):
        stats = winner_stats(np.array([[9, 1, 5], [9, 2, 3], [4, 2, 7]]))
        self.assertEqual(stats["counts"], [0, 0, 1])
        self.assertEqual(stats["ties"], 2)
        self.assertEqual(stats["shares"], [0, 0, 1])
        all_tied = winner_stats(np.ones((3, 4), dtype=np.uint64))
        self.assertEqual(all_tied["ties"], 4)
        self.assertIsNone(all_tied["max_deviation_pp"])

    def test_router_allocations_stay_in_block_and_are_distinct(self):
        network = IPv4Network("10.0.0.0/16")
        rng = np.random.default_rng(12345)
        for pattern in ("random", "consecutive", "strided", "subnets"):
            for _ in range(100):
                routers = router_set(network, 8, pattern, rng)
                self.assertEqual(len(set(routers)), 8)
                self.assertTrue(all(IPv4Address(r) in network for r in routers))
                self.assertNotIn(int(network.network_address), routers)
                self.assertNotIn(int(network.broadcast_address), routers)
                if pattern == "subnets":
                    self.assertEqual(len({r & 255 for r in routers}), 1)
                if pattern in ("consecutive", "strided"):
                    steps = {b - a for a, b in zip(routers, routers[1:])}
                    self.assertEqual(len(steps), 1)
                    if pattern == "consecutive":
                        self.assertEqual(steps, {1})

    def test_source_sampling_is_reproducible_and_without_replacement(self):
        args = ("192.0.0.0/16", 1000)
        first = source_addresses(*args, np.random.default_rng(42))
        second = source_addresses(*args, np.random.default_rng(42))
        np.testing.assert_array_equal(first, second)
        self.assertEqual(len(set(first.tolist())), 1000)
        self.assertTrue(all(IPv4Address(int(s)) in IPv4Network(args[0]) for s in first))
        complete = source_addresses("192.0.2.0/24", 1000, np.random.default_rng(42))
        self.assertEqual(len(complete), 256)

    def test_reported_counterexample(self):
        sources = source_addresses("192.0.0.0/16", 65536, np.random.default_rng(42))
        routers = [int(IPv4Address(r)) for r in
                   ("10.0.0.1", "10.0.37.210", "10.0.75.163")]
        result = compare(sources, int(IPv4Address("224.1.1.1")), routers)
        self.assertEqual(result["pim"]["counts"], [23048, 23231, 19257])
        self.assertEqual(result["jenkins"]["counts"], [21954, 21950, 21632])
        self.assertEqual(result["pim"]["ties"], 0)
        self.assertEqual(result["jenkins"]["ties"], 0)

    def test_exact_group_boundaries(self):
        for address in ("224.0.0.0", "239.254.254.254"):
            self.assertTrue(valid_group(IPv4Address(address)))
        for address in ("223.255.255.255", "239.254.254.255", "240.0.0.0"):
            self.assertFalse(valid_group(IPv4Address(address)))

    def test_source_exclusion_and_boundaries(self):
        rng = np.random.default_rng(42)
        with self.assertRaisesRegex(ValueError, "no eligible addresses"):
            source_addresses("224.1.1.0/24", 100, rng)
        with self.assertRaisesRegex(ValueError, "no eligible addresses"):
            source_addresses("224.0.0.0/32", 100, rng)
        sources = source_addresses("239.254.254.254/31", 100, rng)
        self.assertEqual(sources.tolist(), [int(IPv4Address("239.254.254.255"))])
        sources = source_addresses("224.0.0.0/3", 1000, rng)
        self.assertTrue(all(s > int(IPv4Address("239.254.254.254")) for s in sources))
        sources = source_addresses("0.0.0.0/0", 10000, rng)
        self.assertEqual(len(set(sources.tolist())), 10000)
        self.assertFalse(any(valid_group(s) for s in sources))
        self.assertTrue(any(s < int(IPv4Address("224.0.0.0")) for s in sources))
        self.assertTrue(any(s > int(IPv4Address("239.254.254.254")) for s in sources))
        spans = source_spans("0.0.0.0/0")
        self.assertEqual(spans, [(0, int(IPv4Address("223.255.255.255"))),
                                 (int(IPv4Address("239.254.254.255")), 2**32 - 1)])


if __name__ == "__main__":
    unittest.main()
