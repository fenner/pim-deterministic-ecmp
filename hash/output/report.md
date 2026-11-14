# Hash search results

Completed batches: 21561

Deviations are percentage points from equal share. Quantiles have <0.01 pp binning error; maxima are exact. Cases with ties are excluded from deviation statistics. These are descriptive results; flows, groups, and router sets are not independent samples.

The overall mixture combines different workloads and source counts; use the strata for decisions.

| Hash | Cases | Cases with ties | Median | p95 | p99 | Max | >=5 pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| PIM hash | 4312200 | 0 | 0.40 | 4.55 | 6.51 | 25.00 | 154120 |
| Jenkins | 4312200 | 5303 | 0.97 | 5.07 | 7.03 | 15.49 | 216200 |

## Workloads

A /0 source workload samples uniformly from eligible IPv4 addresses. Other source prefixes are enumerated up to the configured cap. Router blocks and source prefixes vary between batches.

| Workload | Cases | PIM p95 | Jenkins p95 | PIM max | Jenkins max | PIM better | Jenkins better | Equal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| paths=16;router=/16;consecutive;sources=/0 | 30800 | 0.29 | 0.98 | 0.53 | 1.45 | 30428 | 327 | 20 |
| paths=16;router=/16;consecutive;sources=/16 | 30800 | 0.51 | 1.01 | 3.06 | 1.44 | 27475 | 3247 | 39 |
| paths=16;router=/16;consecutive;sources=/20 | 30800 | 1.31 | 1.29 | 4.25 | 2.54 | 16454 | 13301 | 1043 |
| paths=16;router=/16;consecutive;sources=/24 | 30800 | 4.68 | 4.68 | 9.38 | 8.59 | 13187 | 13120 | 4493 |
| paths=16;router=/16;random;sources=/0 | 30800 | 0.30 | 0.30 | 0.68 | 0.72 | 14044 | 15943 | 281 |
| paths=16;router=/16;random;sources=/16 | 30800 | 0.51 | 0.30 | 1.74 | 0.73 | 11898 | 18166 | 224 |
| paths=16;router=/16;random;sources=/20 | 30800 | 1.31 | 1.12 | 3.39 | 1.88 | 13432 | 16297 | 1037 |
| paths=16;router=/16;random;sources=/24 | 30800 | 4.68 | 4.68 | 9.38 | 8.59 | 12990 | 13134 | 4673 |
| paths=16;router=/16;strided;sources=/0 | 30800 | 0.31 | 0.28 | 0.87 | 2.98 | 12874 | 16885 | 239 |
| paths=16;router=/16;strided;sources=/16 | 30800 | 0.52 | 0.28 | 2.11 | 2.29 | 11188 | 18630 | 196 |
| paths=16;router=/16;strided;sources=/20 | 30800 | 1.31 | 1.12 | 3.64 | 2.08 | 13393 | 16220 | 1129 |
| paths=16;router=/16;strided;sources=/24 | 30800 | 4.68 | 4.68 | 10.55 | 8.59 | 12832 | 13321 | 4642 |
| paths=16;router=/16;subnets;sources=/0 | 30800 | 0.44 | 0.28 | 0.77 | 0.49 | 4958 | 25687 | 155 |
| paths=16;router=/16;subnets;sources=/16 | 30800 | 0.55 | 0.28 | 2.25 | 0.45 | 4489 | 26170 | 141 |
| paths=16;router=/16;subnets;sources=/20 | 30800 | 1.36 | 1.12 | 3.69 | 1.98 | 11892 | 17874 | 1034 |
| paths=16;router=/16;subnets;sources=/24 | 30800 | 4.68 | 4.68 | 8.20 | 8.20 | 12728 | 13459 | 4613 |
| paths=16;router=/24;consecutive;sources=/0 | 30800 | 0.29 | 0.52 | 0.53 | 0.71 | 30414 | 373 | 13 |
| paths=16;router=/24;consecutive;sources=/16 | 30800 | 0.49 | 0.52 | 1.29 | 0.69 | 27519 | 3231 | 50 |
| paths=16;router=/24;consecutive;sources=/20 | 30800 | 1.31 | 1.19 | 4.76 | 1.93 | 15748 | 13935 | 1117 |
| paths=16;router=/24;consecutive;sources=/24 | 30800 | 4.68 | 4.68 | 10.55 | 7.42 | 13083 | 13067 | 4650 |
| paths=16;router=/24;random;sources=/0 | 30800 | 0.31 | 1.34 | 0.62 | 2.66 | 30796 | 4 | 0 |
| paths=16;router=/24;random;sources=/16 | 30800 | 0.53 | 1.33 | 1.76 | 2.53 | 30383 | 412 | 5 |
| paths=16;router=/24;random;sources=/20 | 30800 | 1.31 | 1.70 | 3.34 | 3.88 | 24790 | 5500 | 510 |
| paths=16;router=/24;random;sources=/24 | 30800 | 4.68 | 4.68 | 8.98 | 9.77 | 14329 | 11973 | 4498 |
| paths=16;router=/24;strided;sources=/0 | 30800 | 0.30 | 0.86 | 0.55 | 1.19 | 29402 | 1354 | 44 |
| paths=16;router=/24;strided;sources=/16 | 30800 | 0.50 | 0.86 | 1.81 | 1.23 | 27215 | 3539 | 46 |
| paths=16;router=/24;strided;sources=/20 | 30800 | 1.31 | 1.36 | 3.25 | 2.29 | 19061 | 10825 | 914 |
| paths=16;router=/24;strided;sources=/24 | 30800 | 4.68 | 4.68 | 8.20 | 8.98 | 13332 | 12957 | 4511 |
| paths=2;router=/16;consecutive;sources=/0 | 30800 | 0.38 | 0.38 | 0.79 | 0.85 | 15258 | 15375 | 167 |
| paths=2;router=/16;consecutive;sources=/16 | 30800 | 0.39 | 0.38 | 4.26 | 0.80 | 17036 | 13635 | 129 |
| paths=2;router=/16;consecutive;sources=/20 | 30800 | 1.53 | 1.53 | 5.49 | 3.54 | 15810 | 14472 | 518 |
| paths=2;router=/16;consecutive;sources=/24 | 30800 | 6.25 | 6.25 | 15.23 | 12.50 | 14550 | 14136 | 2114 |
| paths=2;router=/16;random;sources=/0 | 30800 | 0.38 | 0.38 | 0.81 | 0.82 | 15301 | 15285 | 155 |
| paths=2;router=/16;random;sources=/16 | 30800 | 0.39 | 0.37 | 5.81 | 0.93 | 17119 | 13485 | 147 |
| paths=2;router=/16;random;sources=/20 | 30800 | 1.56 | 1.51 | 7.57 | 3.10 | 15732 | 14508 | 557 |
| paths=2;router=/16;random;sources=/24 | 30800 | 6.25 | 6.25 | 14.06 | 13.28 | 14272 | 14486 | 2042 |
| paths=2;router=/16;strided;sources=/0 | 30800 | 0.37 | 0.38 | 0.87 | 0.92 | 15325 | 15286 | 147 |
| paths=2;router=/16;strided;sources=/16 | 30800 | 0.39 | 0.38 | 2.62 | 0.90 | 17075 | 13535 | 143 |
| paths=2;router=/16;strided;sources=/20 | 30800 | 1.56 | 1.53 | 7.45 | 3.74 | 15700 | 14561 | 538 |
| paths=2;router=/16;strided;sources=/24 | 30800 | 6.25 | 6.25 | 15.62 | 12.89 | 14473 | 14240 | 2087 |
| paths=2;router=/16;subnets;sources=/0 | 30800 | 0.38 | 0.37 | 0.82 | 0.82 | 15333 | 15325 | 142 |
| paths=2;router=/16;subnets;sources=/16 | 30800 | 0.40 | 0.38 | 4.44 | 0.79 | 17716 | 12957 | 127 |
| paths=2;router=/16;subnets;sources=/20 | 30800 | 1.68 | 1.51 | 9.69 | 3.15 | 15487 | 14752 | 561 |
| paths=2;router=/16;subnets;sources=/24 | 30800 | 6.25 | 6.25 | 17.97 | 12.89 | 14406 | 14341 | 2053 |
| paths=2;router=/24;consecutive;sources=/0 | 31000 | 0.38 | 0.37 | 0.83 | 0.78 | 15410 | 15455 | 135 |
| paths=2;router=/24;consecutive;sources=/16 | 30800 | 0.38 | 0.38 | 3.80 | 0.88 | 16991 | 13669 | 140 |
| paths=2;router=/24;consecutive;sources=/20 | 30800 | 1.56 | 1.53 | 4.59 | 3.47 | 15548 | 14727 | 525 |
| paths=2;router=/24;consecutive;sources=/24 | 30800 | 6.25 | 6.25 | 14.45 | 13.67 | 14357 | 14246 | 2197 |
| paths=2;router=/24;random;sources=/0 | 30800 | 0.38 | 0.38 | 0.80 | 0.79 | 15495 | 15163 | 142 |
| paths=2;router=/24;random;sources=/16 | 30800 | 0.39 | 0.38 | 4.14 | 0.79 | 17173 | 13481 | 146 |
| paths=2;router=/24;random;sources=/20 | 30800 | 1.58 | 1.53 | 6.98 | 3.10 | 15536 | 14721 | 543 |
| paths=2;router=/24;random;sources=/24 | 30800 | 6.25 | 6.25 | 15.62 | 14.45 | 14475 | 14225 | 2100 |
| paths=2;router=/24;strided;sources=/0 | 30800 | 0.37 | 0.38 | 0.82 | 0.90 | 15617 | 15059 | 124 |
| paths=2;router=/24;strided;sources=/16 | 30800 | 0.39 | 0.38 | 3.38 | 0.83 | 17251 | 13419 | 130 |
| paths=2;router=/24;strided;sources=/20 | 30800 | 1.58 | 1.53 | 6.96 | 2.98 | 15695 | 14552 | 553 |
| paths=2;router=/24;strided;sources=/24 | 30800 | 6.25 | 6.25 | 25.00 | 13.28 | 14545 | 14166 | 2089 |
| paths=3;router=/16;consecutive;sources=/0 | 30800 | 0.46 | 4.13 | 2.07 | 4.61 | 30800 | 0 | 0 |
| paths=3;router=/16;consecutive;sources=/16 | 30800 | 0.52 | 4.13 | 4.48 | 4.58 | 30799 | 1 | 0 |
| paths=3;router=/16;consecutive;sources=/20 | 30800 | 1.79 | 5.01 | 7.41 | 6.70 | 30760 | 39 | 1 |
| paths=3;router=/16;consecutive;sources=/24 | 30800 | 6.90 | 9.11 | 14.32 | 15.49 | 20539 | 9553 | 708 |
| paths=3;router=/16;random;sources=/0 | 30800 | 0.46 | 0.44 | 4.69 | 4.24 | 15042 | 15594 | 65 |
| paths=3;router=/16;random;sources=/16 | 30800 | 0.51 | 0.44 | 4.22 | 4.26 | 16605 | 14030 | 73 |
| paths=3;router=/16;random;sources=/20 | 30800 | 1.81 | 1.74 | 6.45 | 4.06 | 15677 | 14900 | 219 |
| paths=3;router=/16;random;sources=/24 | 30800 | 6.90 | 6.90 | 17.06 | 14.71 | 14928 | 14960 | 912 |
| paths=3;router=/16;strided;sources=/0 | 30800 | 0.45 | 0.43 | 2.49 | 5.62 | 14887 | 15775 | 54 |
| paths=3;router=/16;strided;sources=/16 | 30800 | 0.52 | 0.43 | 4.72 | 5.98 | 16572 | 14089 | 44 |
| paths=3;router=/16;strided;sources=/20 | 30800 | 1.82 | 1.74 | 10.59 | 5.48 | 15799 | 14776 | 223 |
| paths=3;router=/16;strided;sources=/24 | 30800 | 6.90 | 6.90 | 15.49 | 15.10 | 15059 | 14779 | 962 |
| paths=3;router=/16;subnets;sources=/0 | 30800 | 0.62 | 0.44 | 4.17 | 0.95 | 13492 | 17258 | 50 |
| paths=3;router=/16;subnets;sources=/16 | 30800 | 0.74 | 0.45 | 5.63 | 0.94 | 15128 | 15626 | 46 |
| paths=3;router=/16;subnets;sources=/20 | 30800 | 2.04 | 1.74 | 10.38 | 3.61 | 15058 | 15536 | 206 |
| paths=3;router=/16;subnets;sources=/24 | 30800 | 7.16 | 6.90 | 14.71 | 13.15 | 14931 | 14948 | 921 |
| paths=3;router=/24;consecutive;sources=/0 | 30800 | 0.47 | 4.13 | 3.28 | 4.55 | 30800 | 0 | 0 |
| paths=3;router=/24;consecutive;sources=/16 | 30800 | 0.52 | 4.13 | 2.85 | 4.53 | 30800 | 0 | 0 |
| paths=3;router=/24;consecutive;sources=/20 | 30800 | 1.77 | 5.01 | 4.99 | 6.77 | 30734 | 65 | 1 |
| paths=3;router=/24;consecutive;sources=/24 | 30800 | 6.90 | 8.85 | 14.32 | 15.10 | 20553 | 9554 | 693 |
| paths=3;router=/24;random;sources=/0 | 30800 | 0.47 | 3.81 | 3.38 | 7.00 | 29589 | 1204 | 7 |
| paths=3;router=/24;random;sources=/16 | 30800 | 0.52 | 3.80 | 5.34 | 7.03 | 29656 | 1137 | 7 |
| paths=3;router=/24;random;sources=/20 | 30800 | 1.79 | 4.06 | 7.71 | 8.17 | 24051 | 6634 | 115 |
| paths=3;router=/24;random;sources=/24 | 30800 | 6.90 | 7.68 | 15.10 | 14.71 | 16379 | 13541 | 880 |
| paths=3;router=/24;strided;sources=/0 | 30800 | 0.47 | 3.86 | 3.60 | 6.21 | 26682 | 4108 | 10 |
| paths=3;router=/24;strided;sources=/16 | 30800 | 0.54 | 3.86 | 3.44 | 6.11 | 27081 | 3703 | 16 |
| paths=3;router=/24;strided;sources=/20 | 30800 | 1.84 | 3.97 | 7.94 | 7.36 | 20543 | 10074 | 183 |
| paths=3;router=/24;strided;sources=/24 | 30800 | 6.90 | 7.29 | 14.58 | 14.32 | 15927 | 13963 | 910 |
| paths=4;router=/16;consecutive;sources=/0 | 30800 | 0.46 | 2.61 | 1.46 | 5.04 | 30716 | 83 | 1 |
| paths=4;router=/16;consecutive;sources=/16 | 30800 | 0.53 | 2.61 | 4.81 | 5.02 | 30720 | 79 | 1 |
| paths=4;router=/16;consecutive;sources=/20 | 30800 | 1.75 | 3.75 | 5.98 | 6.42 | 30537 | 251 | 12 |
| paths=4;router=/16;consecutive;sources=/24 | 30800 | 6.64 | 8.20 | 18.36 | 14.84 | 19498 | 9526 | 1776 |
| paths=4;router=/16;random;sources=/0 | 30800 | 0.45 | 0.43 | 3.38 | 2.40 | 14719 | 15832 | 111 |
| paths=4;router=/16;random;sources=/16 | 30800 | 0.52 | 0.43 | 3.89 | 2.33 | 16114 | 14458 | 108 |
| paths=4;router=/16;random;sources=/20 | 30800 | 1.75 | 1.68 | 7.13 | 3.30 | 15487 | 14772 | 534 |
| paths=4;router=/16;random;sources=/24 | 30800 | 6.64 | 6.64 | 13.28 | 12.11 | 14306 | 14317 | 2177 |
| paths=4;router=/16;strided;sources=/0 | 30800 | 0.45 | 0.42 | 2.59 | 2.59 | 14441 | 16050 | 119 |
| paths=4;router=/16;strided;sources=/16 | 30800 | 0.52 | 0.42 | 3.20 | 4.30 | 15993 | 14547 | 119 |
| paths=4;router=/16;strided;sources=/20 | 30800 | 1.78 | 1.68 | 6.20 | 3.20 | 15411 | 14855 | 528 |
| paths=4;router=/16;strided;sources=/24 | 30800 | 6.64 | 6.64 | 18.75 | 12.11 | 14337 | 14269 | 2194 |
| paths=4;router=/16;subnets;sources=/0 | 30800 | 0.65 | 0.43 | 3.20 | 0.86 | 12306 | 18382 | 112 |
| paths=4;router=/16;subnets;sources=/16 | 30800 | 0.72 | 0.43 | 4.98 | 0.82 | 13506 | 17175 | 119 |
| paths=4;router=/16;subnets;sources=/20 | 30800 | 2.00 | 1.68 | 7.76 | 3.32 | 14358 | 15963 | 479 |
| paths=4;router=/16;subnets;sources=/24 | 30800 | 6.64 | 6.64 | 14.06 | 12.89 | 14100 | 14525 | 2175 |
| paths=4;router=/24;consecutive;sources=/0 | 30800 | 0.46 | 2.60 | 1.28 | 2.99 | 30800 | 0 | 0 |
| paths=4;router=/24;consecutive;sources=/16 | 30800 | 0.53 | 2.60 | 3.30 | 3.02 | 30779 | 21 | 0 |
| paths=4;router=/24;consecutive;sources=/20 | 30800 | 1.75 | 3.71 | 6.88 | 5.18 | 30597 | 193 | 10 |
| paths=4;router=/24;consecutive;sources=/24 | 30800 | 6.64 | 8.20 | 15.62 | 14.06 | 19620 | 9475 | 1705 |
| paths=4;router=/24;random;sources=/0 | 30800 | 0.47 | 3.64 | 2.76 | 8.39 | 30418 | 378 | 4 |
| paths=4;router=/24;random;sources=/16 | 30800 | 0.54 | 3.64 | 4.24 | 9.35 | 30383 | 413 | 4 |
| paths=4;router=/24;random;sources=/20 | 30800 | 1.78 | 3.95 | 6.08 | 8.59 | 26014 | 4601 | 185 |
| paths=4;router=/24;random;sources=/24 | 30800 | 6.64 | 7.42 | 13.28 | 14.45 | 16621 | 12180 | 1999 |
| paths=4;router=/24;strided;sources=/0 | 30800 | 0.47 | 1.75 | 2.08 | 2.94 | 26924 | 3832 | 44 |
| paths=4;router=/24;strided;sources=/16 | 30800 | 0.54 | 1.76 | 4.16 | 2.77 | 27072 | 3699 | 29 |
| paths=4;router=/24;strided;sources=/20 | 30800 | 1.80 | 2.63 | 6.13 | 4.83 | 21634 | 8805 | 361 |
| paths=4;router=/24;strided;sources=/24 | 30800 | 6.64 | 7.03 | 14.84 | 14.06 | 15274 | 13511 | 2015 |
| paths=8;router=/16;consecutive;sources=/0 | 30800 | 0.39 | 3.07 | 0.81 | 3.40 | 30800 | 0 | 0 |
| paths=8;router=/16;consecutive;sources=/16 | 30800 | 0.50 | 3.07 | 3.06 | 3.49 | 30799 | 1 | 0 |
| paths=8;router=/16;consecutive;sources=/20 | 30800 | 1.56 | 3.90 | 4.98 | 5.22 | 30725 | 70 | 5 |
| paths=8;router=/16;consecutive;sources=/24 | 30800 | 5.85 | 7.42 | 11.33 | 12.11 | 20918 | 7576 | 2306 |
| paths=8;router=/16;random;sources=/0 | 30800 | 0.38 | 0.38 | 1.51 | 1.42 | 14402 | 15917 | 207 |
| paths=8;router=/16;random;sources=/16 | 30800 | 0.53 | 0.38 | 3.21 | 1.27 | 14609 | 15723 | 179 |
| paths=8;router=/16;random;sources=/20 | 30800 | 1.56 | 1.41 | 4.71 | 2.32 | 14752 | 15277 | 752 |
| paths=8;router=/16;random;sources=/24 | 30800 | 5.85 | 5.46 | 12.11 | 9.77 | 13672 | 14012 | 3115 |
| paths=8;router=/16;strided;sources=/0 | 30800 | 0.39 | 0.35 | 1.44 | 2.19 | 13706 | 16545 | 203 |
| paths=8;router=/16;strided;sources=/16 | 30800 | 0.53 | 0.35 | 2.76 | 2.84 | 13906 | 16378 | 140 |
| paths=8;router=/16;strided;sources=/20 | 30800 | 1.56 | 1.41 | 5.05 | 4.10 | 14527 | 15490 | 764 |
| paths=8;router=/16;strided;sources=/24 | 30800 | 5.85 | 5.46 | 11.33 | 10.16 | 13820 | 13858 | 3120 |
| paths=8;router=/16;subnets;sources=/0 | 30800 | 0.60 | 0.36 | 1.64 | 0.65 | 8913 | 21762 | 125 |
| paths=8;router=/16;subnets;sources=/16 | 30800 | 0.69 | 0.36 | 3.03 | 0.59 | 8890 | 21791 | 119 |
| paths=8;router=/16;subnets;sources=/20 | 30800 | 1.63 | 1.41 | 5.76 | 2.37 | 13124 | 16952 | 724 |
| paths=8;router=/16;subnets;sources=/24 | 30800 | 5.85 | 5.46 | 12.89 | 9.38 | 13637 | 14107 | 3056 |
| paths=8;router=/24;consecutive;sources=/0 | 30800 | 0.38 | 3.07 | 0.82 | 3.39 | 30800 | 0 | 0 |
| paths=8;router=/24;consecutive;sources=/16 | 30800 | 0.51 | 3.07 | 2.11 | 3.36 | 30800 | 0 | 0 |
| paths=8;router=/24;consecutive;sources=/20 | 30800 | 1.56 | 3.90 | 6.15 | 5.42 | 30752 | 45 | 3 |
| paths=8;router=/24;consecutive;sources=/24 | 30800 | 5.85 | 7.42 | 10.94 | 11.72 | 20922 | 7627 | 2251 |
| paths=8;router=/24;random;sources=/0 | 30800 | 0.40 | 2.64 | 1.12 | 6.32 | 30769 | 31 | 0 |
| paths=8;router=/24;random;sources=/16 | 30800 | 0.53 | 2.65 | 2.34 | 5.93 | 30657 | 143 | 0 |
| paths=8;router=/24;random;sources=/20 | 30800 | 1.56 | 2.95 | 4.30 | 6.91 | 27439 | 3148 | 213 |
| paths=8;router=/24;random;sources=/24 | 30800 | 5.46 | 6.25 | 10.55 | 12.11 | 16210 | 11689 | 2901 |
| paths=8;router=/24;strided;sources=/0 | 30800 | 0.39 | 1.57 | 1.06 | 3.23 | 29094 | 1678 | 28 |
| paths=8;router=/24;strided;sources=/16 | 30800 | 0.53 | 1.57 | 1.88 | 3.28 | 28299 | 2469 | 32 |
| paths=8;router=/24;strided;sources=/20 | 30800 | 1.58 | 2.17 | 4.35 | 4.93 | 21131 | 9157 | 512 |
| paths=8;router=/24;strided;sources=/24 | 30800 | 5.85 | 5.85 | 10.94 | 10.16 | 14766 | 13031 | 3003 |

