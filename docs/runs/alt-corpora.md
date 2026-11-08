# Alt corpora

The run `alt` (`python -m tests.corpus`) on alt: constricter 0.4.5.dev41+g28434383f.d20261107
(`19a3e9c8dc16`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 8 minutes. Timings don't compare across machines, nor their seconds across runs, taken
beside the other steps: their instructions do.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus         | Version | constricter | Files |      `LVA001` |      `LVA002` |     `LVA004` |   `LVA005` |  `LVA006` | `LVA009` |  Total |
| -------------- | ------- | ----------- | ----: | ------------: | ------------: | -----------: | ---------: | --------: | -------: | -----: |
| requests       | 2.34.2  | alt+dev     |    19 |           305 |            62 |           32 |         10 |         0 |        0 |    409 |
| rich           | 15.0.0  | alt+dev     |   100 |         1,612 |           258 |          308 |          6 |         7 |        0 |  2,191 |
| trio           | 0.34.0  | alt+dev     |   144 |         2,540 |           245 |          199 |         39 |         2 |        0 |  3,025 |
| urllib3        | 2.8.0   | alt+dev     |    36 |           443 |            57 |          134 |          5 |         1 |        2 |    642 |
| langchain-core | 1.7.0   | alt+dev     |   182 |         2,872 |           632 |          226 |        182 |        10 |        0 |  3,922 |
| sqlmodel       | 0.0.48  | alt+dev     |    16 |            86 |            18 |           21 |         17 |         0 |        0 |    142 |
| marshmallow    | 4.3.1   | alt+dev     |    14 |           147 |            50 |          105 |         20 |         3 |        0 |    325 |
| **Total**      |         | alt+dev     |   511 | 8,005 (75.1%) | 1,322 (12.4%) | 1,025 (9.6%) | 279 (2.6%) | 23 (0.2%) | 2 (0.0%) | 10,656 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus         | constricter |  `relaxed` |      `strict` |  `constrict` | `suffocate` |         Fixed |      Likely |       Guessed | Broken | Left | Left, likely |
| -------------- | ----------- | ---------: | ------------: | -----------: | ----------: | ------------: | ----------: | ------------: | -----: | ---: | -----------: |
| requests       | alt+dev     |    0 / 399 |      337 / 72 |     399 / 10 |     409 / 0 |    96 (23.5%) |    9 (2.2%) |     17 (4.2%) |      0 |    0 |            0 |
| rich           | alt+dev     |  0 / 2,178 |   1,920 / 271 |   2,178 / 13 |   2,191 / 0 | 1,021 (46.6%) | 307 (14.0%) |   434 (19.8%) |      0 |    0 |            0 |
| trio           | alt+dev     |  0 / 2,984 |   2,739 / 286 |   2,984 / 41 |   3,025 / 0 | 1,102 (36.4%) |  275 (9.1%) |   336 (11.1%) |      0 |    0 |            0 |
| urllib3        | alt+dev     |    0 / 636 |      577 / 65 |      636 / 6 |     642 / 0 |   259 (40.3%) |   42 (6.5%) |    79 (12.3%) |      0 |    0 |            0 |
| langchain-core | alt+dev     |  0 / 3,730 |   3,098 / 824 |  3,730 / 192 |   3,922 / 0 | 1,702 (43.4%) |  204 (5.2%) |    307 (7.8%) |      0 |    0 |            0 |
| sqlmodel       | alt+dev     |    0 / 125 |      107 / 35 |     125 / 17 |     142 / 0 |     11 (7.7%) |    5 (3.5%) |     10 (7.0%) |      0 |    0 |            0 |
| marshmallow    | alt+dev     |    0 / 302 |      252 / 73 |     302 / 23 |     325 / 0 |    51 (15.7%) |    5 (1.5%) |    52 (16.0%) |      0 |    0 |            0 |
| **Total**      | alt+dev     | 0 / 10,354 | 9,030 / 1,626 | 10,354 / 302 |  10,656 / 0 | 4,242 (39.8%) |  847 (7.9%) | 1,235 (11.6%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus         | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| -------------- | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| requests       | alt+dev     |             28.6% |         45.8% |            47.4% |                  48.8% | +17.2 pts, 24.1% of untyped | +20.2 pts, 28.3% of untyped |
| rich           | alt+dev     |             13.4% |         54.0% |            66.2% |                  71.3% | +40.6 pts, 46.9% of untyped | +57.8 pts, 66.8% of untyped |
| trio           | alt+dev     |             15.0% |         46.2% |            54.0% |                  55.8% | +31.2 pts, 36.7% of untyped | +40.7 pts, 47.9% of untyped |
| urllib3        | alt+dev     |             25.8% |         56.1% |            61.1% |                  65.4% | +30.3 pts, 40.9% of untyped | +39.5 pts, 53.3% of untyped |
| langchain-core | alt+dev     |             20.6% |         56.8% |            61.2% |                  63.4% | +36.2 pts, 45.6% of untyped | +42.8 pts, 53.9% of untyped |
| sqlmodel       | alt+dev     |             23.8% |         30.5% |            33.5% |                  36.6% |   +6.7 pts, 8.8% of untyped | +12.8 pts, 16.8% of untyped |
| marshmallow    | alt+dev     |             20.1% |         33.6% |            34.9% |                  47.4% | +13.5 pts, 16.9% of untyped | +27.2 pts, 34.1% of untyped |
| **Total**      | alt+dev     |             18.4% |         51.8% |            58.4% |                  61.5% | +33.4 pts, 40.9% of untyped | +43.1 pts, 52.8% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus         | fix                | fixed | certain | likely | guess | broken | left | typed | bindings | seconds |
| -------------- | ------------------ | ----: | ------: | -----: | ----: | -----: | ---: | ----: | -------: | ------: |
| requests       | certain            |    96 |      96 |        |       |      0 |    0 |   256 |      559 |     0.9 |
| requests       | likely             |   105 |      96 |      9 |       |      0 |    0 |   265 |      559 |     0.9 |
| requests       | unsafe             |   113 |      96 |      9 |     8 |      0 |    0 |   273 |      559 |     0.9 |
| requests       | infer-basedpyright |   221 |      96 |     16 |   109 |      0 |    0 |   381 |      559 |     4.0 |
| requests       | infer-ty           |   223 |      96 |     13 |   114 |      0 |    0 |   383 |      559 |     1.4 |
| requests       | infer-pyrefly      |   146 |      96 |     10 |    40 |      0 |    0 |   306 |      559 |     1.3 |
| requests       | infer-trace        |   113 |      96 |      9 |     8 |      0 |    0 |   273 |      559 |     0.7 |
| rich           | certain            | 1,021 |   1,021 |        |       |      0 |    1 | 1,359 |    2,516 |     1.7 |
| rich           | likely             | 1,328 |   1,033 |    295 |       |      0 |    0 | 1,666 |    2,516 |     2.2 |
| rich           | unsafe             | 1,455 |   1,022 |    293 |   140 |      0 |    0 | 1,793 |    2,516 |     2.0 |
| rich           | infer-basedpyright | 1,774 |   1,021 |    296 |   457 |      0 |    0 | 2,112 |    2,516 |    11.8 |
| rich           | infer-ty           | 1,617 |   1,021 |    299 |   297 |      0 |    1 | 1,955 |    2,516 |     2.6 |
| rich           | infer-pyrefly      | 1,657 |   1,021 |    298 |   338 |      0 |    1 | 1,995 |    2,516 |     4.4 |
| rich           | infer-trace        | 1,455 |   1,022 |    293 |   140 |      0 |    0 | 1,793 |    2,516 |     3.2 |
| trio           | certain            | 1,102 |   1,102 |        |       |      0 |    4 | 1,633 |    3,531 |     2.5 |
| trio           | likely             | 1,377 |   1,110 |    267 |       |      0 |    0 | 1,908 |    3,531 |     4.3 |
| trio           | unsafe             | 1,438 |   1,107 |    267 |    64 |      0 |    0 | 1,969 |    3,531 |     8.4 |
| trio           | infer-basedpyright | 1,690 |   1,103 |    273 |   314 |      0 |    0 | 2,221 |    3,531 |    13.2 |
| trio           | infer-ty           | 1,786 |   1,102 |    273 |   411 |      0 |    8 | 2,317 |    3,531 |     6.7 |
| trio           | infer-pyrefly      | 1,602 |   1,102 |    270 |   230 |      0 |    7 | 2,133 |    3,531 |     6.4 |
| trio           | infer-trace        | 1,438 |   1,107 |    267 |    64 |      0 |    0 | 1,969 |    3,531 |     3.7 |
| urllib3        | certain            |   259 |     259 |        |       |      0 |    0 |   480 |      855 |     2.1 |
| urllib3        | likely             |   301 |     261 |     40 |       |      0 |    0 |   522 |      855 |     1.3 |
| urllib3        | unsafe             |   338 |     259 |     40 |    39 |      0 |    0 |   559 |      855 |     1.5 |
| urllib3        | infer-basedpyright |   412 |     259 |     40 |   113 |      0 |    1 |   633 |      855 |     6.5 |
| urllib3        | infer-ty           |   416 |     259 |     40 |   117 |      0 |    0 |   637 |      855 |     2.3 |
| urllib3        | infer-pyrefly      |   411 |     259 |     40 |   112 |      0 |    0 |   632 |      855 |     2.5 |
| urllib3        | infer-trace        |   338 |     259 |     40 |    39 |      0 |    0 |   559 |      855 |     1.5 |
| langchain-core | certain            | 1,702 |   1,702 |        |       |      0 |    0 | 2,668 |    4,696 |     4.5 |
| langchain-core | likely             | 1,906 |   1,706 |    200 |       |      0 |    0 | 2,872 |    4,696 |    10.1 |
| langchain-core | unsafe             | 2,009 |   1,702 |    200 |   107 |      0 |    0 | 2,975 |    4,696 |     9.7 |
| langchain-core | infer-basedpyright | 2,209 |   1,702 |    211 |   296 |      0 |    0 | 3,175 |    4,696 |    22.2 |
| langchain-core | infer-ty           | 2,246 |   1,702 |    213 |   331 |      0 |    0 | 3,212 |    4,696 |     8.7 |
| langchain-core | infer-pyrefly      | 2,359 |   1,702 |    218 |   439 |      0 |    0 | 3,325 |    4,696 |     8.1 |
| langchain-core | infer-trace        | 2,009 |   1,702 |    200 |   107 |      0 |    0 | 2,975 |    4,696 |     3.8 |
| sqlmodel       | certain            |    11 |      11 |        |       |      0 |    0 |    50 |      164 |     0.7 |
| sqlmodel       | likely             |    16 |      11 |      5 |       |      0 |    0 |    55 |      164 |     1.1 |
| sqlmodel       | unsafe             |    21 |      11 |      5 |     5 |      0 |    0 |    60 |      164 |     2.8 |
| sqlmodel       | infer-basedpyright |    23 |      11 |      5 |     7 |      0 |    0 |    62 |      164 |     5.2 |
| sqlmodel       | infer-ty           |    23 |      11 |      5 |     7 |      0 |    0 |    62 |      164 |     3.3 |
| sqlmodel       | infer-pyrefly      |    30 |      11 |      5 |    14 |      0 |    0 |    69 |      164 |     2.7 |
| sqlmodel       | infer-trace        |    21 |      11 |      5 |     5 |      0 |    0 |    60 |      164 |     1.7 |
| marshmallow    | certain            |    51 |      51 |        |       |      0 |    0 |   127 |      378 |     0.5 |
| marshmallow    | likely             |    56 |      51 |      5 |       |      0 |    0 |   132 |      378 |     0.6 |
| marshmallow    | unsafe             |   103 |      51 |      5 |    47 |      0 |    0 |   179 |      378 |     0.7 |
| marshmallow    | infer-basedpyright |   120 |      51 |      5 |    64 |      0 |    0 |   196 |      378 |     2.9 |
| marshmallow    | infer-ty           |   118 |      51 |      5 |    62 |      0 |    0 |   194 |      378 |     1.1 |
| marshmallow    | infer-pyrefly      |   119 |      51 |      5 |    63 |      0 |    0 |   195 |      378 |     1.5 |
| marshmallow    | infer-trace        |   103 |      51 |      5 |    47 |      0 |    0 |   179 |      378 |     0.6 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms        | fixed | certain | likely | guess |
| ------------------ | ----------------- | ----: | ------: | -----: | ----: |
| certain            | literal           |   710 |     710 |        |       |
| certain            | call              |   473 |     473 |        |       |
| certain            | method            |   363 |     363 |        |       |
| certain            | stdlib            |   325 |     325 |        |       |
| certain            | copy+loop         |   231 |     231 |        |       |
| certain            | builtin           |   131 |     131 |        |       |
| certain            | loop              |   127 |     127 |        |       |
| certain            | copy+unpack       |   111 |     111 |        |       |
| certain            | call+unpack       |   107 |     107 |        |       |
| certain            | attribute+loop    |    85 |      85 |        |       |
| certain            | container+literal |    85 |      85 |        |       |
| certain            | attribute         |    76 |      76 |        |       |
| likely             | literal           |   710 |     710 |        |       |
| likely             | constructor       |   549 |       2 |    547 |       |
| likely             | call              |   479 |     474 |      5 |       |
| likely             | method            |   397 |     364 |     33 |       |
| likely             | stdlib            |   325 |     325 |        |       |
| likely             | copy+loop         |   265 |     231 |     34 |       |
| likely             | builtin           |   131 |     131 |        |       |
| likely             | loop              |   127 |     127 |        |       |
| likely             | copy+unpack       |   113 |     111 |      2 |       |
| likely             | call+unpack       |   107 |     107 |        |       |
| likely             | attribute         |    97 |      76 |     21 |       |
| likely             | attribute+loop    |    88 |      87 |      1 |       |
| unsafe             | literal           |   710 |     710 |        |       |
| unsafe             | constructor       |   548 |       2 |    546 |       |
| unsafe             | call              |   478 |     473 |      5 |       |
| unsafe             | method            |   397 |     364 |     33 |       |
| unsafe             | stdlib            |   330 |     325 |        |     5 |
| unsafe             | copy+loop         |   265 |     231 |     34 |       |
| unsafe             | builtin           |   131 |     131 |        |       |
| unsafe             | loop              |   127 |     127 |        |       |
| unsafe             | copy+unpack       |   113 |     111 |      2 |       |
| unsafe             | call+unpack       |   107 |     107 |        |       |
| unsafe             | alias             |   104 |      73 |        |    31 |
| unsafe             | attribute         |    97 |      76 |     21 |       |
| infer-basedpyright | checker           |   826 |         |        |   826 |
| infer-basedpyright | literal           |   710 |     710 |        |       |
| infer-basedpyright | constructor       |   545 |       2 |    543 |       |
| infer-basedpyright | call              |   479 |     473 |      6 |       |
| infer-basedpyright | method            |   407 |     363 |     44 |       |
| infer-basedpyright | stdlib            |   329 |     324 |        |     5 |
| infer-basedpyright | copy+loop         |   278 |     231 |     47 |       |
| infer-basedpyright | builtin           |   131 |     131 |        |       |
| infer-basedpyright | loop              |   127 |     127 |        |       |
| infer-basedpyright | copy+unpack       |   113 |     111 |      2 |       |
| infer-basedpyright | call+unpack       |   111 |     107 |        |     4 |
| infer-basedpyright | alias             |   104 |      73 |        |    31 |
| infer-ty           | checker           |   847 |         |        |   847 |
| infer-ty           | literal           |   710 |     710 |        |       |
| infer-ty           | constructor       |   547 |       2 |    545 |       |
| infer-ty           | call              |   478 |     473 |      5 |       |
| infer-ty           | method            |   410 |     363 |     47 |       |
| infer-ty           | stdlib            |   329 |     324 |        |     5 |
| infer-ty           | copy+loop         |   274 |     231 |     43 |       |
| infer-ty           | builtin           |   131 |     131 |        |       |
| infer-ty           | loop              |   127 |     127 |        |       |
| infer-ty           | copy+unpack       |   113 |     111 |      2 |       |
| infer-ty           | call+unpack       |   107 |     107 |        |       |
| infer-ty           | alias             |   104 |      73 |        |    31 |
| infer-pyrefly      | checker           |   740 |         |        |   740 |
| infer-pyrefly      | literal           |   710 |     710 |        |       |
| infer-pyrefly      | constructor       |   543 |       2 |    541 |       |
| infer-pyrefly      | call              |   478 |     473 |      5 |       |
| infer-pyrefly      | method            |   405 |     363 |     42 |       |
| infer-pyrefly      | stdlib            |   329 |     324 |        |     5 |
| infer-pyrefly      | copy+loop         |   272 |     231 |     41 |       |
| infer-pyrefly      | builtin           |   131 |     131 |        |       |
| infer-pyrefly      | loop              |   127 |     127 |        |       |
| infer-pyrefly      | copy+unpack       |   121 |     111 |     10 |       |
| infer-pyrefly      | call+unpack       |   107 |     107 |        |       |
| infer-pyrefly      | alias             |   104 |      73 |        |    31 |
| infer-trace        | literal           |   710 |     710 |        |       |
| infer-trace        | constructor       |   548 |       2 |    546 |       |
| infer-trace        | call              |   478 |     473 |      5 |       |
| infer-trace        | method            |   397 |     364 |     33 |       |
| infer-trace        | stdlib            |   330 |     325 |        |     5 |
| infer-trace        | copy+loop         |   265 |     231 |     34 |       |
| infer-trace        | builtin           |   131 |     131 |        |       |
| infer-trace        | loop              |   127 |     127 |        |       |
| infer-trace        | copy+unpack       |   113 |     111 |      2 |       |
| infer-trace        | call+unpack       |   107 |     107 |        |       |
| infer-trace        | alias             |   104 |      73 |        |    31 |
| infer-trace        | attribute         |    97 |      76 |     21 |       |
| infer-union        | literal           |   710 |     710 |        |       |
| infer-union        | agreed+checker    |   688 |         |    688 |       |
| infer-union        | checker           |   639 |         |        |   639 |
| infer-union        | constructor       |   543 |       2 |    541 |       |
| infer-union        | call              |   479 |     473 |      6 |       |
| infer-union        | method            |   411 |     363 |     48 |       |
| infer-union        | stdlib            |   329 |     324 |        |     5 |
| infer-union        | copy+loop         |   283 |     231 |     52 |       |
| infer-union        | builtin           |   131 |     131 |        |       |
| infer-union        | loop              |   127 |     127 |        |       |
| infer-union        | copy+unpack       |   121 |     111 |     10 |       |
| infer-union        | call+unpack       |   111 |     107 |        |     4 |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus         | untyped | guessed | unfixed | unparsed |
| -------------- | ------: | ------: | ------: | -------: |
| requests       |     399 |      17 |     286 |        0 |
| rich           |   2,178 |     433 |     724 |        0 |
| trio           |   2,984 |     329 |   1,553 |        0 |
| urllib3        |     634 |      79 |     296 |        0 |
| langchain-core |   3,730 |     307 |   1,721 |        0 |
| sqlmodel       |     125 |      10 |     104 |        0 |
| marshmallow    |     302 |      52 |     199 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus         | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by | beside other steps |
| -------------- | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: | -----------------: |
| requests       |    4 |        0.44 |      0.47 |    1 |                         4.6 |       5.9 | hyperfine |                yes |
| rich           |    4 |        3.08 |      2.32 |    1 |                        23.6 |      25.2 | hyperfine |                yes |
| trio           |    4 |        3.22 |      2.05 |    1 |                        30.9 |      32.4 | hyperfine |                yes |
| urllib3        |    4 |        0.87 |      0.55 |    1 |                         8.0 |       9.4 | hyperfine |                yes |
| langchain-core |    4 |        5.99 |      2.28 |    1 |                        49.1 |      43.1 | hyperfine |                yes |
| sqlmodel       |    4 |         0.7 |      0.95 |    1 |                         6.5 |       9.3 | hyperfine |                yes |
| marshmallow    |    4 |        0.38 |       0.5 |    1 |                         3.6 |       4.7 | hyperfine |                yes |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus         | tier                |  told |  held | differed | resting on the trace |                                                               tests | seconds | untraced |
| -------------- | ------------------- | ----: | ----: | -------: | -------------------: | ------------------------------------------------------------------: | ------: | -------: |
| requests       |                     |       |       |          |                    0 |                      617 passed, 15 skipped, 1 xpassed, 18 warnings |    23.1 |     24.1 |
| requests       | certain             |    64 |    63 |        1 |                      |                                                                     |         |          |
| requests       | likely              |     8 |     8 |        0 |                      |                                                                     |         |          |
| requests       | guess               |     5 |     5 |        0 |                      |                                                                     |         |          |
| requests       | infer-union certain |    64 |    63 |        1 |                      |                                                                     |         |          |
| requests       | infer-union likely  |    90 |    89 |        1 |                      |                                                                     |         |          |
| requests       | infer-union guess   |    35 |    35 |        0 |                      |                                                                     |         |          |
| rich           |                     |       |       |          |                    0 |                                    8 failed, 948 passed, 25 skipped |     8.5 |      7.0 |
| rich           | certain             |   810 |   810 |        0 |                      |                                                                     |         |          |
| rich           | likely              |   148 |   147 |        1 |                      |                                                                     |         |          |
| rich           | guess               |    71 |    71 |        0 |                      |                                                                     |         |          |
| rich           | infer-union certain |   810 |   810 |        0 |                      |                                                                     |         |          |
| rich           | infer-union likely  |   257 |   256 |        1 |                      |                                                                     |         |          |
| rich           | infer-union guess   |   269 |   269 |        0 |                      |                                                                     |         |          |
| trio           |                     |       |       |          |                    0 |                                   871 passed, 23 skipped, 3 xfailed |    47.3 |     65.2 |
| trio           | certain             |   866 |   864 |        2 |                      |                                                                     |         |          |
| trio           | likely              |   224 |   224 |        0 |                      |                                                                     |         |          |
| trio           | guess               |    35 |    35 |        0 |                      |                                                                     |         |          |
| trio           | infer-union certain |   866 |   864 |        2 |                      |                                                                     |         |          |
| trio           | infer-union likely  |   387 |   385 |        2 |                      |                                                                     |         |          |
| trio           | infer-union guess   |   288 |   288 |        0 |                      |                                                                     |         |          |
| urllib3        |                     |       |       |          |                    0 |                     839 passed, 142 skipped, 2 xfailed, 35 warnings |     9.2 |      9.9 |
| urllib3        | certain             |   121 |   120 |        1 |                      |                                                                     |         |          |
| urllib3        | likely              |    29 |    29 |        0 |                      |                                                                     |         |          |
| urllib3        | guess               |    11 |    11 |        0 |                      |                                                                     |         |          |
| urllib3        | infer-union certain |   121 |   120 |        1 |                      |                                                                     |         |          |
| urllib3        | infer-union likely  |    68 |    67 |        1 |                      |                                                                     |         |          |
| urllib3        | infer-union guess   |    35 |    35 |        0 |                      |                                                                     |         |          |
| langchain-core |                     |       |       |          |                    0 | 1 failed, 2409 passed, 20 skipped, 9 xfailed, 1 xpassed, 9 warnings |    12.5 |     11.6 |
| langchain-core | certain             | 1,018 | 1,013 |        5 |                      |                                                                     |         |          |
| langchain-core | likely              |   141 |   141 |        0 |                      |                                                                     |         |          |
| langchain-core | guess               |    65 |    62 |        3 |                      |                                                                     |         |          |
| langchain-core | infer-union certain | 1,018 | 1,013 |        5 |                      |                                                                     |         |          |
| langchain-core | infer-union likely  |   311 |   310 |        1 |                      |                                                                     |         |          |
| langchain-core | infer-union guess   |   160 |   155 |        5 |                      |                                                                     |         |          |
| sqlmodel       |                     |       |       |          |                    0 |                                                            3 errors |     3.9 |      3.8 |
| sqlmodel       | certain             |     3 |     3 |        0 |                      |                                                                     |         |          |
| sqlmodel       | likely              |     2 |     2 |        0 |                      |                                                                     |         |          |
| sqlmodel       | guess               |     1 |     1 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union certain |     3 |     3 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union likely  |     3 |     3 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union guess   |     2 |     2 |        0 |                      |                                                                     |         |          |
| marshmallow    |                     |       |       |          |                    0 |                                                         1188 passed |     1.6 |      2.2 |
| marshmallow    | certain             |    35 |    34 |        1 |                      |                                                                     |         |          |
| marshmallow    | likely              |     3 |     3 |        0 |                      |                                                                     |         |          |
| marshmallow    | guess               |     0 |     0 |        0 |                      |                                                                     |         |          |
| marshmallow    | infer-union certain |    35 |    34 |        1 |                      |                                                                     |         |          |
| marshmallow    | infer-union likely  |    18 |    18 |        0 |                      |                                                                     |         |          |
| marshmallow    | infer-union guess   |     6 |     4 |        2 |                      |                                                                     |         |          |

The bindings with neither a fix nor a guess, by shape: those a traced test reached, and those it saw
hold one type, the most any inference could type (each shape's commonest source is in
`tables/one-type.csv`):

| corpus         | shape                                      | no fix | traced | one type |
| -------------- | ------------------------------------------ | -----: | -----: | -------: |
| requests       | `call: imported function`                  |     43 |     40 |       36 |
| requests       | `copy: local`                              |     30 |     26 |       15 |
| requests       | `call: chained .method()`                  |     16 |     15 |       12 |
| requests       | `call: local.method()`                     |     15 |     13 |       11 |
| requests       | `None literal`                             |     14 |     11 |       11 |
| requests       | `call: param.method()`                     |     13 |     13 |        9 |
| requests       | `call: module.func()`                      |     13 |     11 |       10 |
| requests       | `subscript: other`                         |     10 |      8 |        8 |
| requests       | `call: self.method()`                      |     10 |      9 |        6 |
| requests       | `call: builtin iter()`                     |      9 |      4 |        4 |
| requests       | `dict (mixed/unknown elements)`            |      8 |      6 |        5 |
| requests       | `copy: param (annotated)`                  |      8 |      7 |        5 |
| requests       | `tuple (mixed/unknown elements)`           |      8 |      5 |        5 |
| requests       | `attr: local.x`                            |      7 |      7 |        4 |
| requests       | `call: builtin getattr()`                  |      7 |      6 |        2 |
| requests       | `other constant`                           |      6 |      6 |        6 |
| requests       | `JoinedStr`                                |      5 |      5 |        5 |
| requests       | `attr: chained`                            |      4 |      4 |        4 |
| requests       | `boolop (or)`                              |      4 |      4 |        3 |
| requests       | `compare`                                  |      4 |      2 |        2 |
| requests       | `call: module class`                       |      4 |      4 |        4 |
| requests       | `call: imported class`                     |      3 |      3 |        3 |
| requests       | `binop (one side literal)`                 |      3 |      1 |        1 |
| requests       | `call: local name`                         |      3 |      3 |        2 |
| requests       | `attr: module.x`                           |      3 |      1 |        1 |
| requests       | `copy: global`                             |      3 |      0 |        0 |
| requests       | `attr: param.x`                            |      3 |      3 |        3 |
| requests       | `binop (unknown operands)`                 |      3 |      2 |        2 |
| requests       | `call: module function (annotated)`        |      3 |      2 |        2 |
| requests       | `boolop (and)`                             |      2 |      2 |        1 |
| requests       | `call: builtin list()`                     |      2 |      2 |        2 |
| requests       | `ListComp (unknown elements)`              |      2 |      2 |        2 |
| requests       | `conditional`                              |      2 |      1 |        1 |
| requests       | `DictComp (unknown elements)`              |      2 |      0 |        0 |
| requests       | `call: global.method()`                    |      2 |      2 |        2 |
| requests       | `call: capitalised`                        |      1 |      0 |        0 |
| requests       | `attr: self.x`                             |      1 |      1 |        0 |
| requests       | `attr: imported.x`                         |      1 |      0 |        0 |
| requests       | `call: param name`                         |      1 |      1 |        0 |
| requests       | `call: global name`                        |      1 |      1 |        1 |
| requests       | `call: other callee`                       |      1 |      1 |        1 |
| requests       | `call: builtin chr()`                      |      1 |      1 |        1 |
| requests       | `GeneratorExp (unknown elements)`          |      1 |      0 |        0 |
| requests       | `list (mixed/unknown elements)`            |      1 |      1 |        1 |
| requests       | `call: str-literal.method()`               |      1 |      0 |        0 |
| requests       | `subscript: param[...]`                    |      1 |      1 |        1 |
| requests       | `subscript: imported[...]`                 |      1 |      1 |        1 |
| rich           | `attr: local.x`                            |     59 |     51 |       51 |
| rich           | `call: imported function`                  |     56 |     36 |       34 |
| rich           | `conditional`                              |     40 |     33 |       27 |
| rich           | `copy: local`                              |     39 |     35 |       28 |
| rich           | `attr: self.x`                             |     37 |     33 |       28 |
| rich           | `attr: chained`                            |     35 |     21 |       21 |
| rich           | `call: local.method()`                     |     34 |     23 |       20 |
| rich           | `binop (unknown operands)`                 |     28 |     23 |       23 |
| rich           | `call: chained .method()`                  |     25 |     13 |       12 |
| rich           | `copy: imported`                           |     23 |     22 |       22 |
| rich           | `call: module.func()`                      |     22 |      8 |        5 |
| rich           | `copy: param (annotated)`                  |     21 |     19 |       12 |
| rich           | `call: other name`                         |     18 |     11 |       10 |
| rich           | `copy: modclass`                           |     18 |     16 |       16 |
| rich           | `call: local name`                         |     16 |     11 |       10 |
| rich           | `call: module class`                       |     16 |      1 |        1 |
| rich           | `other constant`                           |     14 |      6 |        6 |
| rich           | `attr: imported.x`                         |     11 |      9 |        9 |
| rich           | `call: imported.attr()`                    |     11 |      6 |        6 |
| rich           | `attr: param.x`                            |     11 |      7 |        6 |
| rich           | `subscript: local[...]`                    |     11 |     10 |        9 |
| rich           | `call: self.method()`                      |     11 |     10 |        8 |
| rich           | `dict (mixed/unknown elements)`            |     10 |      1 |        1 |
| rich           | `call: param.method()`                     |     10 |      9 |        9 |
| rich           | `boolop (or)`                              |     10 |     10 |        5 |
| rich           | `ListComp (unknown elements)`              |     10 |     10 |        6 |
| rich           | `call: builtin enumerate()`                |      8 |      6 |        6 |
| rich           | `list (mixed/unknown elements)`            |      7 |      1 |        1 |
| rich           | `binop (one side literal)`                 |      7 |      7 |        7 |
| rich           | `call: builtin getattr()`                  |      7 |      5 |        2 |
| rich           | `copy: other`                              |      6 |      6 |        6 |
| rich           | `call: builtin iter()`                     |      6 |      6 |        6 |
| rich           | `subscript: other`                         |      5 |      3 |        3 |
| rich           | `call: global.method()`                    |      5 |      0 |        0 |
| rich           | `call: builtin zip()`                      |      5 |      5 |        5 |
| rich           | `copy: builtin`                            |      5 |      1 |        1 |
| rich           | `call: imported class`                     |      4 |      1 |        1 |
| rich           | `compare`                                  |      4 |      4 |        4 |
| rich           | `call: builtin list()`                     |      4 |      3 |        3 |
| rich           | `tuple (mixed/unknown elements)`           |      4 |      1 |        1 |
| rich           | `boolop (and)`                             |      4 |      4 |        3 |
| rich           | `call: builtin next()`                     |      4 |      3 |        3 |
| rich           | `call: modclass.method()`                  |      4 |      0 |        0 |
| rich           | `call: other.method()`                     |      4 |      3 |        2 |
| rich           | `call: builtin divmod()`                   |      3 |      3 |        3 |
| rich           | `subscript: imported[...]`                 |      3 |      2 |        2 |
| rich           | `DictComp (unknown elements)`              |      3 |      2 |        2 |
| rich           | `GeneratorExp (unknown elements)`          |      3 |      3 |        3 |
| rich           | `call: builtin tuple()`                    |      3 |      2 |        2 |
| rich           | `call: module function (annotated)`        |      2 |      1 |        1 |
| rich           | `call: builtin sum()`                      |      2 |      2 |        2 |
| rich           | `copy: global`                             |      2 |      1 |        0 |
| rich           | `call: builtin type()`                     |      2 |      1 |        0 |
| rich           | `call: param name`                         |      1 |      1 |        1 |
| rich           | `call: builtin frozenset()`                |      1 |      0 |        0 |
| rich           | `call: builtin min()`                      |      1 |      1 |        1 |
| rich           | `subscript: self[...]`                     |      1 |      1 |        1 |
| rich           | `None literal`                             |      1 |      1 |        1 |
| rich           | `attr: modclass.x`                         |      1 |      1 |        1 |
| rich           | `subscript: param[...]`                    |      1 |      0 |        0 |
| rich           | `Yield`                                    |      1 |      1 |        1 |
| rich           | `call: cls name`                           |      1 |      1 |        0 |
| rich           | `attr: cls.x`                              |      1 |      1 |        1 |
| rich           | `empty dict`                               |      1 |      0 |        0 |
| rich           | `attr: module.x`                           |      1 |      1 |        1 |
| trio           | `call: imported.attr()`                    |    317 |    293 |      292 |
| trio           | `call: module.func()`                      |    222 |    187 |      183 |
| trio           | `call: module function (annotated)`        |     84 |     44 |       42 |
| trio           | `empty list`                               |     61 |      0 |        0 |
| trio           | `await: call: local.method()`              |     50 |     45 |       43 |
| trio           | `call: imported class`                     |     48 |     38 |       38 |
| trio           | `call: other callee`                       |     47 |     43 |       43 |
| trio           | `call: imported function`                  |     46 |     30 |       29 |
| trio           | `call: local.method()`                     |     44 |     43 |       35 |
| trio           | `call: other name`                         |     38 |     36 |       35 |
| trio           | `await: call: module function (annotated)` |     36 |     36 |       36 |
| trio           | `call: chained .method()`                  |     35 |     28 |       19 |
| trio           | `call: param.method()`                     |     29 |     28 |       27 |
| trio           | `await: call: imported function`           |     29 |     29 |       29 |
| trio           | `attr: chained`                            |     27 |     23 |       21 |
| trio           | `copy: local`                              |     25 |     21 |       21 |
| trio           | `subscript: other`                         |     24 |     20 |       18 |
| trio           | `tuple (mixed/unknown elements)`           |     24 |     21 |       15 |
| trio           | `attr: local.x`                            |     21 |     16 |       13 |
| trio           | `call: param name`                         |     18 |     18 |       13 |
| trio           | `copy: param (annotated)`                  |     17 |     16 |       14 |
| trio           | `binop (unknown operands)`                 |     16 |     11 |       10 |
| trio           | `list (mixed/unknown elements)`            |     16 |     15 |        9 |
| trio           | `await: call: param.method()`              |     15 |      8 |        6 |
| trio           | `call: builtin set()`                      |     14 |      4 |        2 |
| trio           | `ListComp (unknown elements)`              |     14 |      5 |        5 |
| trio           | `None literal`                             |     13 |     11 |       11 |
| trio           | `attr: self.x`                             |     12 |     11 |       10 |
| trio           | `call: global.method()`                    |     12 |      9 |        9 |
| trio           | `call: other.method()`                     |     11 |     11 |        9 |
| trio           | `call: builtin getattr()`                  |     11 |     10 |        8 |
| trio           | `call: module class`                       |     10 |     10 |        4 |
| trio           | `subscript: local[...]`                    |     10 |      5 |        5 |
| trio           | `other constant`                           |      9 |      4 |        4 |
| trio           | `await: call: chained .method()`           |      9 |      8 |        7 |
| trio           | `await: call: module.func()`               |      9 |      9 |        7 |
| trio           | `call: builtin list()`                     |      8 |      7 |        3 |
| trio           | `call: capitalised`                        |      7 |      7 |        7 |
| trio           | `await: call: other.method()`              |      7 |      7 |        6 |
| trio           | `copy: other`                              |      7 |      3 |        3 |
| trio           | `await: call: other name`                  |      7 |      7 |        7 |
| trio           | `copy: imported`                           |      6 |      5 |        5 |
| trio           | `call: self.method()`                      |      5 |      5 |        3 |
| trio           | `await: call: imported.attr()`             |      5 |      2 |        2 |
| trio           | `attr: imported.x`                         |      5 |      3 |        3 |
| trio           | `attr: other.x`                            |      5 |      5 |        5 |
| trio           | `attr: module.x`                           |      5 |      3 |        3 |
| trio           | `attr: param.x`                            |      5 |      5 |        3 |
| trio           | `call: modclass.method()`                  |      4 |      4 |        4 |
| trio           | `call: builtin memoryview()`               |      4 |      3 |        3 |
| trio           | `await: call: self.method()`               |      4 |      4 |        3 |
| trio           | `call: builtin next()`                     |      3 |      2 |        2 |
| trio           | `dict (mixed/unknown elements)`            |      3 |      2 |        2 |
| trio           | `subscript: other[...]`                    |      3 |      3 |        3 |
| trio           | `subscript: param[...]`                    |      3 |      3 |        3 |
| trio           | `conditional`                              |      3 |      3 |        3 |
| trio           | `await: call: local name`                  |      3 |      3 |        3 |
| trio           | `call: local name`                         |      3 |      3 |        3 |
| trio           | `set (mixed/unknown elements)`             |      3 |      3 |        3 |
| trio           | `subscript: imported[...]`                 |      2 |      0 |        0 |
| trio           | `subscript: global[...]`                   |      2 |      2 |        2 |
| trio           | `call: builtin enumerate()`                |      2 |      2 |        1 |
| trio           | `empty dict`                               |      2 |      0 |        0 |
| trio           | `call: builtin bytearray()`                |      2 |      2 |        2 |
| trio           | `call: builtin open()`                     |      2 |      2 |        2 |
| trio           | `subscript: builtin[...]`                  |      1 |      0 |        0 |
| trio           | `call: builtin reversed()`                 |      1 |      1 |        1 |
| trio           | `Yield`                                    |      1 |      1 |        1 |
| trio           | `await: call: global name`                 |      1 |      1 |        1 |
| trio           | `unaryop Invert`                           |      1 |      0 |        0 |
| trio           | `compare`                                  |      1 |      1 |        1 |
| trio           | `call: moddef.method()`                    |      1 |      1 |        1 |
| trio           | `call: builtin eval()`                     |      1 |      1 |        1 |
| trio           | `call: builtin object()`                   |      1 |      1 |        1 |
| trio           | `copy: modclass`                           |      1 |      0 |        0 |
| urllib3        | `call: chained .method()`                  |     37 |     17 |       13 |
| urllib3        | `call: local.method()`                     |     24 |      6 |        6 |
| urllib3        | `call: module.func()`                      |     21 |      3 |        2 |
| urllib3        | `None literal`                             |     20 |      9 |        9 |
| urllib3        | `call: param.method()`                     |     20 |     10 |        6 |
| urllib3        | `attr: self.x`                             |     12 |      8 |        8 |
| urllib3        | `copy: local`                              |      9 |      6 |        5 |
| urllib3        | `dict (mixed/unknown elements)`            |      8 |      2 |        1 |
| urllib3        | `attr: local.x`                            |      8 |      6 |        5 |
| urllib3        | `copy: param (annotated)`                  |      7 |      7 |        4 |
| urllib3        | `subscript: other`                         |      7 |      4 |        4 |
| urllib3        | `call: imported function`                  |      7 |      5 |        4 |
| urllib3        | `call: self.method()`                      |      6 |      3 |        1 |
| urllib3        | `subscript: param[...]`                    |      6 |      3 |        3 |
| urllib3        | `attr: chained`                            |      5 |      1 |        1 |
| urllib3        | `copy: other`                              |      4 |      0 |        0 |
| urllib3        | `subscript: local[...]`                    |      4 |      2 |        2 |
| urllib3        | `attr: module.x`                           |      4 |      2 |        2 |
| urllib3        | `call: builtin getattr()`                  |      4 |      4 |        2 |
| urllib3        | `call: module function (annotated)`        |      4 |      1 |        1 |
| urllib3        | `copy: modclass`                           |      4 |      0 |        0 |
| urllib3        | `other constant`                           |      4 |      1 |        1 |
| urllib3        | `tuple (mixed/unknown elements)`           |      4 |      3 |        3 |
| urllib3        | `attr: param.x`                            |      4 |      1 |        1 |
| urllib3        | `ListComp (unknown elements)`              |      4 |      2 |        2 |
| urllib3        | `call: local name`                         |      4 |      1 |        1 |
| urllib3        | `call: global.method()`                    |      4 |      4 |        2 |
| urllib3        | `copy: global`                             |      3 |      0 |        0 |
| urllib3        | `call: builtin min()`                      |      3 |      0 |        0 |
| urllib3        | `list (mixed/unknown elements)`            |      3 |      0 |        0 |
| urllib3        | `empty list`                               |      3 |      0 |        0 |
| urllib3        | `copy: self`                               |      2 |      2 |        2 |
| urllib3        | `call: builtin enumerate()`                |      2 |      2 |        2 |
| urllib3        | `call: builtin staticmethod()`             |      2 |      0 |        0 |
| urllib3        | `binop: literal % formatting`              |      2 |      0 |        0 |
| urllib3        | `compare`                                  |      2 |      2 |        2 |
| urllib3        | `boolop (and)`                             |      2 |      2 |        1 |
| urllib3        | `call: builtin dict()`                     |      2 |      0 |        0 |
| urllib3        | `DictComp (unknown elements)`              |      2 |      0 |        0 |
| urllib3        | `copy: imported`                           |      2 |      0 |        0 |
| urllib3        | `attr: global.x`                           |      2 |      0 |        0 |
| urllib3        | `call: builtin bytearray()`                |      2 |      0 |        0 |
| urllib3        | `call: builtin memoryview()`               |      2 |      0 |        0 |
| urllib3        | `boolop (or)`                              |      2 |      2 |        2 |
| urllib3        | `conditional`                              |      1 |      1 |        0 |
| urllib3        | `subscript: global[...]`                   |      1 |      0 |        0 |
| urllib3        | `subscript: imported[...]`                 |      1 |      0 |        0 |
| urllib3        | `call: other name`                         |      1 |      1 |        1 |
| urllib3        | `attr: other.x`                            |      1 |      1 |        0 |
| urllib3        | `JoinedStr`                                |      1 |      0 |        0 |
| urllib3        | `call: imported.attr()`                    |      1 |      1 |        1 |
| urllib3        | `binop (one side literal)`                 |      1 |      0 |        0 |
| urllib3        | `GeneratorExp (unknown elements)`          |      1 |      1 |        1 |
| urllib3        | `call: other.method()`                     |      1 |      0 |        0 |
| urllib3        | `binop (unknown operands)`                 |      1 |      1 |        1 |
| urllib3        | `call: imported class`                     |      1 |      1 |        0 |
| urllib3        | `call: builtin len()`                      |      1 |      0 |        0 |
| langchain-core | `call: local.method()`                     |    187 |    159 |      106 |
| langchain-core | `call: param.method()`                     |    125 |    109 |       66 |
| langchain-core | `call: imported function`                  |    115 |     93 |       48 |
| langchain-core | `call: chained .method()`                  |    113 |     75 |       45 |
| langchain-core | `copy: local`                              |     87 |     71 |       38 |
| langchain-core | `call: self.method()`                      |     69 |     39 |       19 |
| langchain-core | `boolop (or)`                              |     56 |     46 |       30 |
| langchain-core | `dict (mixed/unknown elements)`            |     54 |     37 |       18 |
| langchain-core | `conditional`                              |     52 |     43 |       22 |
| langchain-core | `copy: param (annotated)`                  |     50 |     34 |       19 |
| langchain-core | `call: module function (annotated)`        |     46 |     32 |       13 |
| langchain-core | `DictComp (unknown elements)`              |     43 |     32 |       20 |
| langchain-core | `subscript: other`                         |     41 |     37 |       29 |
| langchain-core | `ListComp (unknown elements)`              |     38 |     29 |       26 |
| langchain-core | `empty list`                               |     36 |      0 |        0 |
| langchain-core | `attr: self.x`                             |     33 |     29 |       13 |
| langchain-core | `call: module.func()`                      |     31 |     24 |       22 |
| langchain-core | `call: imported class`                     |     31 |      6 |        6 |
| langchain-core | `None literal`                             |     29 |     26 |       26 |
| langchain-core | `list (mixed/unknown elements)`            |     28 |     20 |       16 |
| langchain-core | `subscript: param[...]`                    |     28 |     23 |       14 |
| langchain-core | `attr: local.x`                            |     26 |     19 |       13 |
| langchain-core | `call: builtin enumerate()`                |     24 |     17 |        4 |
| langchain-core | `JoinedStr`                                |     23 |      2 |        2 |
| langchain-core | `binop (unknown operands)`                 |     22 |      9 |        7 |
| langchain-core | `attr: chained`                            |     20 |     16 |       14 |
| langchain-core | `call: builtin getattr()`                  |     19 |     15 |       10 |
| langchain-core | `other constant`                           |     19 |      7 |        7 |
| langchain-core | `call: builtin dict()`                     |     17 |     15 |        7 |
| langchain-core | `subscript: local[...]`                    |     17 |     14 |        8 |
| langchain-core | `empty dict`                               |     15 |      0 |        0 |
| langchain-core | `call: builtin list()`                     |     14 |     11 |       11 |
| langchain-core | `await: call: imported function`           |     13 |      6 |        3 |
| langchain-core | `attr: param.x`                            |     12 |     10 |        6 |
| langchain-core | `await: call: local.method()`              |     11 |      8 |        5 |
| langchain-core | `call: other name`                         |     10 |      5 |        5 |
| langchain-core | `call: other.method()`                     |     10 |      5 |        5 |
| langchain-core | `call: builtin object()`                   |      8 |      5 |        5 |
| langchain-core | `call: builtin next()`                     |      8 |      7 |        5 |
| langchain-core | `call: builtin set()`                      |      8 |      4 |        4 |
| langchain-core | `call: builtin zip()`                      |      8 |      8 |        2 |
| langchain-core | `call: global.method()`                    |      7 |      7 |        5 |
| langchain-core | `copy: other`                              |      7 |      5 |        2 |
| langchain-core | `await: call: module.func()`               |      6 |      2 |        2 |
| langchain-core | `copy: imported`                           |      6 |      5 |        5 |
| langchain-core | `await: call: chained .method()`           |      6 |      5 |        4 |
| langchain-core | `await: call: self.method()`               |      6 |      6 |        5 |
| langchain-core | `SetComp (unknown elements)`               |      6 |      5 |        5 |
| langchain-core | `call: other callee`                       |      5 |      4 |        3 |
| langchain-core | `call: imported.attr()`                    |      4 |      2 |        1 |
| langchain-core | `await: call: param.method()`              |      4 |      3 |        2 |
| langchain-core | `compare`                                  |      4 |      3 |        3 |
| langchain-core | `tuple (mixed/unknown elements)`           |      4 |      4 |        2 |
| langchain-core | `call: builtin tuple()`                    |      4 |      4 |        2 |
| langchain-core | `attr: other.x`                            |      4 |      3 |        2 |
| langchain-core | `copy: modclass`                           |      4 |      0 |        0 |
| langchain-core | `call: builtin round()`                    |      4 |      4 |        4 |
| langchain-core | `copy: self`                               |      3 |      3 |        2 |
| langchain-core | `boolop (and)`                             |      3 |      3 |        2 |
| langchain-core | `call: builtin map()`                      |      3 |      2 |        2 |
| langchain-core | `call: local name`                         |      2 |      1 |        0 |
| langchain-core | `call: param name`                         |      2 |      2 |        1 |
| langchain-core | `call: builtin frozenset()`                |      2 |      1 |        1 |
| langchain-core | `call: builtin sorted()`                   |      2 |      2 |        2 |
| langchain-core | `call: module class`                       |      2 |      2 |        2 |
| langchain-core | `attr: cls.x`                              |      2 |      2 |        2 |
| langchain-core | `call: builtin type()`                     |      2 |      2 |        0 |
| langchain-core | `await: call: builtin anext()`             |      2 |      0 |        0 |
| langchain-core | `call: cls name`                           |      2 |      2 |        2 |
| langchain-core | `await: call: module function (annotated)` |      1 |      1 |        1 |
| langchain-core | `subscript: global[...]`                   |      1 |      1 |        1 |
| langchain-core | `call: builtin repr()`                     |      1 |      0 |        0 |
| langchain-core | `subscript: imported[...]`                 |      1 |      1 |        1 |
| langchain-core | `copy: builtin`                            |      1 |      0 |        0 |
| langchain-core | `await: call: param name`                  |      1 |      1 |        0 |
| langchain-core | `GeneratorExp (unknown elements)`          |      1 |      0 |        0 |
| langchain-core | `subscript: other[...]`                    |      1 |      1 |        1 |
| langchain-core | `call: builtin min()`                      |      1 |      1 |        1 |
| langchain-core | `call: str-literal.method()`               |      1 |      0 |        0 |
| langchain-core | `call: builtin.method()`                   |      1 |      0 |        0 |
| langchain-core | `await: copy: local`                       |      1 |      0 |        0 |
| langchain-core | `call: builtin reversed()`                 |      1 |      1 |        1 |
| langchain-core | `await: call: other.method()`              |      1 |      0 |        0 |
| langchain-core | `attr: module.x`                           |      1 |      0 |        0 |
| langchain-core | `unaryop USub`                             |      1 |      1 |        1 |
| langchain-core | `call: builtin max()`                      |      1 |      1 |        1 |
| sqlmodel       | `call: chained .method()`                  |     19 |      1 |        1 |
| sqlmodel       | `call: imported function`                  |     14 |     10 |        4 |
| sqlmodel       | `call: param.method()`                     |     12 |     11 |        8 |
| sqlmodel       | `call: module function (annotated)`        |     12 |     11 |        8 |
| sqlmodel       | `other constant`                           |      6 |      0 |        0 |
| sqlmodel       | `call: builtin getattr()`                  |      5 |      3 |        2 |
| sqlmodel       | `copy: param (annotated)`                  |      5 |      3 |        0 |
| sqlmodel       | `copy: local`                              |      4 |      2 |        2 |
| sqlmodel       | `copy: imported`                           |      3 |      1 |        1 |
| sqlmodel       | `call: local.method()`                     |      3 |      2 |        2 |
| sqlmodel       | `empty dict`                               |      3 |      0 |        0 |
| sqlmodel       | `await: call: imported function`           |      2 |      0 |        0 |
| sqlmodel       | `dict (mixed/unknown elements)`            |      2 |      1 |        0 |
| sqlmodel       | `call: other name`                         |      2 |      2 |        0 |
| sqlmodel       | `subscript: other`                         |      2 |      0 |        0 |
| sqlmodel       | `attr: imported.x`                         |      2 |      0 |        0 |
| sqlmodel       | `call: builtin type()`                     |      1 |      0 |        0 |
| sqlmodel       | `conditional`                              |      1 |      1 |        1 |
| sqlmodel       | `attr: param.x`                            |      1 |      1 |        1 |
| sqlmodel       | `boolop (or)`                              |      1 |      0 |        0 |
| sqlmodel       | `DictComp (unknown elements)`              |      1 |      0 |        0 |
| sqlmodel       | `call: other.method()`                     |      1 |      1 |        0 |
| sqlmodel       | `empty list`                               |      1 |      0 |        0 |
| sqlmodel       | `call: imported class`                     |      1 |      0 |        0 |
| marshmallow    | `dict (mixed/unknown elements)`            |     28 |      0 |        0 |
| marshmallow    | `call: self.method()`                      |     14 |      9 |        3 |
| marshmallow    | `call: param.method()`                     |     12 |      9 |        2 |
| marshmallow    | `call: chained .method()`                  |     11 |     11 |        6 |
| marshmallow    | `subscript: other`                         |      9 |      9 |        7 |
| marshmallow    | `attr: self.x`                             |      9 |      5 |        4 |
| marshmallow    | `conditional`                              |      7 |      6 |        6 |
| marshmallow    | `call: module.func()`                      |      7 |      5 |        2 |
| marshmallow    | `boolop (or)`                              |      6 |      6 |        4 |
| marshmallow    | `empty list`                               |      6 |      0 |        0 |
| marshmallow    | `call: builtin enumerate()`                |      6 |      5 |        2 |
| marshmallow    | `copy: local`                              |      6 |      6 |        5 |
| marshmallow    | `other constant`                           |      6 |      0 |        0 |
| marshmallow    | `empty dict`                               |      5 |      0 |        0 |
| marshmallow    | `attr: module.x`                           |      5 |      0 |        0 |
| marshmallow    | `copy: modclass`                           |      5 |      0 |        0 |
| marshmallow    | `subscript: local[...]`                    |      5 |      3 |        3 |
| marshmallow    | `call: local.method()`                     |      5 |      4 |        3 |
| marshmallow    | `call: builtin getattr()`                  |      5 |      5 |        4 |
| marshmallow    | `ListComp (unknown elements)`              |      4 |      3 |        3 |
| marshmallow    | `copy: builtin`                            |      3 |      0 |        0 |
| marshmallow    | `SetComp (unknown elements)`               |      3 |      1 |        1 |
| marshmallow    | `call: builtin reversed()`                 |      2 |      2 |        0 |
| marshmallow    | `set (mixed/unknown elements)`             |      2 |      0 |        0 |
| marshmallow    | `DictComp (unknown elements)`              |      2 |      1 |        1 |
| marshmallow    | `call: imported.attr()`                    |      2 |      2 |        2 |
| marshmallow    | `call: imported function`                  |      2 |      1 |        1 |
| marshmallow    | `call: builtin iter()`                     |      2 |      2 |        2 |
| marshmallow    | `tuple (mixed/unknown elements)`           |      2 |      0 |        0 |
| marshmallow    | `call: builtin tuple()`                    |      2 |      2 |        2 |
| marshmallow    | `copy: param (annotated)`                  |      2 |      2 |        1 |
| marshmallow    | `attr: cls.x`                              |      1 |      1 |        1 |
| marshmallow    | `subscript: global[...]`                   |      1 |      1 |        0 |
| marshmallow    | `attr: local.x`                            |      1 |      0 |        0 |
| marshmallow    | `attr: chained`                            |      1 |      0 |        0 |
| marshmallow    | `copy: param (unannotated)`                |      1 |      1 |        0 |
| marshmallow    | `attr: param.x`                            |      1 |      1 |        0 |
| marshmallow    | `call: module function (annotated)`        |      1 |      1 |        0 |
| marshmallow    | `call: module function (unannotated)`      |      1 |      1 |        0 |
| marshmallow    | `copy: imported`                           |      1 |      0 |        0 |
| marshmallow    | `call: builtin type()`                     |      1 |      1 |        1 |
| marshmallow    | `call: param name`                         |      1 |      1 |        0 |
| marshmallow    | `attr: other.x`                            |      1 |      1 |        1 |
| marshmallow    | `call: capitalised`                        |      1 |      0 |        0 |
| marshmallow    | `binop (unknown operands)`                 |      1 |      1 |        1 |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus         | run                | same as released | summary                                                  | new failures | gone | named | skipped anew | skipped no more |
| -------------- | ------------------ | ---------------- | -------------------------------------------------------- | -----------: | ---: | ----: | -----------: | --------------: |
| requests       | released           |                  | 617 passed, 15 skipped, 1 xpassed                        |              |      |       |              |                 |
| requests       | fix-certain        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | fix-likely         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | fix-unsafe         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-basedpyright | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-pyrefly      | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-trace        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-ty           | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-union        | True             | 617 passed, 15 skipped, 1 xpassed                        |            0 |    0 |     0 |            0 |               0 |
| rich           | released           |                  | 8 failed, 948 passed, 25 skipped                         |              |      |       |              |                 |
| rich           | fix-certain        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | fix-likely         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | fix-unsafe         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-basedpyright | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-pyrefly      | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-trace        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-ty           | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-union        | True             | 8 failed, 948 passed, 25 skipped                         |            0 |    0 |     0 |            0 |               0 |
| trio           | released           |                  | 871 passed, 23 skipped, 3 xfailed                        |              |      |       |              |                 |
| trio           | fix-certain        | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | fix-likely         | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | fix-unsafe         | False            | as infer-trace's (implied)                               |            1 |    0 |     0 |            0 |               0 |
| trio           | infer-basedpyright | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | infer-pyrefly      | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | infer-trace        | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | infer-ty           | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| trio           | infer-union        | False            | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            1 |    0 |     0 |            0 |               0 |
| urllib3        | released           |                  | 839 passed, 142 skipped, 2 xfailed                       |              |      |       |              |                 |
| urllib3        | fix-certain        | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | fix-likely         | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | fix-unsafe         | False            | as infer-trace's (implied)                               |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-basedpyright | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-pyrefly      | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-trace        | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-ty           | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-union        | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| langchain-core | released           |                  | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed |              |      |       |              |                 |
| langchain-core | fix-certain        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | fix-likely         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | fix-unsafe         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-basedpyright | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-pyrefly      | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-trace        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-ty           | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-union        | True             | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | released           |                  | 3 error                                                  |              |      |       |              |                 |
| sqlmodel       | fix-certain        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | fix-likely         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | fix-unsafe         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-basedpyright | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-pyrefly      | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-trace        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-ty           | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-union        | True             | 3 error                                                  |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | released           |                  | 1,188 passed                                             |              |      |       |              |                 |
| marshmallow    | fix-certain        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | fix-likely         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | fix-unsafe         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-basedpyright | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-pyrefly      | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-trace        | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-ty           | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-union        | True             | 1,188 passed                                             |            0 |    0 |     0 |            0 |               0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus         | run                | errors | new | gone |                                                   change |
| -------------- | ------------------ | -----: | --: | ---: | -------------------------------------------------------: |
| requests       | released           |      0 |     |      |                                                          |
| requests       | fix-certain        |      0 |   0 |    0 |     13 files changed, 119 insertions(+), 77 deletions(-) |
| requests       | fix-likely         |      0 |   0 |    0 |     13 files changed, 119 insertions(+), 77 deletions(-) |
| requests       | fix-unsafe         |      0 |   0 |    0 |     13 files changed, 119 insertions(+), 77 deletions(-) |
| requests       | infer-basedpyright |     17 |  17 |    0 |    13 files changed, 233 insertions(+), 176 deletions(-) |
| requests       | infer-pyrefly      |     10 |  10 |    0 |    13 files changed, 152 insertions(+), 106 deletions(-) |
| requests       | infer-trace        |      0 |   0 |    0 |     13 files changed, 119 insertions(+), 77 deletions(-) |
| requests       | infer-ty           |     10 |  10 |    0 |    13 files changed, 235 insertions(+), 162 deletions(-) |
| requests       | infer-union        |     17 |  17 |    0 |    13 files changed, 257 insertions(+), 179 deletions(-) |
| rich           | released           |      0 |     |      |                                                          |
| rich           | fix-certain        |      2 |   2 |    0 |   62 files changed, 1076 insertions(+), 679 deletions(-) |
| rich           | fix-likely         |      5 |   5 |    0 |   92 files changed, 1389 insertions(+), 971 deletions(-) |
| rich           | fix-unsafe         |      5 |   5 |    0 |  93 files changed, 1540 insertions(+), 1090 deletions(-) |
| rich           | infer-basedpyright |      6 |   6 |    0 |  93 files changed, 1874 insertions(+), 1391 deletions(-) |
| rich           | infer-pyrefly      |      7 |   7 |    0 |  93 files changed, 1748 insertions(+), 1216 deletions(-) |
| rich           | infer-trace        |      5 |   5 |    0 |  93 files changed, 1540 insertions(+), 1090 deletions(-) |
| rich           | infer-ty           |      6 |   6 |    0 |  93 files changed, 1703 insertions(+), 1190 deletions(-) |
| rich           | infer-union        |      9 |   9 |    0 |  93 files changed, 1952 insertions(+), 1399 deletions(-) |
| trio           | released           |      1 |     |      |                                                          |
| trio           | fix-certain        |      1 |   0 |    0 | 107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio           | fix-likely         |      1 |   0 |    0 |  107 files changed, 1441 insertions(+), 996 deletions(-) |
| trio           | fix-unsafe         |      1 |   0 |    0 | 107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio           | infer-basedpyright |      1 |   0 |    0 | 114 files changed, 1801 insertions(+), 1295 deletions(-) |
| trio           | infer-pyrefly      |      1 |   0 |    0 | 108 files changed, 1677 insertions(+), 1154 deletions(-) |
| trio           | infer-trace        |      1 |   0 |    0 | 107 files changed, 1513 insertions(+), 1050 deletions(-) |
| trio           | infer-ty           |      1 |   0 |    0 | 114 files changed, 1876 insertions(+), 1246 deletions(-) |
| trio           | infer-union        |      1 |   0 |    0 | 115 files changed, 2045 insertions(+), 1359 deletions(-) |
| urllib3        | released           |      6 |     |      |                                                          |
| urllib3        | fix-certain        |      6 |   0 |    0 |    28 files changed, 309 insertions(+), 249 deletions(-) |
| urllib3        | fix-likely         |      6 |   0 |    0 |    28 files changed, 309 insertions(+), 249 deletions(-) |
| urllib3        | fix-unsafe         |      7 |   1 |    0 |    28 files changed, 347 insertions(+), 282 deletions(-) |
| urllib3        | infer-basedpyright |     19 |  13 |    0 |    29 files changed, 426 insertions(+), 349 deletions(-) |
| urllib3        | infer-pyrefly      |     13 |   7 |    0 |    29 files changed, 425 insertions(+), 331 deletions(-) |
| urllib3        | infer-trace        |      7 |   1 |    0 |    28 files changed, 347 insertions(+), 282 deletions(-) |
| urllib3        | infer-ty           |     18 |  12 |    0 |    29 files changed, 431 insertions(+), 345 deletions(-) |
| urllib3        | infer-union        |     20 |  14 |    0 |    29 files changed, 456 insertions(+), 359 deletions(-) |
| langchain-core | released           |      0 |     |      |                                                          |
| langchain-core | fix-certain        |      1 |   1 |    0 | 147 files changed, 1787 insertions(+), 1335 deletions(-) |
| langchain-core | fix-likely         |      1 |   1 |    0 | 150 files changed, 1994 insertions(+), 1503 deletions(-) |
| langchain-core | fix-unsafe         |      1 |   1 |    0 | 150 files changed, 2108 insertions(+), 1594 deletions(-) |
| langchain-core | infer-basedpyright |      5 |   5 |    0 | 152 files changed, 2316 insertions(+), 1788 deletions(-) |
| langchain-core | infer-pyrefly      |     10 |  10 |    0 | 152 files changed, 2480 insertions(+), 1852 deletions(-) |
| langchain-core | infer-trace        |      1 |   1 |    0 | 150 files changed, 2108 insertions(+), 1594 deletions(-) |
| langchain-core | infer-ty           |      4 |   4 |    0 | 151 files changed, 2354 insertions(+), 1791 deletions(-) |
| langchain-core | infer-union        |     11 |  11 |    0 | 152 files changed, 2503 insertions(+), 1870 deletions(-) |
| marshmallow    | released           |      0 |     |      |                                                          |
| marshmallow    | fix-certain        |      0 |   0 |    0 |      9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow    | fix-likely         |      0 |   0 |    0 |      9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow    | fix-unsafe         |      0 |   0 |    0 |      9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow    | infer-basedpyright |      4 |   4 |    0 |     9 files changed, 120 insertions(+), 100 deletions(-) |
| marshmallow    | infer-pyrefly      |      0 |   0 |    0 |      9 files changed, 119 insertions(+), 98 deletions(-) |
| marshmallow    | infer-trace        |      0 |   0 |    0 |      9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow    | infer-ty           |      0 |   0 |    0 |      9 files changed, 118 insertions(+), 98 deletions(-) |
| marshmallow    | infer-union        |      4 |   4 |    0 |     9 files changed, 126 insertions(+), 105 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus         | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| -------------- | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| requests       | check                    |     0.9 |         0.1 |  0.1 |    0.03 |          2 |      5.0 | False |
| requests       | fix-certain              |     1.9 |         3.1 |  1.6 |    0.26 |          2 |      5.0 | False |
| requests       | fix-likely               |     1.9 |         3.4 |  1.8 |    0.26 |          2 |      5.0 | False |
| requests       | fix-unsafe               |     2.1 |         3.3 |  1.6 |    0.26 |          2 |      5.0 | False |
| requests       | infer-basedpyright       |     7.1 |        12.4 |  1.7 |    0.59 |          2 |     13.2 | False |
| requests       | infer-ty                 |     2.4 |         4.2 |  1.8 |    0.43 |          2 |     13.2 | False |
| requests       | infer-pyrefly            |     2.7 |         7.8 |  2.9 |     0.6 |          2 |     13.2 | False |
| requests       | census                   |     1.1 |         1.2 |  1.1 |    0.19 |          2 |      5.0 | False |
| requests       | coverage                 |     0.6 |         0.7 |  1.2 |    0.15 |          2 |      5.0 | False |
| requests       | timing                   |     1.1 |         1.3 |  1.2 |    0.17 |          2 |      5.0 | False |
| requests       | traced                   |    24.8 |        15.5 |  0.6 |     0.7 |          8 |      8.0 | False |
| requests       | tests-released           |    24.6 |        10.6 |  0.4 |    0.57 |          8 |      8.0 | False |
| requests       | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| requests       | infer-union              |     8.8 |        16.6 |  1.9 |    0.57 |          1 |      6.6 | False |
| requests       | tests-infer-union        |    21.4 |         5.6 |  0.3 |    0.49 |          8 |      8.0 | False |
| requests       | tests                    |     1.2 |         1.1 |  0.9 |    0.16 |          8 |      8.0 | False |
| requests       | types-released           |     2.3 |         3.3 |  1.4 |    0.37 |          2 |      5.0 | False |
| requests       | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      5.0 | False |
| requests       | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      5.0 | False |
| requests       | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      5.0 | False |
| requests       | types-infer-basedpyright |     2.0 |         3.1 |  1.6 |    0.36 |          2 |      5.0 | False |
| requests       | types-infer-ty           |     2.3 |         3.3 |  1.4 |    0.36 |          2 |      5.0 | False |
| requests       | types-infer-pyrefly      |     2.5 |         3.4 |  1.4 |    0.36 |          2 |      5.0 | False |
| requests       | types-infer-trace        |     1.8 |         2.8 |  1.6 |    0.36 |          2 |      5.0 | False |
| requests       | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     13.2 | False |
| rich           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      5.0 | False |
| rich           | fix-certain              |     3.6 |         8.2 |  2.3 |    0.39 |          2 |      5.0 | False |
| rich           | fix-likely               |     4.6 |        10.9 |  2.4 |    0.38 |          2 |      5.0 | False |
| rich           | fix-unsafe               |     4.0 |        10.1 |  2.5 |    0.39 |          2 |      5.0 | False |
| rich           | infer-basedpyright       |    18.4 |        66.3 |  3.6 |    2.06 |          1 |      6.6 | False |
| rich           | infer-ty                 |     5.7 |        14.7 |  2.6 |    1.21 |          2 |     13.2 | False |
| rich           | infer-pyrefly            |     8.0 |        32.5 |  4.1 |    1.91 |          2 |     13.2 | False |
| rich           | census                   |     2.0 |         3.2 |  1.6 |    0.24 |          2 |      5.0 | False |
| rich           | coverage                 |     0.9 |         1.5 |  1.7 |    0.19 |          2 |      5.0 | False |
| rich           | timing                   |     5.8 |         6.2 |  1.1 |    0.24 |          2 |      5.0 | False |
| rich           | traced                   |    14.8 |        17.5 |  1.2 |     0.4 |          1 |      1.0 | False |
| rich           | tests-released           |     7.6 |         3.9 |  0.5 |    0.12 |          1 |      1.0 | False |
| rich           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      1.0 | False |
| rich           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| rich           | infer-union              |    18.4 |        75.6 |  4.1 |    1.61 |          1 |      6.6 | False |
| rich           | tests-infer-union        |     5.0 |         2.3 |  0.5 |     0.1 |          1 |      1.0 | False |
| rich           | tests                    |     2.0 |         1.9 |  0.9 |    0.16 |          1 |      1.0 | False |
| rich           | types-released           |     2.0 |         1.7 |  0.8 |    0.15 |          2 |      5.0 | False |
| rich           | types-fix-certain        |     2.8 |         2.1 |  0.8 |    0.15 |          2 |      5.0 | False |
| rich           | types-fix-likely         |     1.8 |         1.6 |  0.9 |    0.15 |          2 |      5.0 | False |
| rich           | types-fix-unsafe         |     3.2 |         2.6 |  0.8 |    0.15 |          2 |      5.0 | False |
| rich           | types-infer-basedpyright |     1.8 |         1.6 |  0.9 |    0.15 |          2 |      5.0 | False |
| rich           | types-infer-ty           |     2.0 |         1.7 |  0.8 |    0.15 |          2 |      5.0 | False |
| rich           | types-infer-pyrefly      |     3.6 |         2.8 |  0.8 |    0.15 |          2 |      5.0 | False |
| rich           | types-infer-trace        |     2.4 |         2.2 |  0.9 |    0.15 |          2 |      5.0 | False |
| rich           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     13.2 | False |
| trio           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      5.0 | False |
| trio           | fix-certain              |     5.4 |        12.4 |  2.3 |    0.46 |          2 |      5.0 | False |
| trio           | fix-likely               |     6.9 |        15.8 |  2.3 |    0.65 |          2 |      5.0 | False |
| trio           | fix-unsafe               |    11.2 |        20.0 |  1.8 |    0.72 |          2 |      5.0 | False |
| trio           | infer-basedpyright       |    19.8 |        84.2 |  4.3 |    2.53 |          1 |      6.6 | False |
| trio           | infer-ty                 |    11.4 |        27.1 |  2.4 |     1.7 |          1 |      6.6 | False |
| trio           | infer-pyrefly            |    10.8 |        38.1 |  3.5 |    2.34 |          1 |      6.6 | False |
| trio           | census                   |     3.1 |         5.3 |  1.7 |    0.32 |          2 |      5.0 | False |
| trio           | coverage                 |     1.3 |         1.9 |  1.5 |    0.21 |          2 |      5.0 | False |
| trio           | timing                   |     5.8 |         7.8 |  1.3 |    0.32 |          2 |      5.0 | False |
| trio           | traced                   |    53.0 |        47.7 |  0.9 |    0.73 |          1 |      1.0 | False |
| trio           | tests-released           |    65.7 |        48.0 |  0.7 |    0.66 |          1 |      1.0 | False |
| trio           | tests-fix-certain        |    32.4 |        20.8 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | tests-fix-likely         |    32.8 |        21.3 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          1 |      1.0 | False |
| trio           | tests-infer-basedpyright |    32.2 |        20.7 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | tests-infer-ty           |    32.4 |        20.8 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | tests-infer-pyrefly      |    32.4 |        20.8 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | tests-infer-trace        |    32.2 |        20.6 |  0.6 |    0.57 |          1 |      1.0 | False |
| trio           | infer-union              |    18.6 |        90.2 |  4.8 |    2.08 |          1 |      6.6 | False |
| trio           | tests-infer-union        |    34.8 |        23.5 |  0.7 |    0.57 |          1 |      1.0 | False |
| trio           | tests                    |    33.6 |        22.0 |  0.7 |    0.63 |          1 |      1.0 | False |
| trio           | types-released           |     1.7 |         2.5 |  1.5 |    0.24 |          2 |      5.0 | False |
| trio           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      5.0 | False |
| trio           | types-fix-likely         |     1.6 |         2.6 |  1.6 |    0.26 |          2 |      5.0 | False |
| trio           | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          2 |      5.0 | False |
| trio           | types-infer-basedpyright |     1.6 |         2.6 |  1.6 |    0.24 |          2 |      5.0 | False |
| trio           | types-infer-ty           |     1.6 |         2.6 |  1.6 |    0.25 |          2 |      5.0 | False |
| trio           | types-infer-pyrefly      |     1.8 |         2.8 |  1.6 |    0.24 |          2 |      5.0 | False |
| trio           | types-infer-trace        |     1.0 |         1.7 |  1.7 |    0.24 |          2 |      5.0 | False |
| trio           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     13.2 | False |
| urllib3        | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      5.0 | False |
| urllib3        | fix-certain              |     3.4 |         4.2 |  1.2 |    0.28 |          2 |      5.0 | False |
| urllib3        | fix-likely               |     3.4 |         5.6 |  1.6 |    0.28 |          2 |      5.0 | False |
| urllib3        | fix-unsafe               |     3.0 |         5.0 |  1.7 |    0.28 |          2 |      5.0 | False |
| urllib3        | infer-basedpyright       |    10.0 |        23.3 |  2.3 |    1.02 |          1 |      6.6 | False |
| urllib3        | infer-ty                 |     4.4 |         8.1 |  1.8 |    0.68 |          1 |      6.6 | False |
| urllib3        | infer-pyrefly            |     4.4 |        15.2 |  3.5 |    1.03 |          1 |      6.6 | False |
| urllib3        | census                   |     1.1 |         1.6 |  1.5 |    0.19 |          2 |      5.0 | False |
| urllib3        | coverage                 |     0.8 |         0.9 |  1.1 |    0.16 |          2 |      5.0 | False |
| urllib3        | timing                   |     1.8 |         2.1 |  1.2 |    0.19 |          2 |      5.0 | False |
| urllib3        | traced                   |    12.0 |        12.4 |  1.0 |     0.3 |          1 |      1.0 | False |
| urllib3        | tests-released           |    10.6 |         6.7 |  0.6 |    0.23 |          1 |      1.0 | False |
| urllib3        | tests-fix-certain        |     1.4 |         1.2 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests-fix-likely         |     1.4 |         1.2 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      1.0 | False |
| urllib3        | tests-infer-basedpyright |     1.4 |         1.2 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests-infer-ty           |     1.4 |         1.3 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests-infer-pyrefly      |     1.4 |         1.2 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests-infer-trace        |     1.4 |         1.3 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | infer-union              |     8.4 |        23.2 |  2.8 |    0.81 |          1 |      6.6 | False |
| urllib3        | tests-infer-union        |     1.4 |         1.3 |  0.9 |    0.19 |          1 |      1.0 | False |
| urllib3        | tests                    |     2.2 |         2.1 |  1.0 |    0.26 |          1 |      1.0 | False |
| urllib3        | types-released           |     6.2 |         5.7 |  0.9 |    0.34 |          2 |      5.0 | False |
| urllib3        | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| urllib3        | types-fix-likely         |     1.4 |         1.4 |  1.0 |    0.21 |          2 |      5.0 | False |
| urllib3        | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| urllib3        | types-infer-basedpyright |     2.2 |         1.8 |  0.8 |     0.2 |          2 |      5.0 | False |
| urllib3        | types-infer-ty           |     2.4 |         2.0 |  0.8 |     0.2 |          2 |      5.0 | False |
| urllib3        | types-infer-pyrefly      |     2.4 |         2.0 |  0.8 |    0.21 |          2 |      5.0 | False |
| urllib3        | types-infer-trace        |     1.6 |         1.5 |  0.9 |    0.21 |          2 |      5.0 | False |
| urllib3        | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     13.2 | False |
| langchain-core | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      5.0 | False |
| langchain-core | fix-certain              |     8.6 |        16.7 |  1.9 |    0.57 |          2 |      5.0 | False |
| langchain-core | fix-likely               |    13.8 |        27.3 |  2.0 |    0.84 |          2 |      5.0 | False |
| langchain-core | fix-unsafe               |    12.7 |        22.9 |  1.8 |    0.76 |          2 |      5.0 | False |
| langchain-core | infer-basedpyright       |    34.6 |       132.7 |  3.8 |    3.59 |          1 |      6.6 | False |
| langchain-core | infer-ty                 |    14.0 |        34.0 |  2.4 |     2.0 |          1 |      6.6 | False |
| langchain-core | infer-pyrefly            |    13.2 |        32.1 |  2.4 |    2.39 |          1 |      6.6 | False |
| langchain-core | census                   |     5.4 |         7.9 |  1.5 |    0.39 |          2 |      5.0 | False |
| langchain-core | coverage                 |     1.1 |         2.4 |  2.2 |    0.22 |          2 |      5.0 | False |
| langchain-core | timing                   |     8.6 |        11.2 |  1.3 |    0.39 |          2 |      5.0 | False |
| langchain-core | traced                   |    18.6 |        69.9 |  3.8 |    1.62 |          8 |      8.0 | False |
| langchain-core | tests-released           |    12.0 |        58.2 |  4.9 |     1.4 |          8 |      8.0 | False |
| langchain-core | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      8.0 | False |
| langchain-core | infer-union              |    27.2 |       110.4 |  4.1 |     2.7 |          2 |     13.2 | False |
| langchain-core | tests-infer-union        |     6.0 |        25.8 |  4.3 |    1.15 |          8 |      8.0 | False |
| langchain-core | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          8 |      8.0 | False |
| langchain-core | types-released           |    10.3 |         9.7 |  0.9 |    0.59 |          2 |      5.0 | False |
| langchain-core | types-fix-certain        |     3.8 |         3.6 |  0.9 |    0.27 |          2 |      5.0 | False |
| langchain-core | types-fix-likely         |     3.6 |         3.4 |  0.9 |    0.26 |          2 |      5.0 | False |
| langchain-core | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      5.0 | False |
| langchain-core | types-infer-basedpyright |     3.4 |         3.2 |  0.9 |    0.27 |          2 |      5.0 | False |
| langchain-core | types-infer-ty           |     3.4 |         3.3 |  1.0 |    0.25 |          2 |      5.0 | False |
| langchain-core | types-infer-pyrefly      |     3.2 |         2.9 |  0.9 |    0.27 |          2 |      5.0 | False |
| langchain-core | types-infer-trace        |     2.4 |         2.3 |  1.0 |    0.27 |          2 |      5.0 | False |
| langchain-core | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     13.2 | False |
| sqlmodel       | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      5.0 | False |
| sqlmodel       | fix-certain              |     1.6 |         2.7 |  1.7 |    0.24 |          2 |      5.0 | False |
| sqlmodel       | fix-likely               |     2.3 |         3.7 |  1.6 |    0.28 |          2 |      5.0 | False |
| sqlmodel       | fix-unsafe               |     4.1 |         5.3 |  1.3 |    0.37 |          2 |      5.0 | False |
| sqlmodel       | infer-basedpyright       |    11.0 |        17.4 |  1.6 |    0.85 |          1 |      6.6 | False |
| sqlmodel       | infer-ty                 |     6.2 |         6.6 |  1.1 |    0.56 |          1 |      6.6 | False |
| sqlmodel       | infer-pyrefly            |     4.8 |         5.9 |  1.2 |    0.62 |          2 |     13.2 | False |
| sqlmodel       | census                   |     1.4 |         1.5 |  1.1 |    0.22 |          2 |      5.0 | False |
| sqlmodel       | coverage                 |     0.6 |         0.6 |  1.0 |    0.14 |          2 |      5.0 | False |
| sqlmodel       | timing                   |     2.2 |         2.2 |  1.0 |    0.22 |          2 |      5.0 | False |
| sqlmodel       | traced                   |     7.2 |         7.9 |  1.1 |    0.31 |          1 |      1.0 | False |
| sqlmodel       | tests-released           |     4.2 |         3.4 |  0.8 |    0.16 |          1 |      1.0 | False |
| sqlmodel       | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| sqlmodel       | infer-union              |    15.0 |        21.9 |  1.5 |    0.69 |          1 |      6.6 | False |
| sqlmodel       | tests-infer-union        |     2.0 |         1.8 |  0.9 |    0.14 |          1 |      1.0 | False |
| sqlmodel       | tests                    |     1.4 |         1.2 |  0.9 |    0.16 |          1 |      1.0 | False |
| marshmallow    | check                    |     0.8 |         0.8 |  1.0 |    0.17 |          2 |      5.0 | False |
| marshmallow    | fix-certain              |     1.4 |         2.1 |  1.5 |    0.28 |          2 |      5.0 | False |
| marshmallow    | fix-likely               |     1.7 |         2.4 |  1.4 |    0.28 |          2 |      5.0 | False |
| marshmallow    | fix-unsafe               |     1.7 |         2.5 |  1.5 |    0.28 |          2 |      5.0 | False |
| marshmallow    | infer-basedpyright       |     5.2 |         8.2 |  1.6 |    0.53 |          1 |      6.6 | False |
| marshmallow    | infer-ty                 |     2.2 |         3.2 |  1.5 |     0.4 |          1 |      6.6 | False |
| marshmallow    | infer-pyrefly            |     2.8 |         7.2 |  2.6 |    0.57 |          1 |      6.6 | False |
| marshmallow    | census                   |     0.8 |         0.2 |  0.2 |    0.04 |          2 |      5.0 | False |
| marshmallow    | coverage                 |     0.6 |         0.6 |  1.0 |    0.16 |          2 |      5.0 | False |
| marshmallow    | timing                   |     1.4 |         1.1 |  0.8 |    0.17 |          2 |      5.0 | False |
| marshmallow    | traced                   |     2.9 |         3.3 |  1.1 |    0.28 |          1 |      1.0 | False |
| marshmallow    | tests-released           |     2.7 |         2.2 |  0.8 |    0.09 |          1 |      1.0 | False |
| marshmallow    | tests-fix-certain        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-infer-basedpyright |     0.3 |         0.1 |  0.3 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-infer-ty           |     0.5 |         0.2 |  0.4 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      1.0 | False |
| marshmallow    | tests-infer-trace        |     0.3 |         0.2 |  0.7 |    0.03 |          1 |      1.0 | False |
| marshmallow    | infer-union              |     7.1 |        13.1 |  1.8 |    0.55 |          2 |     13.2 | False |
| marshmallow    | tests-infer-union        |     1.6 |         1.3 |  0.8 |    0.07 |          1 |      1.0 | False |
| marshmallow    | tests                    |     2.4 |         2.0 |  0.8 |    0.16 |          1 |      1.0 | False |
| marshmallow    | types-released           |     2.1 |         2.0 |  1.0 |     0.2 |          2 |      5.0 | False |
| marshmallow    | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| marshmallow    | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| marshmallow    | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| marshmallow    | types-infer-basedpyright |     0.5 |         0.3 |  0.6 |    0.08 |          2 |      5.0 | False |
| marshmallow    | types-infer-ty           |     0.4 |         0.3 |  0.7 |    0.08 |          2 |      5.0 | False |
| marshmallow    | types-infer-pyrefly      |     1.0 |         0.7 |  0.7 |     0.1 |          2 |      5.0 | False |
| marshmallow    | types-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      5.0 | False |
| marshmallow    | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     13.2 | False |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus         | released                                                 | traced                                                   | same failures |
| -------------- | -------------------------------------------------------- | -------------------------------------------------------- | ------------- |
| requests       | 617 passed, 15 skipped, 1 xpassed                        | 617 passed, 15 skipped, 1 xpassed                        | True          |
| rich           | 8 failed, 948 passed, 25 skipped                         | 8 failed, 948 passed, 25 skipped                         | False         |
| trio           | 871 passed, 23 skipped, 3 xfailed                        | 871 passed, 23 skipped, 3 xfailed                        | True          |
| urllib3        | 839 passed, 142 skipped, 2 xfailed                       | 839 passed, 142 skipped, 2 xfailed                       | False         |
| langchain-core | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed | False         |
| sqlmodel       | 3 error                                                  | 3 error                                                  | False         |
| marshmallow    | 1,188 passed                                             | 1,188 passed                                             | True          |

- rich, alt+dev, fix-certain: a second pass would still fix 1
- trio, alt+dev, fix-certain: a second pass would still fix 4
- trio, alt+dev, tests: the tests differ after fix-certain: 1 new
- trio, alt+dev, tests: the tests differ after fix-likely: 1 new
- trio, alt+dev, tests: the tests differ after fix-unsafe: 1 new
- trio, alt+dev, tests: the tests differ after infer-basedpyright: 1 new
- trio, alt+dev, tests: the tests differ after infer-pyrefly: 1 new
- trio, alt+dev, tests: the tests differ after infer-trace: 1 new
- trio, alt+dev, tests: the tests differ after infer-ty: 1 new
- urllib3, alt+dev, tests: the tests differ after fix-certain: 1 new
- urllib3, alt+dev, tests: the tests differ after fix-likely: 1 new
- urllib3, alt+dev, tests: the tests differ after fix-unsafe: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-basedpyright: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-pyrefly: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-trace: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-ty: 1 new
- requests, alt+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, alt+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, alt+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, alt+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- rich, alt+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, alt+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- trio, alt+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- trio, alt+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- trio, alt+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- urllib3, alt+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, alt+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, alt+dev, infer-union: ty's hints for 2 of 3 rounds came from the store, so its seconds
  measure less of the checker
- langchain-core, alt+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- langchain-core, alt+dev, infer-union: pyrefly's hints for 2 of 3 rounds came from the store, so
  its seconds measure less of the checker
- langchain-core, alt+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- marshmallow, alt+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- marshmallow, alt+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- marshmallow, alt+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
