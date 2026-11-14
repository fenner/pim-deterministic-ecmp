"""Check workload coverage, unbiased bookkeeping, deadlines, and recovery."""

import json
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from run_hash_search import analyze_batch, batch_plan, run_worker, summarize
from search_hashes import source_spans, valid_group


class DriverTest(unittest.TestCase):
    def test_balanced_workload_cycle_and_address_constraints(self):
        config = {"paths": [2, 3, 4, 8, 16], "seed": 42}
        plans = [batch_plan(i, config) for i in range(140)]
        self.assertEqual(len({p["stratum"] for p in plans}), 140)
        self.assertEqual(plans, [batch_plan(i, config) for i in range(140)])
        for plan in plans:
            self.assertTrue(all(valid_group(IPv4Address(g)) for g in plan["groups"]))
            self.assertTrue(source_spans(plan["source_prefix"]))
            self.assertTrue(source_spans(plan["validation_prefix"]))
            if plan["source_prefix"] != "0.0.0.0/0":
                self.assertFalse(IPv4Network(plan["source_prefix"]).overlaps(
                    IPv4Network(plan["validation_prefix"])))
            if plan["pattern"] == "subnets":
                self.assertEqual(IPv4Network(plan["router_prefix"]).prefixlen, 16)

    def test_analysis_counts_both_hashes_and_excludes_tied_cases(self):
        state = {"config": {"top": 1}, "strata": {}, "top": {"pim": [], "jenkins": []}}
        cases = []
        for i, (pim, jenkins, ties) in enumerate([(0, 1, 0), (5.001, 2, 0), (25, 3, 2)]):
            cases.append({"trial": i, "search": {
                "pim": {"flows": 100, "ties": ties, "max_deviation_pp": pim},
                "jenkins": {"flows": 100, "ties": 0, "max_deviation_pp": jenkins},
            }})
        analyze_batch(state, 0, {"paths": 3, "stratum": "test"}, {"cases": cases})
        report = summarize(state)
        self.assertEqual(report["overall"]["pim"]["tie_free_cases"], 2)
        self.assertEqual(report["overall"]["pim"]["tied_flows"], 2)
        self.assertEqual(report["overall"]["pim"]["p95_pp"], 5)
        self.assertEqual(report["overall"]["pim"]["max_pp"], 5.001)
        self.assertEqual(report["overall"]["pim"]["at_least_pp"]["5"], 1)
        self.assertEqual(report["strata"]["test"]["pim_better"], 1)
        self.assertEqual(report["strata"]["test"]["jenkins_better"], 1)
        self.assertEqual(report["top"]["pim"][0]["case"]["trial"], 1)
        self.assertEqual(report["top"]["jenkins"][0]["case"]["trial"], 2)

    def test_deadline_stops_unfinished_worker(self):
        with tempfile.TemporaryDirectory() as temporary:
            started = time.monotonic()
            completed = run_worker([sys.executable, "-c", "import time; time.sleep(30)"],
                                   Path(temporary) / "worker.log", started + .1)
            self.assertFalse(completed)
            self.assertLess(time.monotonic() - started, 5)

    def test_resume_and_archive_recovery_do_not_double_count(self):
        script = Path(__file__).with_name("run_hash_search.py")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)

            def run(*extra):
                result = subprocess.run([sys.executable, str(script), "--output", temporary,
                                         "--max-batches", "1", *extra],
                                        text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return json.loads((directory / "state.json").read_text())

            first = run("--batch-trials", "2", "--paths", "3", "--max-sources", "16", "--top", "1")
            second = run("--resume")
            self.assertEqual(first["completed_batches"], 1)
            self.assertEqual(second["completed_batches"], 2)
            # Simulate a crash after archiving batch 1 but before checkpointing it.
            (directory / "state.json").write_text(json.dumps(first))
            recovered = run("--resume")
            self.assertEqual(recovered, second)
            self.assertEqual(len(list(directory.glob("batch-*.json.gz"))), 2)
            summary = json.loads((directory / "summary.json").read_text())
            self.assertEqual(summary["overall"]["pim"]["cases"], 8)
            for examples in summary["top"].values():
                self.assertIn("validation", examples[0]["case"])
            self.assertIn("Jenkins", (directory / "report.md").read_text())


if __name__ == "__main__":
    unittest.main()
