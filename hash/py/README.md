# PIM hash comparison

`search_hashes.py` searches for imbalance when each source/group flow chooses
the router with the highest hash. It compares the nested PIM hash
`h(router_id, h(group, source))` against the Jenkins one-at-a-time hash.
IPv4 addresses are interpreted as network-order integers;
Jenkins hashes the source, group, and router ID bytes in that order.

The search requires Python 3 and NumPy. If needed, install NumPy with
`python3 -m pip install numpy`.

```sh
python3 search_hashes.py --trials 1000 --top 5 --json results.json
```

By default this searches three-router allocations within `10.0.0.0/16`, using
all 4,096 sources in `192.0.0.0/20` and group `224.1.1.1`. It cycles through
four allocation patterns: consecutive router IDs, equally spaced IDs, matching
host numbers in different /24s, and random IDs within the block. The random seed
defaults to 12345. Repeat a command with the same NumPy version to reproduce it.

Every router set is evaluated using both hashes. The report shows the median,
95th percentile, and largest **maximum absolute deviation from equal share**, in
percentage points. For example, shares of 30%, 30%, and 40% have a maximum
deviation of 6.67 percentage points from the expected 33.33%.

The top cases are ranked by PIM hash deviation by default (`--rank-by both`
selects the top cases for each hash), and then checked using sources
from the separate prefix `192.1.0.0/16`. The JSON output includes every search
case, the configuration, and validation results for the top cases. These top
cases are selected counterexamples; the aggregate search summary is more useful
for understanding how frequently imbalance occurs under the tested allocations.

Customize the block, path count, groups, and source prefixes:

```sh
python3 search_hashes.py \
  --router-prefix 10.20.0.0/16 --paths 4 \
  --patterns consecutive,subnets,random \
  --group 224.1.1.1 --group 239.1.2.3 \
  --search-sources 172.16.0.0/20 \
  --validation-sources 172.16.16.0/20 \
  --validation-sources 172.17.0.0/16 \
  --trials 2000 --seed 42 --json results.json
```

Use `--patterns consecutive` to test only consecutive allocations. Each
`--group` is evaluated against every generated router set. Validation uses the
same group as its search case. Source prefixes include network and broadcast
addresses, but exclude **224.0.0.0 through 239.254.254.254 inclusive**.
Groups must be within that exact range. A source prefix entirely within the
excluded range is rejected. Prefixes crossing its boundaries use only eligible
addresses. When the eligible population exceeds `--max-sources` (default 65,536),
it is sampled uniformly without replacement, rather than exhaustively enumerated.

Tied flows are counted separately. Winner percentages and deviations exclude
those flows; they describe only the unique winners. The local-information
tiebreaker is not simulated because its inputs are unspecified. Search summaries
exclude cases with ties, and top-case output reports ties explicitly. A case
where every flow ties has no defined deviation and sorts last.

To check vectorized hash compatibility against scalar implementations,
allocation constraints, tie handling, and the previously reported example:

```sh
python3 -m unittest -v test_search_hashes.py
```

## A 24-hour campaign

`run_hash_search.py` runs `search_hashes.py` in bounded batches and analyzes its
JSON output. Start with a short smoke run:

```sh
python3 run_hash_search.py --output smoke-results --max-batches 2
```

Run a 24-hour campaign in a persistent terminal session:

```sh
python3 run_hash_search.py --output campaign-results --hours 24
```

The driver cycles through a shuffled, reproducible matrix of path counts
2, 3, 4, 8, and 16; router blocks of /24 and /16; applicable allocation patterns;
and source prefixes of /24, /20, /16, and /0. A complete round contains 140
workload cells. Blocks and seeds change between batches. The /0 workload samples
uniformly across eligible IPv4 sources; other workloads use prefixes from
10.0.0.0/8, 172.16.0.0/12, and 192.0.0.0/16. Each batch uses one of five fixed
groups and one randomly selected valid group. The exact source/group range
restrictions above apply throughout.

Defaults are 100 router sets per batch, at most 65,536 sources, and the top
three cases for **each** hash. Additional-prefix checks use a /16 from a
different source pool and the same group. These prefixes are disjoint from
prefix-based search workloads; the /0 sampling workload can overlap them.
All additional-prefix checks are reported separately from search statistics.

Each completed batch updates:

- `report.md`: readable overall results, workload breakdowns, paired comparisons,
  and the largest counterexamples for each hash, with additional-prefix checks.
- `summary.json`: the same aggregate statistics and counterexamples for analysis.
- `state.json`: atomic checkpoints containing the configuration, histograms, and
  selected examples. Quantiles have less than 0.01 percentage point binning error;
  maxima and threshold counts are exact. This keeps memory bounded as the run grows.
- `batch-*.json.gz` and `batch-*.log`: compressed complete worker results and logs,
  including configurations and commands for reproduction. Disk use grows with
  completed batches.

Cases with ties are counted separately and excluded from aggregate deviation
and paired-comparison statistics. Results are separated by path count, router
block size, allocation pattern, and source prefix size. Interpret each workload
separately: pooling cases with different source counts can obscure differences.
The reported percentiles and comparisons are descriptive; the driver does not
assume that flows or repeated groups/router sets are independent samples.

At the deadline, the driver terminates any unfinished worker. Completed batches
are preserved. Ctrl-C also preserves completed batches. Resume with:

```sh
python3 run_hash_search.py --output campaign-results --resume --hours 24
```

`--hours` is an additional time budget for that invocation. Resume uses the
saved experiment settings and retries any unfinished batch. It requires the
same driver/search code and Python/NumPy versions, so changed experiments use
new output directories. Only one driver may use a directory at a time.

To customize a new campaign, use `--paths 3,4,8`, `--batch-trials 250`,
`--max-sources 65536`, `--top 5`, or `--seed 42`. Reports can be rebuilt from
the saved checkpoint without running searches:

```sh
python3 run_hash_search.py --output campaign-results --report-only
python3 -m unittest -v test_search_hashes.py test_run_hash_search.py
```

The campaign is a structured search, not exhaustive enumeration of router
combinations. The driver performs the arithmetic and bookkeeping; interpretation
and decisions about further experiments can use the reports and archived cases.