## Selected counterexamples

These examples were selected for large deviations; additional-prefix checks are not included in the aggregate search statistics. Each batch validates its top cases for both hashes.

### PIM hash

- Batch 15496, 10.66.135.0/24, group 237.229.18.77, routers 10.128.139.76, 10.128.139.184
  - Search: PIM 25.00 pp, Jenkins 3.52 pp; ties 0/0
  - Additional prefix 172.31.0.0/16: PIM 0.21 pp, Jenkins 0.05 pp; ties 0/0
- Batch 8459, 172.31.121.0/24, group 239.254.254.254, routers 10.66.3.67, 10.66.59.124, 10.66.115.181, 10.66.171.238
  - Search: PIM 18.75 pp, Jenkins 3.91 pp; ties 0/0
  - Additional prefix 192.0.0.0/16: PIM 0.32 pp, Jenkins 0.33 pp; ties 0/0
- Batch 20633, 172.18.59.0/24, group 224.0.0.0, routers 10.145.239.172, 10.145.239.173, 10.145.239.174, 10.145.239.175
  - Search: PIM 18.36 pp, Jenkins 4.30 pp; ties 0/0
  - Additional prefix 192.0.0.0/16: PIM 0.23 pp, Jenkins 2.36 pp; ties 0/0

### Jenkins

- Batch 18902, 172.20.220.0/24, group 237.115.108.59, routers 10.196.153.171, 10.196.153.172, 10.196.153.173
  - Search: PIM 2.47 pp, Jenkins 15.49 pp; ties 0/0
  - Additional prefix 192.0.0.0/16: PIM 0.15 pp, Jenkins 3.76 pp; ties 0/0
- Batch 18137, 172.26.205.0/24, group 224.0.0.1, routers 10.191.67.214, 10.191.67.215, 10.191.67.216
  - Search: PIM 2.47 pp, Jenkins 15.36 pp; ties 0/0
  - Additional prefix 192.0.0.0/16: PIM 0.28 pp, Jenkins 3.92 pp; ties 0/0
- Batch 15955, 172.19.38.0/24, group 234.236.32.105, routers 10.3.204.95, 10.3.204.96, 10.3.204.97
  - Search: PIM 4.43 pp, Jenkins 15.10 pp; ties 0/0
  - Additional prefix 192.0.0.0/16: PIM 0.13 pp, Jenkins 3.66 pp; ties 0/0

