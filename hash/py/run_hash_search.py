#!/usr/bin/env python3
"""Run resumable, time-bounded search_hashes.py batches and summarize both hashes."""

import argparse
from collections import Counter
import fcntl
import gzip
import hashlib
from ipaddress import IPv4Address, IPv4Network
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

from search_hashes import GROUP_MIN, GROUP_MAX


PATTERNS = [(24, "consecutive"), (24, "strided"), (24, "random"),
            (16, "consecutive"), (16, "strided"), (16, "subnets"), (16, "random")]
POOLS = [IPv4Network(p) for p in ("10.0.0.0/8", "172.16.0.0/12", "192.0.0.0/16")]
FIXED_GROUPS = ["224.1.1.1", "239.1.2.3", "224.0.0.1", "224.0.0.0", "239.254.254.254"]


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def subnet(pool, prefixlen, rng):
    offset = int(rng.integers(0, 1 << (prefixlen - pool.prefixlen)))
    return str(IPv4Network((int(pool.network_address) + (offset << (32 - prefixlen)), prefixlen)))


def batch_plan(index, config):
    """Visit every workload cell once per round; reproduce a batch by index."""
    cells = list(itertools.product(config["paths"], PATTERNS, (24, 20, 16, 0)))
    cycle, position = divmod(index, len(cells))
    order = np.random.default_rng(np.random.SeedSequence([config["seed"], cycle, 0]))
    cell = cells[int(order.permutation(len(cells))[position])]
    paths, (router_bits, pattern), source_bits = cell
    rng = np.random.default_rng(np.random.SeedSequence([config["seed"], index, 1]))
    router_prefix = subnet(POOLS[0], router_bits, rng)
    pool_index = int(rng.integers(0, len(POOLS)))
    source_prefix = subnet(POOLS[pool_index], source_bits, rng) if source_bits else "0.0.0.0/0"
    validation_prefix = subnet(POOLS[(pool_index + 1) % len(POOLS)], 16, rng)
    return {
        "paths": paths, "router_prefix": router_prefix, "pattern": pattern,
        "source_prefix": source_prefix, "validation_prefix": validation_prefix,
        "groups": [FIXED_GROUPS[index % len(FIXED_GROUPS)],
                   str(IPv4Address(int(rng.integers(GROUP_MIN, GROUP_MAX + 1))))],
        "seed": int(rng.integers(0, 2**32)),
        "stratum": f"paths={paths};router=/{router_bits};{pattern};sources=/{source_bits}",
    }


def worker_command(script, plan, config, output):
    command = [sys.executable, str(script),
               "--router-prefix", plan["router_prefix"], "--paths", str(plan["paths"]),
               "--patterns", plan["pattern"], "--search-sources", plan["source_prefix"],
               "--validation-sources", plan["validation_prefix"],
               "--trials", str(config["batch_trials"]), "--seed", str(plan["seed"]),
               "--max-sources", str(config["max_sources"]), "--top", str(config["top"]),
               "--rank-by", "both", "--json", str(output)]
    for group in plan["groups"]:
        command.extend(["--group", group])
    return command


def run_worker(command, log_path, deadline):
    """Stop an unfinished batch at the deadline; completed batches stay safe."""
    with log_path.open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                try:
                    status = process.wait(timeout=min(1, remaining))
                except subprocess.TimeoutExpired:
                    continue
                if status:
                    raise RuntimeError(f"search batch failed ({status}); see {log_path}")
                return True
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def empty_hash_stats():
    return {"cases": 0, "tied_cases": 0, "tied_flows": 0, "flows": 0,
            "histogram": {}, "max_deviation_pp": None}


def analyze_batch(state, index, plan, payload):
    """Maintain bounded-memory histograms and selected examples, not all cases."""
    bucket = state["strata"].setdefault(plan["stratum"], {
        "paths": plan["paths"], "cases": 0,
        "pim_better": 0, "jenkins_better": 0, "equal": 0,
        "pim": empty_hash_stats(), "jenkins": empty_hash_stats(),
    })
    for case in payload["cases"]:
        bucket["cases"] += 1
        paired = all(case["search"][name]["ties"] == 0 for name in ("pim", "jenkins"))
        if paired:
            difference = (case["search"]["pim"]["max_deviation_pp"] -
                          case["search"]["jenkins"]["max_deviation_pp"])
            bucket["pim_better" if difference < -1e-12 else
                   "jenkins_better" if difference > 1e-12 else "equal"] += 1
        for name in ("pim", "jenkins"):
            result, stats = case["search"][name], bucket[name]
            stats["cases"] += 1
            stats["flows"] += result["flows"]
            stats["tied_flows"] += result["ties"]
            if result["ties"]:
                stats["tied_cases"] += 1
                continue
            deviation = result["max_deviation_pp"]
            # Quantile error is <0.01 percentage points; maxima remain exact.
            bin_key = str(math.floor(deviation * 100))
            stats["histogram"][bin_key] = stats["histogram"].get(bin_key, 0) + 1
            current_max = stats["max_deviation_pp"]
            stats["max_deviation_pp"] = max(deviation, current_max or 0)
    for name in ("pim", "jenkins"):
        candidates = [{"batch": index, "plan": plan, "case": case}
                      for case in payload["cases"] if case["search"][name]["ties"] == 0]
        candidates.extend(state["top"][name])
        candidates.sort(key=lambda c: c["case"]["search"][name]["max_deviation_pp"], reverse=True)
        state["top"][name] = candidates[:state["config"]["top"]]
    state["completed_batches"] = index + 1


