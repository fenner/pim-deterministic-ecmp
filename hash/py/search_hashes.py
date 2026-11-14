#!/usr/bin/env python3
# Copyright (c) 2026 Arista Networks, Inc. All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Search realistic IPv4 router allocations for highest-hash selection bias.

Requires NumPy. Groups must be in 224.0.0.0 through 239.254.254.254,
inclusive; sources exclude that range. Source prefixes otherwise include
network and broadcast addresses. Eligible addresses in larger prefixes are
sampled uniformly without replacement, using --max-sources as the limit.

Ties are reported, not broken: evaluating the local-information tiebreaker
requires inputs that this tool does not have. Shares and deviations describe
only flows with a unique winner.
"""

import argparse
import json
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

import numpy as np


A = 1103515245
B = 12345
MASK31 = (1 << 31) - 1
MASK32 = (1 << 32) - 1
GROUP_MIN = int(IPv4Address("224.0.0.0"))
GROUP_MAX = int(IPv4Address("239.254.254.254"))


def valid_group(address):
    return GROUP_MIN <= int(address) <= GROUP_MAX


def pim_stage(g, c):
    """The PIM function with M = 0xffffffff (scalar or NumPy array)."""
    # Reducing the first multiplication also bounds temporary values. NumPy's
    # uint64 wraparound preserves the low 31 bits of the final multiplication.
    return (A * (((A * g + B) & MASK31) ^ c) + B) & MASK31


def pim_hash(source, group, router_id):
    return pim_stage(router_id, pim_stage(group, source))


def jenkins_hash(source, group, router_id):
    """Vectorized Jenkins one-at-a-time hash in source/group/router ID order."""
    value = np.zeros_like(source, dtype=np.uint64)
    for field in (source, group, router_id):
        for shift in (24, 16, 8, 0):
            value = (value + ((field >> shift) & 255)) & MASK32
            value = (value + (value << 10)) & MASK32
            value ^= value >> 6
    value = (value + (value << 3)) & MASK32
    value ^= value >> 11
    return (value + (value << 15)) & MASK32


def winner_stats(scores):
    """Count strict winners; never let argmax silently resolve a tie."""
    highest = scores.max(axis=0)
    winners = scores == highest
    unique = winners.sum(axis=0) == 1
    counts = winners[:, unique].sum(axis=1)
    unique_count = int(unique.sum())
    shares = counts / unique_count if unique_count else None
    return {
        "counts": counts.tolist(),
        "flows": int(scores.shape[1]),
        "ties": int((~unique).sum()),
        "shares": shares.tolist() if shares is not None else None,
        "max_deviation_pp": (
            float(np.max(np.abs(shares - 1 / scores.shape[0])) * 100)
            if shares is not None else None
        ),
    }


def compare(sources, group, routers):
    inner = pim_stage(group, sources)
    return {
        "pim": winner_stats(np.array([pim_stage(r, inner) for r in routers])),
        "jenkins": winner_stats(
            np.array([jenkins_hash(sources, group, r) for r in routers])
        ),
    }


def source_spans(prefix):
    """Return eligible inclusive address spans without enumerating the prefix."""
    network = IPv4Network(prefix)
    first, last = int(network.network_address), int(network.broadcast_address)
    spans = [(max(first, low), min(last, high))
             for low, high in ((0, GROUP_MIN - 1), (GROUP_MAX + 1, MASK32))
             if max(first, low) <= min(last, high)]
    if not spans:
        raise ValueError(f"source prefix {prefix} has no eligible addresses")
    return spans


def source_addresses(prefix, limit, rng):
    spans = source_spans(prefix)
    lengths = [last - first + 1 for first, last in spans]
    size = sum(lengths)
    offsets = (np.arange(size, dtype=np.uint64) if size <= limit else
               rng.choice(size, size=limit, replace=False).astype(np.uint64))
    addresses = spans[0][0] + offsets
    if len(spans) == 2:
        second = offsets >= lengths[0]
        addresses[second] = spans[1][0] + (offsets[second] - lengths[0])
    return addresses


def router_bounds(network):
    # /31 addresses are both usable. Exclude network/broadcast for larger blocks.
    exclude = int(network.prefixlen < 31)
    return (int(network.network_address) + exclude,
            int(network.broadcast_address) - exclude)


def router_set(network, paths, pattern, rng):
    low, high = router_bounds(network)
    size = high - low + 1
    if pattern == "random":
        return sorted((low + rng.choice(size, paths, replace=False)).tolist())
    if pattern == "subnets":
        # The same host number in distinct /24s within the router block.
        subnets = rng.choice(network.num_addresses // 256, paths, replace=False)
        host = int(rng.integers(1, 255))
        return sorted((int(network.network_address) + subnets * 256 + host).tolist())
    step = 1 if pattern == "consecutive" else int(
        rng.integers(1, (size - 1) // (paths - 1) + 1)
    )
    start = int(rng.integers(low, high - (paths - 1) * step + 1))
    return [start + i * step for i in range(paths)]


def describe(stats):
    shares = (", ".join(f"{s * 100:.2f}%" for s in stats["shares"])
              if stats["shares"] is not None else "no unique winners")
    deviation = stats["max_deviation_pp"]
    deviation_text = f"{deviation:.2f} pp" if deviation is not None else "n/a"
    return (f"[{shares}]; counts={stats['counts']}; "
            f"max deviation={deviation_text}; ties={stats['ties']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--router-prefix", type=IPv4Network, default=IPv4Network("10.0.0.0/16"))
    parser.add_argument("--paths", type=int, default=3)
    parser.add_argument("--trials", type=int, default=1000, help="number of router sets")
    parser.add_argument("--patterns", default="consecutive,strided,subnets,random",
                        help="comma-separated allocation patterns, cycled in order")
    parser.add_argument("--group", action="append", type=IPv4Address,
                        help="group in 224.0.0.0–239.254.254.254 inclusive; repeatable")
    parser.add_argument("--search-sources", default="192.0.0.0/20")
    parser.add_argument("--validation-sources", action="append",
                        help="source prefix for subsequent checks; repeatable; default 192.1.0.0/16")
    parser.add_argument("--max-sources", type=int, default=65536)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--rank-by", choices=("pim", "jenkins", "both"), default="pim",
                        help="select top cases for either hash or the union of both")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--threshold-pp", type=float, default=5,
                        help="deviation threshold for aggregate reporting")
    parser.add_argument("--json", type=Path, help="write all search cases and top-case validation")
    args = parser.parse_args()

    patterns = args.patterns.split(",")
    if any(p not in {"consecutive", "strided", "subnets", "random"} for p in patterns):
        parser.error("unknown allocation pattern")
    if not 2 <= args.paths <= 64:
        parser.error("--paths must be between 2 and 64")
    low, high = router_bounds(args.router_prefix)
    if args.paths > high - low + 1:
        parser.error("router prefix has too few usable addresses")
    if "subnets" in patterns and (
        args.router_prefix.prefixlen > 24 or args.router_prefix.num_addresses // 256 < args.paths
    ):
        parser.error("subnets pattern needs at least --paths /24s; choose different --patterns")
    if min(args.trials, args.max_sources, args.top) < 1 or args.seed < 0:
        parser.error("trials, max-sources and top must be positive; seed must be nonnegative")
    if not np.isfinite(args.threshold_pp) or args.threshold_pp < 0:
        parser.error("threshold-pp must be finite and nonnegative")
    groups = args.group or [IPv4Address("224.1.1.1")]
    if any(not valid_group(group) for group in groups):
        parser.error("--group must be within 224.0.0.0–239.254.254.254 inclusive")
    validation_prefixes = args.validation_sources or ["192.1.0.0/16"]
    try:
        source_spans(args.search_sources)
        for prefix in validation_prefixes:
            source_spans(prefix)
    except ValueError as exc:
        parser.error(str(exc))

    # Separate random streams keep router sets independent of sampling limits.
    streams = np.random.SeedSequence(args.seed).spawn(2 + len(validation_prefixes))
    router_rng = np.random.default_rng(streams[0])
    sources = source_addresses(args.search_sources, args.max_sources,
                               np.random.default_rng(streams[1]))
    print(f"Seed {args.seed}; {args.trials} router sets in {args.router_prefix}; "
          f"{len(sources)} sources from {args.search_sources}", flush=True)
    print("Shares exclude tied flows; local-information tiebreaking is not simulated.")
    cases = []
    for trial in range(args.trials):
        pattern = patterns[trial % len(patterns)]
        routers = router_set(args.router_prefix, args.paths, pattern, router_rng)
        for group in groups:
            cases.append({
                "trial": trial, "pattern": pattern,
                "routers": [str(IPv4Address(r)) for r in routers],
                "group": str(group), "search": compare(sources, int(group), routers),
            })
        if (trial + 1) % 100 == 0:
            print(f"Searched {trial + 1}/{args.trials} router sets", flush=True)

    print("\nSearch summary (cases without ties; deviation from equal share):")
    for name, label in (("pim", "PIM hash"), ("jenkins", "Jenkins")):
        stats = [case["search"][name] for case in cases]
        deviations = [s["max_deviation_pp"] for s in stats if s["ties"] == 0]
        if deviations:
            p50, p95 = np.percentile(deviations, [50, 95])
            over = sum(d >= args.threshold_pp for d in deviations)
            print(f"{label}: median={p50:.2f} pp; p95={p95:.2f} pp; "
                  f"max={max(deviations):.2f} pp; "
                  f">={args.threshold_pp:g} pp: {over}/{len(deviations)}; "
                  f"cases with ties={sum(s['ties'] > 0 for s in stats)}")
        else:
            print(f"{label}: every case has ties")

    # These are selected counterexamples, not an unbiased validation sample.
    ranking_hashes = ("pim", "jenkins") if args.rank_by == "both" else (args.rank_by,)
    selected = {}
    for name in ranking_hashes:
        ranked = sorted(cases, key=lambda c: c["search"][name]["max_deviation_pp"]
                        if c["search"][name]["max_deviation_pp"] is not None else -1,
                        reverse=True)[:args.top]
        for case in ranked:
            selected[(case["trial"], case["group"])] = case
    top = list(selected.values())
    validation = [source_addresses(prefix, args.max_sources, np.random.default_rng(stream))
                  for prefix, stream in zip(validation_prefixes, streams[2:])]
    print(f"\nTop cases selected by {args.rank_by} deviation (selected by search):")
    for rank, case in enumerate(top, 1):
        print(f"\n{rank}. {case['pattern']}; group={case['group']}; "
              f"routers={', '.join(case['routers'])}")
        print("  Search PIM hash:", describe(case["search"]["pim"]))
        print("  Search Jenkins: ", describe(case["search"]["jenkins"]))
        case["validation"] = []
        for prefix, addresses in zip(validation_prefixes, validation):
            result = compare(addresses, int(IPv4Address(case["group"])),
                             [int(IPv4Address(r)) for r in case["routers"]])
            case["validation"].append({"sources": prefix, "results": result})
            print(f"  Validation {prefix} ({len(addresses)} sources):")
            print("    PIM hash:", describe(result["pim"]))
            print("    Jenkins: ", describe(result["jenkins"]))

    if args.json:
        config = {key: str(value) if isinstance(value, (Path, IPv4Network)) else value
                  for key, value in vars(args).items()}
        config["group"] = [str(group) for group in groups]
        config["validation_sources"] = validation_prefixes
        args.json.write_text(json.dumps({"config": config, "cases": cases,
                                         "top_trial_groups": [[c["trial"], c["group"]] for c in top]},
                                        indent=2) + "\n")
        print(f"\nSaved {args.json}")


if __name__ == "__main__":
    main()