def hash_summary(stats):
    histogram = sorted((int(key), count) for key, count in stats["histogram"].items())
    count = sum(n for _, n in histogram)

    def quantile(fraction):
        if not count:
            return None
        target, total = math.ceil(fraction * count), 0
        for key, number in histogram:
            total += number
            if total >= target:
                return key / 100

    return {
        "cases": stats["cases"], "tie_free_cases": count,
        "tied_cases": stats["tied_cases"], "tied_flows": stats["tied_flows"],
        "flows": stats["flows"], "median_pp": quantile(.5), "p95_pp": quantile(.95),
        "p99_pp": quantile(.99), "max_pp": stats["max_deviation_pp"],
        "at_least_pp": {str(threshold): sum(n for key, n in histogram if key >= threshold * 100)
                        for threshold in (1, 2, 5, 10)},
    }


def summarize(state):
    overall = {name: empty_hash_stats() for name in ("pim", "jenkins")}
    strata = {}
    for key, bucket in sorted(state["strata"].items()):
        strata[key] = {k: bucket[k] for k in ("cases", "paths", "pim_better", "jenkins_better", "equal")}
        for name in overall:
            strata[key][name] = hash_summary(bucket[name])
            source, dest = bucket[name], overall[name]
            for field in ("cases", "tied_cases", "tied_flows", "flows"):
                dest[field] += source[field]
            dest["histogram"] = dict(Counter(dest["histogram"]) + Counter(source["histogram"]))
            if source["max_deviation_pp"] is not None:
                dest["max_deviation_pp"] = max(dest["max_deviation_pp"] or 0, source["max_deviation_pp"])
    return {"completed_batches": state["completed_batches"],
            "overall": {name: hash_summary(stats) for name, stats in overall.items()},
            "strata": strata, "top": state["top"]}


def write_report(directory, state):
    summary = summarize(state)
    atomic_json(directory / "summary.json", summary)

    def number(value):
        return "n/a" if value is None else f"{value:.2f}"

    lines = ["# Hash search results", "", f"Completed batches: {state['completed_batches']}", "",
             "Deviations are percentage points from equal share. Quantiles have <0.01 pp binning error; "
             "maxima are exact. Cases with ties are excluded from deviation statistics. "
             "These are descriptive results; flows, groups, and router sets are not independent samples.", "",
             "The overall mixture combines different workloads and source counts; use the strata for decisions.", "",
             "| Hash | Cases | Cases with ties | Median | p95 | p99 | Max | >=5 pp |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, label in (("pim", "PIM hash"), ("jenkins", "Jenkins")):
        stats = summary["overall"][name]
        values = " | ".join(number(stats[k]) for k in ("median_pp", "p95_pp", "p99_pp", "max_pp"))
        lines.append(f"| {label} | {stats['cases']} | {stats['tied_cases']} | {values} | {stats['at_least_pp']['5']} |")
    lines.extend(["", "## Workloads", "",
                  "A /0 source workload samples uniformly from eligible IPv4 addresses. Other source prefixes "
                  "are enumerated up to the configured cap. Router blocks and source prefixes vary between batches.", "",
                  "| Workload | Cases | PIM p95 | Jenkins p95 | PIM max | Jenkins max | PIM better | Jenkins better | Equal |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for key, bucket in summary["strata"].items():
        values = " | ".join(number(bucket[name][metric])
                            for metric in ("p95_pp", "max_pp") for name in ("pim", "jenkins"))
        lines.append(f"| {key} | {bucket['cases']} | {values} | {bucket['pim_better']} | "
                     f"{bucket['jenkins_better']} | {bucket['equal']} |")
    lines.extend(["", "## Selected counterexamples", "",
                  "These examples were selected for large deviations; additional-prefix checks "
                  "are not included in the aggregate search statistics. Each batch validates its top cases for both hashes.", ""])
    for name, examples in summary["top"].items():
        lines.extend([f"### {'PIM hash' if name == 'pim' else 'Jenkins'}", ""])
        for example in examples:
            case, plan = example["case"], example["plan"]
            lines.append(f"- Batch {example['batch']}, {plan['source_prefix']}, group {case['group']}, "
                         f"routers {', '.join(case['routers'])}")
            for label, result in [("Search", case["search"])] + [
                (f"Additional prefix {v['sources']}", v["results"]) for v in case.get("validation", [])
            ]:
                lines.append(f"  - {label}: PIM {number(result['pim']['max_deviation_pp'])} pp, "
                             f"Jenkins {number(result['jenkins']['max_deviation_pp'])} pp; "
                             f"ties {result['pim']['ties']}/{result['jenkins']['ties']}")
        lines.append("")
    temporary = directory / "report.md.tmp"
    temporary.write_text("\n".join(lines) + "\n")
    temporary.replace(directory / "report.md")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hours", type=float, default=24, help="time budget for this invocation")
    parser.add_argument("--max-batches", type=int, help="optional limit on additional batches")
    parser.add_argument("--batch-trials", type=int, default=100)
    parser.add_argument("--paths", default="2,3,4,8,16")
    parser.add_argument("--max-sources", type=int, default=65536)
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--resume", action="store_true", help="resume using saved experiment settings")
    parser.add_argument("--report-only", action="store_true", help="rebuild reports from saved state")
    args = parser.parse_args()
    if not math.isfinite(args.hours) or args.hours <= 0:
        parser.error("--hours must be finite and positive")
    if args.max_batches is not None and args.max_batches < 1:
        parser.error("--max-batches must be positive")
    try:
        paths = [int(value) for value in args.paths.split(",")]
    except ValueError:
        parser.error("--paths must be comma-separated integers")
    if not paths or len(set(paths)) != len(paths) or any(not 2 <= p <= 64 for p in paths):
        parser.error("--paths must contain distinct values between 2 and 64")
    if min(args.batch_trials, args.max_sources, args.top) < 1 or args.seed < 0:
        parser.error("batch-trials, max-sources and top must be positive; seed must be nonnegative")

    directory = args.output.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    lock = (directory / ".lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.error("another driver is using this output directory")
    script = Path(__file__).with_name("search_hashes.py").resolve()
    fingerprints = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (Path(__file__).resolve(), script)}
    fingerprints["numpy"] = np.__version__
    fingerprints["python"] = sys.version
    state_path = directory / "state.json"
    if args.resume or args.report_only:
        if not state_path.exists():
            parser.error("no saved state in output directory")
        state = json.loads(state_path.read_text())
        if args.report_only:
            write_report(directory, state)
            return 0
        if state["fingerprints"] != fingerprints:
            parser.error("code or Python/NumPy version changed; use a new output directory")
        print("Resuming with saved experiment settings", flush=True)
    else:
        if state_path.exists() or list(directory.glob("batch-*")):
            parser.error("output already contains a run; use --resume or a new directory")
        state = {"config": {"paths": paths, "batch_trials": args.batch_trials,
                             "max_sources": args.max_sources, "top": args.top, "seed": args.seed},
                 "fingerprints": fingerprints, "completed_batches": 0,
                 "strata": {}, "top": {"pim": [], "jenkins": []}}
        atomic_json(state_path, state)
    deadline = time.monotonic() + args.hours * 3600
    completed_now = 0
    try:
        while time.monotonic() < deadline and (
            args.max_batches is None or completed_now < args.max_batches
        ):
            index = state["completed_batches"]
            plan = batch_plan(index, state["config"])
            archive = directory / f"batch-{index:08d}.json.gz"
            if archive.exists():
                # Recover a batch archived immediately before an interrupted checkpoint.
                with gzip.open(archive, "rt") as stream:
                    payload = json.load(stream)
            else:
                pending = directory / f"batch-{index:08d}.pending.json"
                command = worker_command(script, plan, state["config"], pending)
                print(f"Batch {index}: {plan['stratum']}; sources {plan['source_prefix']}", flush=True)
                if not run_worker(command, directory / f"batch-{index:08d}.log", deadline):
                    print("Time budget reached; unfinished batch will be retried on resume.", flush=True)
                    break
                payload = json.loads(pending.read_text())
                payload["driver"] = {"batch": index, "plan": plan, "command": command}
                temporary = archive.with_suffix(".tmp")
                with gzip.open(temporary, "wt") as stream:
                    json.dump(payload, stream)
                temporary.replace(archive)
                pending.unlink()
            analyze_batch(state, index, plan, payload)
            atomic_json(state_path, state)
            write_report(directory, state)
            completed_now += 1
            print(f"Completed {state['completed_batches']} batches; report: {directory / 'report.md'}", flush=True)
    except KeyboardInterrupt:
        print("Interrupted; completed batches are saved.", flush=True)
        state = json.loads(state_path.read_text())
    except (RuntimeError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    write_report(directory, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
