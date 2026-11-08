# Alt corpora

The run `alt` (`python -m tests.corpus`) on alt: constricter 0.4.5.dev41+g28434383f.d20261107
(`4f4059bfc760`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 5 minutes. Timings don't compare across machines, nor their seconds across runs, taken
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
| requests       | likely             |   105 |      96 |      9 |       |      0 |    0 |   265 |      559 |     1.0 |
| requests       | unsafe             |   113 |      96 |      9 |     8 |      0 |    0 |   273 |      559 |     1.4 |
| requests       | infer-basedpyright |   221 |      96 |     16 |   109 |      0 |    0 |   381 |      559 |     2.0 |
| requests       | infer-ty           |   223 |      96 |     13 |   114 |      0 |    0 |   383 |      559 |     1.2 |
| requests       | infer-pyrefly      |   146 |      96 |     10 |    40 |      0 |    0 |   306 |      559 |     1.7 |
| requests       | infer-trace        |   113 |      96 |      9 |     8 |      0 |    0 |   273 |      559 |     0.9 |
| rich           | certain            | 1,021 |   1,021 |        |       |      0 |    1 | 1,359 |    2,516 |     1.4 |
| rich           | likely             | 1,328 |   1,033 |    295 |       |      0 |    0 | 1,666 |    2,516 |     1.9 |
| rich           | unsafe             | 1,455 |   1,022 |    293 |   140 |      0 |    0 | 1,793 |    2,516 |     2.1 |
| rich           | infer-basedpyright | 1,773 |   1,021 |    296 |   456 |      0 |    0 | 2,111 |    2,516 |    11.2 |
| rich           | infer-ty           | 1,617 |   1,021 |    299 |   297 |      0 |    1 | 1,955 |    2,516 |     3.4 |
| rich           | infer-pyrefly      | 1,657 |   1,021 |    298 |   338 |      0 |    1 | 1,995 |    2,516 |     3.1 |
| rich           | infer-trace        | 1,455 |   1,022 |    293 |   140 |      0 |    0 | 1,793 |    2,516 |     2.4 |
| trio           | certain            | 1,102 |   1,102 |        |       |      0 |    4 | 1,633 |    3,531 |     2.8 |
| trio           | likely             | 1,377 |   1,110 |    267 |       |      0 |    0 | 1,908 |    3,531 |     4.3 |
| trio           | unsafe             | 1,438 |   1,107 |    267 |    64 |      0 |    0 | 1,969 |    3,531 |     5.8 |
| trio           | infer-basedpyright | 1,690 |   1,103 |    273 |   314 |      0 |    0 | 2,221 |    3,531 |     4.3 |
| trio           | infer-ty           | 1,786 |   1,102 |    273 |   411 |      0 |    8 | 2,317 |    3,531 |     5.4 |
| trio           | infer-pyrefly      | 1,602 |   1,102 |    270 |   230 |      0 |    7 | 2,133 |    3,531 |     5.4 |
| trio           | infer-trace        | 1,438 |   1,107 |    267 |    64 |      0 |    0 | 1,969 |    3,531 |     3.9 |
| urllib3        | certain            |   259 |     259 |        |       |      0 |    0 |   480 |      855 |     0.8 |
| urllib3        | likely             |   301 |     261 |     40 |       |      0 |    0 |   522 |      855 |     1.2 |
| urllib3        | unsafe             |   338 |     259 |     40 |    39 |      0 |    0 |   559 |      855 |     1.1 |
| urllib3        | infer-basedpyright |   412 |     259 |     40 |   113 |      0 |    1 |   633 |      855 |     2.7 |
| urllib3        | infer-ty           |   416 |     259 |     40 |   117 |      0 |    0 |   637 |      855 |     2.3 |
| urllib3        | infer-pyrefly      |   411 |     259 |     40 |   112 |      0 |    0 |   632 |      855 |     2.0 |
| urllib3        | infer-trace        |   338 |     259 |     40 |    39 |      0 |    0 |   559 |      855 |     0.8 |
| langchain-core | certain            | 1,702 |   1,702 |        |       |      0 |    0 | 2,668 |    4,696 |     3.8 |
| langchain-core | likely             | 1,906 |   1,706 |    200 |       |      0 |    0 | 2,872 |    4,696 |     9.6 |
| langchain-core | unsafe             | 2,009 |   1,702 |    200 |   107 |      0 |    0 | 2,975 |    4,696 |     7.4 |
| langchain-core | infer-basedpyright | 2,209 |   1,702 |    211 |   296 |      0 |    0 | 3,175 |    4,696 |     8.7 |
| langchain-core | infer-ty           | 2,246 |   1,702 |    213 |   331 |      0 |    0 | 3,212 |    4,696 |     9.2 |
| langchain-core | infer-pyrefly      | 2,359 |   1,702 |    218 |   439 |      0 |    0 | 3,325 |    4,696 |     9.6 |
| langchain-core | infer-trace        | 2,009 |   1,702 |    200 |   107 |      0 |    0 | 2,975 |    4,696 |     4.4 |
| sqlmodel       | certain            |    11 |      11 |        |       |      0 |    0 |    50 |      164 |     1.0 |
| sqlmodel       | likely             |    16 |      11 |      5 |       |      0 |    0 |    55 |      164 |     2.1 |
| sqlmodel       | unsafe             |    21 |      11 |      5 |     5 |      0 |    0 |    60 |      164 |     2.1 |
| sqlmodel       | infer-basedpyright |    23 |      11 |      5 |     7 |      0 |    0 |    62 |      164 |     2.3 |
| sqlmodel       | infer-ty           |    23 |      11 |      5 |     7 |      0 |    0 |    62 |      164 |     2.1 |
| sqlmodel       | infer-pyrefly      |    30 |      11 |      5 |    14 |      0 |    0 |    69 |      164 |     2.5 |
| sqlmodel       | infer-trace        |    21 |      11 |      5 |     5 |      0 |    0 |    60 |      164 |     1.2 |
| marshmallow    | certain            |    51 |      51 |        |       |      0 |    0 |   127 |      378 |     0.8 |
| marshmallow    | likely             |    56 |      51 |      5 |       |      0 |    0 |   132 |      378 |     0.8 |
| marshmallow    | unsafe             |   103 |      51 |      5 |    47 |      0 |    0 |   179 |      378 |     2.1 |
| marshmallow    | infer-basedpyright |   120 |      51 |      5 |    64 |      0 |    0 |   196 |      378 |     1.4 |
| marshmallow    | infer-ty           |   118 |      51 |      5 |    62 |      0 |    0 |   194 |      378 |     1.8 |
| marshmallow    | infer-pyrefly      |   119 |      51 |      5 |    63 |      0 |    0 |   195 |      378 |     2.1 |
| marshmallow    | infer-trace        |   103 |      51 |      5 |    47 |      0 |    0 |   179 |      378 |     1.2 |

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
| infer-basedpyright | checker           |   825 |         |        |   825 |
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
| requests       |    4 |        0.42 |       0.5 |    1 |                         4.6 |       5.9 | hyperfine |                yes |
| rich           |    4 |        2.47 |      1.14 |    1 |                        23.6 |      25.2 | hyperfine |                yes |
| trio           |    4 |        3.48 |      1.74 |    1 |                        30.9 |      32.4 | hyperfine |                yes |
| urllib3        |    4 |        0.86 |      0.68 |    1 |                         8.0 |       9.4 | hyperfine |                yes |
| langchain-core |    4 |        5.19 |      2.46 |    1 |                        39.1 |      43.1 | hyperfine |                yes |
| sqlmodel       |    4 |        0.95 |       1.5 |    1 |                         6.5 |       9.3 | hyperfine |                yes |
| marshmallow    |    4 |        0.62 |      0.75 |    1 |                         3.7 |       4.7 | hyperfine |                yes |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus         | tier                |  told |  held | differed | resting on the trace |                                                               tests | seconds | untraced |
| -------------- | ------------------- | ----: | ----: | -------: | -------------------: | ------------------------------------------------------------------: | ------: | -------: |
| requests       |                     |       |       |          |                    0 |                      617 passed, 15 skipped, 1 xpassed, 18 warnings |    23.2 |     24.1 |
| requests       | certain             |    63 |    62 |        1 |                      |                                                                     |         |          |
| requests       | likely              |     8 |     8 |        0 |                      |                                                                     |         |          |
| requests       | guess               |     5 |     5 |        0 |                      |                                                                     |         |          |
| requests       | infer-union certain |    63 |    62 |        1 |                      |                                                                     |         |          |
| requests       | infer-union likely  |    90 |    90 |        0 |                      |                                                                     |         |          |
| requests       | infer-union guess   |    35 |    35 |        0 |                      |                                                                     |         |          |
| rich           |                     |       |       |          |                    0 |                                              956 passed, 25 skipped |     6.3 |      4.9 |
| rich           | certain             |   810 |   810 |        0 |                      |                                                                     |         |          |
| rich           | likely              |   148 |   147 |        1 |                      |                                                                     |         |          |
| rich           | guess               |    71 |    71 |        0 |                      |                                                                     |         |          |
| rich           | infer-union certain |   810 |   810 |        0 |                      |                                                                     |         |          |
| rich           | infer-union likely  |   257 |   256 |        1 |                      |                                                                     |         |          |
| rich           | infer-union guess   |   269 |   269 |        0 |                      |                                                                     |         |          |
| trio           |                     |       |       |          |                    0 |                                   871 passed, 23 skipped, 3 xfailed |    52.9 |     65.2 |
| trio           | certain             |   866 |   864 |        2 |                      |                                                                     |         |          |
| trio           | likely              |   224 |   224 |        0 |                      |                                                                     |         |          |
| trio           | guess               |    35 |    35 |        0 |                      |                                                                     |         |          |
| trio           | infer-union certain |   866 |   864 |        2 |                      |                                                                     |         |          |
| trio           | infer-union likely  |   387 |   385 |        2 |                      |                                                                     |         |          |
| trio           | infer-union guess   |   288 |   288 |        0 |                      |                                                                     |         |          |
| urllib3        |                     |       |       |          |                    0 |                    2418 passed, 288 skipped, 4 xfailed, 71 warnings |    61.6 |     54.9 |
| urllib3        | certain             |   151 |   150 |        1 |                      |                                                                     |         |          |
| urllib3        | likely              |    32 |    31 |        1 |                      |                                                                     |         |          |
| urllib3        | guess               |    13 |    13 |        0 |                      |                                                                     |         |          |
| urllib3        | infer-union certain |   151 |   150 |        1 |                      |                                                                     |         |          |
| urllib3        | infer-union likely  |    79 |    76 |        3 |                      |                                                                     |         |          |
| urllib3        | infer-union guess   |    41 |    41 |        0 |                      |                                                                     |         |          |
| langchain-core |                     |       |       |          |                    0 | 1 failed, 2409 passed, 20 skipped, 9 xfailed, 1 xpassed, 8 warnings |    11.0 |      6.8 |
| langchain-core | certain             | 1,019 | 1,014 |        5 |                      |                                                                     |         |          |
| langchain-core | likely              |   141 |   141 |        0 |                      |                                                                     |         |          |
| langchain-core | guess               |    65 |    62 |        3 |                      |                                                                     |         |          |
| langchain-core | infer-union certain | 1,019 | 1,014 |        5 |                      |                                                                     |         |          |
| langchain-core | infer-union likely  |   311 |   309 |        2 |                      |                                                                     |         |          |
| langchain-core | infer-union guess   |   161 |   156 |        5 |                      |                                                                     |         |          |
| sqlmodel       |                     |       |       |          |                    0 |                          1 failed, 267 passed, 41 warnings, 1 error |    12.0 |      7.3 |
| sqlmodel       | certain             |     6 |     6 |        0 |                      |                                                                     |         |          |
| sqlmodel       | likely              |     4 |     4 |        0 |                      |                                                                     |         |          |
| sqlmodel       | guess               |     1 |     1 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union certain |     6 |     6 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union likely  |     6 |     6 |        0 |                      |                                                                     |         |          |
| sqlmodel       | infer-union guess   |     6 |     6 |        0 |                      |                                                                     |         |          |
| marshmallow    |                     |       |       |          |                    0 |                                                         1188 passed |     2.5 |      2.2 |
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
| requests       | `copy: local`                              |     30 |     25 |       14 |
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
| requests       | `call: builtin getattr()`                  |      7 |      6 |        3 |
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
| requests       | `ListComp (unknown elements)`              |      2 |      1 |        1 |
| requests       | `conditional`                              |      2 |      1 |        1 |
| requests       | `DictComp (unknown elements)`              |      2 |      0 |        0 |
| requests       | `call: global.method()`                    |      2 |      2 |        2 |
| requests       | `call: capitalised`                        |      1 |      0 |        0 |
| requests       | `attr: self.x`                             |      1 |      1 |        0 |
| requests       | `attr: imported.x`                         |      1 |      0 |        0 |
| requests       | `call: param name`                         |      1 |      1 |        1 |
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
| urllib3        | `call: chained .method()`                  |     37 |     22 |       17 |
| urllib3        | `call: local.method()`                     |     24 |      7 |        6 |
| urllib3        | `call: module.func()`                      |     21 |      7 |        5 |
| urllib3        | `None literal`                             |     20 |     17 |       17 |
| urllib3        | `call: param.method()`                     |     20 |     11 |        7 |
| urllib3        | `attr: self.x`                             |     12 |     12 |        9 |
| urllib3        | `copy: local`                              |      9 |      6 |        5 |
| urllib3        | `dict (mixed/unknown elements)`            |      8 |      2 |        1 |
| urllib3        | `attr: local.x`                            |      8 |      7 |        5 |
| urllib3        | `copy: param (annotated)`                  |      7 |      7 |        4 |
| urllib3        | `subscript: other`                         |      7 |      4 |        4 |
| urllib3        | `call: imported function`                  |      7 |      6 |        5 |
| urllib3        | `call: self.method()`                      |      6 |      3 |        1 |
| urllib3        | `subscript: param[...]`                    |      6 |      3 |        3 |
| urllib3        | `attr: chained`                            |      5 |      2 |        2 |
| urllib3        | `copy: other`                              |      4 |      0 |        0 |
| urllib3        | `subscript: local[...]`                    |      4 |      2 |        2 |
| urllib3        | `attr: module.x`                           |      4 |      2 |        2 |
| urllib3        | `call: builtin getattr()`                  |      4 |      4 |        1 |
| urllib3        | `call: module function (annotated)`        |      4 |      2 |        2 |
| urllib3        | `copy: modclass`                           |      4 |      0 |        0 |
| urllib3        | `other constant`                           |      4 |      2 |        2 |
| urllib3        | `tuple (mixed/unknown elements)`           |      4 |      3 |        3 |
| urllib3        | `attr: param.x`                            |      4 |      2 |        2 |
| urllib3        | `ListComp (unknown elements)`              |      4 |      2 |        2 |
| urllib3        | `call: local name`                         |      4 |      3 |        3 |
| urllib3        | `call: global.method()`                    |      4 |      4 |        2 |
| urllib3        | `copy: global`                             |      3 |      0 |        0 |
| urllib3        | `call: builtin min()`                      |      3 |      0 |        0 |
| urllib3        | `list (mixed/unknown elements)`            |      3 |      1 |        1 |
| urllib3        | `empty list`                               |      3 |      0 |        0 |
| urllib3        | `copy: self`                               |      2 |      2 |        2 |
| urllib3        | `call: builtin enumerate()`                |      2 |      2 |        2 |
| urllib3        | `call: builtin staticmethod()`             |      2 |      0 |        0 |
| urllib3        | `binop: literal % formatting`              |      2 |      0 |        0 |
| urllib3        | `compare`                                  |      2 |      2 |        2 |
| urllib3        | `boolop (and)`                             |      2 |      2 |        0 |
| urllib3        | `call: builtin dict()`                     |      2 |      0 |        0 |
| urllib3        | `DictComp (unknown elements)`              |      2 |      0 |        0 |
| urllib3        | `copy: imported`                           |      2 |      0 |        0 |
| urllib3        | `attr: global.x`                           |      2 |      0 |        0 |
| urllib3        | `call: builtin bytearray()`                |      2 |      1 |        1 |
| urllib3        | `call: builtin memoryview()`               |      2 |      1 |        1 |
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
| urllib3        | `call: other.method()`                     |      1 |      1 |        0 |
| urllib3        | `binop (unknown operands)`                 |      1 |      1 |        1 |
| urllib3        | `call: imported class`                     |      1 |      1 |        0 |
| urllib3        | `call: builtin len()`                      |      1 |      1 |        1 |
| langchain-core | `call: local.method()`                     |    187 |    160 |      107 |
| langchain-core | `call: param.method()`                     |    125 |    109 |       66 |
| langchain-core | `call: imported function`                  |    115 |     93 |       47 |
| langchain-core | `call: chained .method()`                  |    113 |     76 |       47 |
| langchain-core | `copy: local`                              |     87 |     71 |       38 |
| langchain-core | `call: self.method()`                      |     69 |     39 |       19 |
| langchain-core | `boolop (or)`                              |     56 |     46 |       30 |
| langchain-core | `dict (mixed/unknown elements)`            |     54 |     37 |       18 |
| langchain-core | `conditional`                              |     52 |     43 |       22 |
| langchain-core | `copy: param (annotated)`                  |     50 |     34 |       19 |
| langchain-core | `call: module function (annotated)`        |     46 |     31 |       13 |
| langchain-core | `DictComp (unknown elements)`              |     43 |     32 |       20 |
| langchain-core | `subscript: other`                         |     41 |     37 |       29 |
| langchain-core | `ListComp (unknown elements)`              |     38 |     28 |       25 |
| langchain-core | `empty list`                               |     36 |      0 |        0 |
| langchain-core | `attr: self.x`                             |     33 |     29 |       13 |
| langchain-core | `call: module.func()`                      |     31 |     24 |       22 |
| langchain-core | `call: imported class`                     |     31 |      6 |        6 |
| langchain-core | `None literal`                             |     29 |     26 |       26 |
| langchain-core | `list (mixed/unknown elements)`            |     28 |     20 |       16 |
| langchain-core | `subscript: param[...]`                    |     28 |     23 |       13 |
| langchain-core | `attr: local.x`                            |     26 |     19 |       12 |
| langchain-core | `call: builtin enumerate()`                |     24 |     17 |        4 |
| langchain-core | `JoinedStr`                                |     23 |      2 |        2 |
| langchain-core | `binop (unknown operands)`                 |     22 |      9 |        7 |
| langchain-core | `attr: chained`                            |     20 |     17 |       14 |
| langchain-core | `call: builtin getattr()`                  |     19 |     15 |       10 |
| langchain-core | `other constant`                           |     19 |      7 |        7 |
| langchain-core | `call: builtin dict()`                     |     17 |     15 |        7 |
| langchain-core | `subscript: local[...]`                    |     17 |     14 |        9 |
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
| langchain-core | `SetComp (unknown elements)`               |      6 |      4 |        4 |
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
| sqlmodel       | `call: chained .method()`                  |     19 |     17 |       12 |
| sqlmodel       | `call: imported function`                  |     14 |     11 |        3 |
| sqlmodel       | `call: param.method()`                     |     12 |     11 |        7 |
| sqlmodel       | `call: module function (annotated)`        |     12 |     11 |        7 |
| sqlmodel       | `other constant`                           |      6 |      0 |        0 |
| sqlmodel       | `call: builtin getattr()`                  |      5 |      3 |        2 |
| sqlmodel       | `copy: param (annotated)`                  |      5 |      5 |        0 |
| sqlmodel       | `copy: local`                              |      4 |      4 |        3 |
| sqlmodel       | `copy: imported`                           |      3 |      1 |        1 |
| sqlmodel       | `call: local.method()`                     |      3 |      3 |        3 |
| sqlmodel       | `empty dict`                               |      3 |      0 |        0 |
| sqlmodel       | `await: call: imported function`           |      2 |      2 |        0 |
| sqlmodel       | `dict (mixed/unknown elements)`            |      2 |      1 |        0 |
| sqlmodel       | `call: other name`                         |      2 |      2 |        0 |
| sqlmodel       | `subscript: other`                         |      2 |      0 |        0 |
| sqlmodel       | `attr: imported.x`                         |      2 |      0 |        0 |
| sqlmodel       | `call: builtin type()`                     |      1 |      0 |        0 |
| sqlmodel       | `conditional`                              |      1 |      1 |        0 |
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

| corpus         | run                                 | same as released | summary                                                  | new failures | gone | named | skipped anew | skipped no more |
| -------------- | ----------------------------------- | ---------------- | -------------------------------------------------------- | -----------: | ---: | ----: | -----------: | --------------: |
| requests       | released (from alt-11-08-2026-1133) |                  | 617 passed, 15 skipped, 1 xpassed                        |              |      |       |              |                 |
| requests       | fix-certain                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | fix-likely                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | fix-unsafe                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-basedpyright                  | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-pyrefly                       | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-trace                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-ty                            | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| requests       | infer-union                         | True             | 617 passed, 15 skipped, 1 xpassed                        |            0 |    0 |     0 |            0 |               0 |
| rich           | released                            |                  | 956 passed, 25 skipped                                   |              |      |       |              |                 |
| rich           | fix-certain                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | fix-likely                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | fix-unsafe                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-basedpyright                  | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-pyrefly                       | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-trace                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-ty                            | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| rich           | infer-union                         | True             | 956 passed, 25 skipped                                   |            0 |    0 |     0 |            0 |               0 |
| trio           | released (from alt-11-08-2026-1133) |                  | 871 passed, 23 skipped, 3 xfailed                        |              |      |       |              |                 |
| trio           | fix-certain                         | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | fix-likely                          | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | fix-unsafe                          | True             | as infer-trace's (implied)                               |            0 |    0 |     1 |            0 |               0 |
| trio           | infer-basedpyright                  | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | infer-pyrefly                       | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | infer-trace                         | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | infer-ty                            | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| trio           | infer-union                         | True             | 1 failed, 870 passed, 23 skipped, 3 xfailed              |            0 |    0 |     1 |            0 |               0 |
| urllib3        | released                            |                  | 2,418 passed, 288 skipped, 4 xfailed                     |              |      |       |              |                 |
| urllib3        | fix-certain                         | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | fix-likely                          | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | fix-unsafe                          | False            | as infer-trace's (implied)                               |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-basedpyright                  | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-pyrefly                       | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-trace                         | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-ty                            | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| urllib3        | infer-union                         | False            | 1 error, 1 skipped                                       |            1 |    0 |     0 |            0 |               0 |
| langchain-core | released                            |                  | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed |              |      |       |              |                 |
| langchain-core | fix-certain                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | fix-likely                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | fix-unsafe                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-basedpyright                  | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-pyrefly                       | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-trace                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-ty                            | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| langchain-core | infer-union                         | True             | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed |            0 |    0 |     0 |            0 |               0 |
| sqlmodel       | released                            |                  | 1 failed, 267 passed                                     |              |      |       |              |                 |
| sqlmodel       | fix-certain                         | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | fix-likely                          | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | fix-unsafe                          | False            | as infer-trace's (implied)                               |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-basedpyright                  | False            | as infer-ty's (implied)                                  |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-pyrefly                       | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-trace                         | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-ty                            | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| sqlmodel       | infer-union                         | False            | 2 failed, 266 passed                                     |            1 |    0 |     0 |            0 |               0 |
| marshmallow    | released (from alt-11-08-2026-1133) |                  | 1,188 passed                                             |              |      |       |              |                 |
| marshmallow    | fix-certain                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | fix-likely                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | fix-unsafe                          | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-basedpyright                  | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-pyrefly                       | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-trace                         | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-ty                            | True             | as infer-union's (implied)                               |            0 |    0 |     0 |            0 |               0 |
| marshmallow    | infer-union                         | True             | 1,188 passed                                             |            0 |    0 |     0 |            0 |               0 |

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
| rich           | infer-basedpyright |      6 |   6 |    0 |  93 files changed, 1873 insertions(+), 1390 deletions(-) |
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
| requests       | check                    |     1.0 |         1.0 |  1.0 |    0.17 |          2 |     0.24 | False |
| requests       | fix-certain              |     1.8 |         2.8 |  1.6 |    0.26 |          2 |     0.32 | False |
| requests       | fix-likely               |     2.2 |         3.3 |  1.5 |    0.25 |          2 |     0.32 | False |
| requests       | fix-unsafe               |     3.2 |         3.5 |  1.1 |    0.26 |          2 |     0.32 | False |
| requests       | infer-basedpyright       |     4.0 |         4.3 |  1.1 |    0.21 |          1 |     0.37 | False |
| requests       | infer-ty                 |     3.0 |         3.8 |  1.3 |    0.26 |          1 |     0.27 | False |
| requests       | infer-pyrefly            |     3.4 |         3.6 |  1.1 |    0.26 |          1 |     0.25 | False |
| requests       | census                   |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.24 | False |
| requests       | coverage                 |     0.6 |         0.7 |  1.2 |    0.15 |          2 |     0.19 | False |
| requests       | timing                   |     1.2 |         1.4 |  1.2 |    0.17 |          2 |     0.21 | False |
| requests       | traced                   |    25.5 |        14.9 |  0.6 |    0.62 |          1 |     0.87 | False |
| requests       | tests-released           |    24.6 |        10.6 |  0.4 |    0.57 |          8 |      8.0 | False |
| requests       | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.71 | False |
| requests       | infer-union              |     2.4 |         4.0 |  1.7 |    0.26 |          1 |     0.36 | False |
| requests       | tests-infer-union        |    22.5 |         7.5 |  0.3 |    0.49 |          1 |     0.61 | False |
| requests       | tests                    |     2.0 |         1.8 |  0.9 |    0.16 |          2 |      0.2 | False |
| requests       | types-released           |     3.6 |         4.1 |  1.1 |    0.38 |          2 |     0.46 | False |
| requests       | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.45 | False |
| requests       | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.45 | False |
| requests       | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.45 | False |
| requests       | types-infer-basedpyright |     2.2 |         3.3 |  1.5 |    0.35 |          2 |     0.45 | False |
| requests       | types-infer-ty           |     2.3 |         3.3 |  1.4 |    0.37 |          2 |     0.45 | False |
| requests       | types-infer-pyrefly      |     3.6 |         4.1 |  1.1 |    0.37 |          2 |     0.45 | False |
| requests       | types-infer-trace        |     2.5 |         3.4 |  1.4 |    0.35 |          2 |     0.45 | False |
| requests       | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| rich           | check                    |     1.6 |         3.2 |  2.0 |    0.24 |          2 |      0.3 | False |
| rich           | fix-certain              |     3.5 |         8.4 |  2.4 |    0.38 |          3 |     0.49 | False |
| rich           | fix-likely               |     3.8 |        10.4 |  2.7 |    0.35 |          3 |     0.47 | False |
| rich           | fix-unsafe               |     4.4 |        10.2 |  2.3 |    0.36 |          3 |     0.49 | False |
| rich           | infer-basedpyright       |    19.1 |        45.8 |  2.4 |     1.2 |          1 |     0.64 | False |
| rich           | infer-ty                 |     6.6 |        12.2 |  1.8 |    0.36 |          1 |      0.5 | False |
| rich           | infer-pyrefly            |     6.2 |        11.6 |  1.9 |    0.36 |          1 |     0.48 | False |
| rich           | census                   |     1.0 |         0.8 |  0.8 |    0.05 |          2 |      0.3 | False |
| rich           | coverage                 |     0.8 |         1.5 |  1.9 |    0.19 |          2 |     0.24 | False |
| rich           | timing                   |     4.0 |         5.4 |  1.4 |    0.24 |          2 |      0.3 | False |
| rich           | traced                   |    10.6 |        13.5 |  1.3 |    0.37 |          1 |      0.5 | False |
| rich           | tests-released           |     5.4 |         2.3 |  0.4 |    0.09 |          1 |     0.15 | False |
| rich           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| rich           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| rich           | tests-fix-unsafe         |     0.3 |         0.1 |  0.3 |    0.03 |          1 |     0.15 | False |
| rich           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| rich           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| rich           | tests-infer-pyrefly      |     0.3 |         0.1 |  0.3 |    0.03 |          1 |     0.15 | False |
| rich           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| rich           | infer-union              |    16.4 |        54.9 |  3.3 |    1.43 |          1 |      0.4 | False |
| rich           | tests-infer-union        |     4.0 |         1.4 |  0.3 |     0.1 |          1 |     0.12 | False |
| rich           | tests                    |     1.4 |         1.3 |  0.9 |    0.16 |          1 |      0.2 | False |
| rich           | types-released           |     4.0 |         2.4 |  0.6 |    0.14 |          1 |     0.19 | False |
| rich           | types-fix-certain        |     2.8 |         2.2 |  0.8 |    0.15 |          1 |     0.19 | False |
| rich           | types-fix-likely         |     2.4 |         1.8 |  0.8 |    0.15 |          1 |     0.19 | False |
| rich           | types-fix-unsafe         |     3.1 |         2.4 |  0.8 |    0.15 |          1 |     0.19 | False |
| rich           | types-infer-basedpyright |     2.1 |         1.9 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich           | types-infer-ty           |     3.6 |         2.6 |  0.7 |    0.15 |          1 |     0.19 | False |
| rich           | types-infer-pyrefly      |     3.0 |         2.4 |  0.8 |    0.15 |          1 |     0.19 | False |
| rich           | types-infer-trace        |     2.4 |         2.1 |  0.9 |    0.15 |          1 |     0.19 | False |
| rich           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| trio           | check                    |     2.2 |         4.5 |  2.0 |    0.32 |          2 |      0.4 | False |
| trio           | fix-certain              |     5.7 |        12.5 |  2.2 |    0.46 |          3 |     0.57 | False |
| trio           | fix-likely               |     6.6 |        16.1 |  2.4 |    0.66 |          3 |     0.81 | False |
| trio           | fix-unsafe               |     9.4 |        18.1 |  1.9 |    0.66 |          2 |      0.9 | False |
| trio           | infer-basedpyright       |     7.8 |        16.2 |  2.1 |    0.53 |          4 |     2.53 | False |
| trio           | infer-ty                 |     8.8 |        17.9 |  2.0 |    0.64 |          2 |     1.42 | False |
| trio           | infer-pyrefly            |     9.2 |        16.9 |  1.8 |    0.64 |          2 |     1.46 | False |
| trio           | census                   |     1.9 |         0.8 |  0.4 |    0.05 |          2 |      0.4 | False |
| trio           | coverage                 |     0.8 |         1.4 |  1.7 |    0.21 |          2 |     0.26 | False |
| trio           | timing                   |     5.7 |         7.8 |  1.4 |    0.32 |          2 |      0.4 | False |
| trio           | traced                   |    59.8 |        52.9 |  0.9 |    0.66 |          1 |     0.91 | False |
| trio           | tests-released           |    65.7 |        48.0 |  0.7 |    0.66 |          1 |      1.0 | False |
| trio           | tests-fix-certain        |    32.2 |        20.7 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | tests-fix-likely         |    32.2 |        20.7 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.04 |          1 |     0.82 | False |
| trio           | tests-infer-basedpyright |    32.2 |        20.6 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | tests-infer-ty           |    33.0 |        21.4 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | tests-infer-pyrefly      |    32.2 |        20.6 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | tests-infer-trace        |    32.2 |        20.7 |  0.6 |    0.57 |          1 |     0.71 | False |
| trio           | infer-union              |     7.2 |        14.9 |  2.1 |    0.65 |          2 |     1.04 | False |
| trio           | tests-infer-union        |    33.7 |        22.6 |  0.7 |    0.57 |          1 |     0.71 | False |
| trio           | tests                    |     1.2 |         1.0 |  0.8 |    0.16 |          1 |     0.79 | False |
| trio           | types-released           |     1.6 |         2.4 |  1.5 |    0.25 |          2 |      0.3 | False |
| trio           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      0.3 | False |
| trio           | types-fix-likely         |     1.6 |         2.3 |  1.4 |    0.23 |          2 |     0.32 | False |
| trio           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          2 |      0.3 | False |
| trio           | types-infer-basedpyright |     1.4 |         2.2 |  1.6 |    0.25 |          2 |      0.3 | False |
| trio           | types-infer-ty           |     1.4 |         2.2 |  1.6 |    0.23 |          2 |     0.31 | False |
| trio           | types-infer-pyrefly      |     1.2 |         2.1 |  1.8 |    0.24 |          2 |      0.3 | False |
| trio           | types-infer-trace        |     1.2 |         2.1 |  1.8 |    0.24 |          2 |      0.3 | False |
| trio           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| urllib3        | check                    |     1.0 |         1.5 |  1.5 |    0.19 |          2 |     0.24 | False |
| urllib3        | fix-certain              |     2.0 |         3.7 |  1.9 |    0.28 |          2 |     0.35 | False |
| urllib3        | fix-likely               |     2.4 |         4.6 |  1.9 |    0.28 |          2 |     0.35 | False |
| urllib3        | fix-unsafe               |     2.6 |         4.9 |  1.9 |    0.28 |          2 |     0.35 | False |
| urllib3        | infer-basedpyright       |     5.2 |         5.9 |  1.1 |    0.24 |          1 |     0.42 | False |
| urllib3        | infer-ty                 |     4.6 |         5.8 |  1.3 |    0.28 |          1 |     0.42 | False |
| urllib3        | infer-pyrefly            |     4.0 |         5.7 |  1.4 |    0.28 |          1 |     0.32 | False |
| urllib3        | census                   |     0.6 |         0.3 |  0.5 |    0.04 |          2 |     0.24 | False |
| urllib3        | coverage                 |     0.6 |         0.9 |  1.5 |    0.16 |          2 |      0.2 | False |
| urllib3        | timing                   |     1.8 |         2.3 |  1.3 |    0.19 |          2 |     0.24 | False |
| urllib3        | traced                   |    63.2 |        14.5 |  0.2 |    0.28 |          1 |     0.37 | False |
| urllib3        | tests-released           |    55.2 |         6.0 |  0.1 |    0.19 |          1 |     0.29 | False |
| urllib3        | tests-fix-certain        |     1.4 |         1.2 |  0.9 |     0.2 |          1 |     0.24 | False |
| urllib3        | tests-fix-likely         |     1.4 |         1.3 |  0.9 |     0.2 |          1 |     0.24 | False |
| urllib3        | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.29 | False |
| urllib3        | tests-infer-basedpyright |     1.4 |         1.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| urllib3        | tests-infer-ty           |     1.4 |         1.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| urllib3        | tests-infer-pyrefly      |     1.4 |         1.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| urllib3        | tests-infer-trace        |     1.4 |         1.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| urllib3        | infer-union              |     2.3 |         4.2 |  1.8 |    0.27 |          3 |     1.01 | False |
| urllib3        | tests-infer-union        |     1.4 |         1.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| urllib3        | tests                    |     2.4 |         2.2 |  0.9 |    0.26 |          1 |     0.32 | False |
| urllib3        | types-released           |     0.6 |         0.4 |  0.7 |    0.07 |          1 |     0.42 | False |
| urllib3        | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.42 | False |
| urllib3        | types-fix-likely         |     1.2 |         1.2 |  1.0 |    0.21 |          1 |     0.26 | False |
| urllib3        | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.42 | False |
| urllib3        | types-infer-basedpyright |     2.2 |         1.8 |  0.8 |     0.2 |          1 |     0.25 | False |
| urllib3        | types-infer-ty           |     2.8 |         2.3 |  0.8 |    0.21 |          1 |     0.25 | False |
| urllib3        | types-infer-pyrefly      |     2.6 |         2.1 |  0.8 |    0.21 |          1 |     0.26 | False |
| urllib3        | types-infer-trace        |     1.3 |         1.2 |  0.9 |     0.2 |          1 |     0.26 | False |
| urllib3        | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| langchain-core | check                    |     3.0 |         5.6 |  1.9 |    0.39 |          2 |     0.49 | False |
| langchain-core | fix-certain              |     7.8 |        15.7 |  2.0 |    0.58 |          2 |     0.71 | False |
| langchain-core | fix-likely               |    13.7 |        27.6 |  2.0 |    0.82 |          2 |     1.05 | False |
| langchain-core | fix-unsafe               |    12.4 |        22.0 |  1.8 |    0.64 |          2 |     0.95 | False |
| langchain-core | infer-basedpyright       |    14.2 |        23.8 |  1.7 |     0.8 |          2 |     2.24 | False |
| langchain-core | infer-ty                 |    15.2 |        23.7 |  1.6 |     0.8 |          1 |     0.83 | False |
| langchain-core | infer-pyrefly            |    14.6 |        24.1 |  1.7 |     0.8 |          2 |     1.99 | False |
| langchain-core | census                   |     1.2 |         1.0 |  0.8 |    0.06 |          2 |     0.49 | False |
| langchain-core | coverage                 |     1.2 |         2.6 |  2.2 |    0.23 |          3 |     0.27 | False |
| langchain-core | timing                   |     8.1 |        10.5 |  1.3 |    0.39 |          2 |     0.49 | False |
| langchain-core | traced                   |    17.9 |        71.0 |  4.0 |    1.43 |          5 |     2.02 | False |
| langchain-core | tests-released           |     7.0 |        31.8 |  4.5 |    1.15 |          7 |     1.75 | False |
| langchain-core | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.75 | False |
| langchain-core | infer-union              |     9.9 |        20.5 |  2.1 |    0.81 |          5 |     3.37 | False |
| langchain-core | tests-infer-union        |     9.0 |        31.8 |  3.5 |    1.15 |          6 |     1.44 | False |
| langchain-core | tests                    |     1.2 |         1.1 |  0.9 |    0.17 |          2 |      0.2 | False |
| langchain-core | types-released           |     1.4 |         0.8 |  0.6 |    0.14 |          1 |     0.74 | False |
| langchain-core | types-fix-certain        |     3.0 |         2.8 |  0.9 |    0.27 |          1 |     0.34 | False |
| langchain-core | types-fix-likely         |     3.6 |         3.3 |  0.9 |    0.27 |          1 |     0.32 | False |
| langchain-core | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          1 |     0.74 | False |
| langchain-core | types-infer-basedpyright |     3.9 |         3.5 |  0.9 |    0.27 |          1 |     0.34 | False |
| langchain-core | types-infer-ty           |     5.2 |         4.4 |  0.8 |    0.25 |          1 |     0.31 | False |
| langchain-core | types-infer-pyrefly      |     4.9 |         4.5 |  0.9 |    0.27 |          1 |     0.34 | False |
| langchain-core | types-infer-trace        |     2.5 |         2.4 |  1.0 |    0.26 |          1 |     0.34 | False |
| langchain-core | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlmodel       | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.27 | False |
| sqlmodel       | fix-certain              |     2.7 |         3.8 |  1.4 |    0.24 |          2 |      0.3 | False |
| sqlmodel       | fix-likely               |     4.0 |         4.6 |  1.1 |    0.28 |          2 |     0.35 | False |
| sqlmodel       | fix-unsafe               |     4.4 |         4.5 |  1.0 |    0.28 |          2 |     0.46 | False |
| sqlmodel       | infer-basedpyright       |     4.8 |         5.0 |  1.0 |    0.28 |          1 |     0.53 | False |
| sqlmodel       | infer-ty                 |     4.6 |         4.7 |  1.0 |    0.28 |          1 |     0.35 | False |
| sqlmodel       | infer-pyrefly            |     4.4 |         4.9 |  1.1 |    0.33 |          1 |     0.39 | False |
| sqlmodel       | census                   |     2.0 |         1.8 |  0.9 |    0.22 |          2 |     0.27 | False |
| sqlmodel       | coverage                 |     1.0 |         0.7 |  0.7 |    0.14 |          1 |     0.17 | False |
| sqlmodel       | timing                   |     2.8 |         2.6 |  0.9 |    0.22 |          1 |     0.27 | False |
| sqlmodel       | traced                   |    14.7 |        14.5 |  1.0 |    0.29 |          1 |     0.39 | False |
| sqlmodel       | tests-released           |     7.6 |         7.2 |  0.9 |    0.24 |          1 |      0.2 | False |
| sqlmodel       | tests-fix-certain        |     6.6 |         6.2 |  0.9 |    0.23 |          1 |      0.2 | False |
| sqlmodel       | tests-fix-likely         |     4.8 |         4.6 |  1.0 |    0.24 |          1 |      0.2 | False |
| sqlmodel       | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| sqlmodel       | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| sqlmodel       | tests-infer-ty           |     6.8 |         6.3 |  0.9 |    0.24 |          1 |      0.2 | False |
| sqlmodel       | tests-infer-pyrefly      |     6.4 |         6.0 |  0.9 |    0.24 |          1 |      0.2 | False |
| sqlmodel       | tests-infer-trace        |     5.3 |         5.0 |  0.9 |    0.24 |          1 |      0.2 | False |
| sqlmodel       | infer-union              |     3.2 |         4.7 |  1.5 |    0.33 |          1 |     0.43 | False |
| sqlmodel       | tests-infer-union        |     9.2 |         8.1 |  0.9 |    0.24 |          1 |     0.17 | False |
| sqlmodel       | tests                    |     6.1 |         6.0 |  1.0 |    0.31 |          1 |      0.2 | False |
| marshmallow    | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| marshmallow    | fix-certain              |     2.4 |         2.7 |  1.1 |    0.28 |          2 |     0.35 | False |
| marshmallow    | fix-likely               |     2.0 |         2.7 |  1.4 |    0.29 |          2 |     0.35 | False |
| marshmallow    | fix-unsafe               |     3.6 |         3.2 |  0.9 |    0.29 |          2 |     0.35 | False |
| marshmallow    | infer-basedpyright       |     3.4 |         3.4 |  1.0 |    0.25 |          1 |     0.33 | False |
| marshmallow    | infer-ty                 |     3.6 |         3.3 |  0.9 |    0.29 |          1 |     0.25 | False |
| marshmallow    | infer-pyrefly            |     3.6 |         3.4 |  0.9 |    0.29 |          1 |     0.24 | False |
| marshmallow    | census                   |     1.8 |         1.2 |  0.7 |    0.17 |          1 |     0.21 | False |
| marshmallow    | coverage                 |     0.8 |         0.7 |  0.9 |    0.16 |          1 |      0.2 | False |
| marshmallow    | timing                   |     2.0 |         1.6 |  0.8 |    0.17 |          1 |     0.21 | False |
| marshmallow    | traced                   |     5.2 |         5.2 |  1.0 |    0.28 |          1 |     0.35 | False |
| marshmallow    | tests-released           |     2.7 |         2.2 |  0.8 |    0.09 |          1 |      1.0 | False |
| marshmallow    | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-fix-likely         |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-infer-basedpyright |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow    | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| marshmallow    | infer-union              |     3.6 |         4.2 |  1.2 |    0.26 |          1 |     0.34 | False |
| marshmallow    | tests-infer-union        |     1.8 |         1.5 |  0.8 |    0.07 |          1 |     0.09 | False |
| marshmallow    | tests                    |     2.0 |         1.7 |  0.8 |    0.16 |          1 |      0.2 | False |
| marshmallow    | types-released           |     1.4 |         1.1 |  0.8 |     0.1 |          1 |     0.25 | False |
| marshmallow    | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.25 | False |
| marshmallow    | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| marshmallow    | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| marshmallow    | types-infer-basedpyright |     1.8 |         1.2 |  0.7 |     0.1 |          1 |      0.1 | False |
| marshmallow    | types-infer-ty           |     1.0 |         0.5 |  0.5 |    0.07 |          1 |      0.1 | False |
| marshmallow    | types-infer-pyrefly      |     0.8 |         0.5 |  0.6 |    0.07 |          1 |     0.12 | False |
| marshmallow    | types-infer-trace        |     0.5 |         0.2 |  0.4 |    0.03 |          1 |     0.25 | False |
| marshmallow    | types                    |     0.3 |         0.2 |  0.7 |    0.03 |          1 |     0.04 | False |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus         | released                                                 | traced                                                   | same failures |
| -------------- | -------------------------------------------------------- | -------------------------------------------------------- | ------------- |
| requests       | 617 passed, 15 skipped, 1 xpassed                        | 617 passed, 15 skipped, 1 xpassed                        | True          |
| rich           | 956 passed, 25 skipped                                   | 956 passed, 25 skipped                                   | True          |
| trio           | 871 passed, 23 skipped, 3 xfailed                        | 871 passed, 23 skipped, 3 xfailed                        | True          |
| urllib3        | 2,418 passed, 288 skipped, 4 xfailed                     | 2,418 passed, 288 skipped, 4 xfailed                     | True          |
| langchain-core | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed | 1 failed, 2,409 passed, 20 skipped, 9 xfailed, 1 xpassed | False         |
| sqlmodel       | 1 failed, 267 passed                                     | 1 error, 1 failed, 267 passed                            | False         |
| marshmallow    | 1,188 passed                                             | 1,188 passed                                             | True          |

- rich, alt+dev, fix-certain: a second pass would still fix 1
- trio, alt+dev, fix-certain: a second pass would still fix 4
- urllib3, alt+dev, tests: the tests differ after fix-certain: 1 new
- urllib3, alt+dev, tests: the tests differ after fix-likely: 1 new
- urllib3, alt+dev, tests: the tests differ after fix-unsafe: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-basedpyright: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-pyrefly: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-trace: 1 new
- urllib3, alt+dev, tests: the tests differ after infer-ty: 1 new
- sqlmodel, alt+dev, tests: the tests differ after fix-certain: 1 new
- sqlmodel, alt+dev, tests: the tests differ after fix-likely: 1 new
- sqlmodel, alt+dev, tests: the tests differ after fix-unsafe: 1 new
- sqlmodel, alt+dev, tests: the tests differ after infer-basedpyright: 1 new
- sqlmodel, alt+dev, tests: the tests differ after infer-pyrefly: 1 new
- sqlmodel, alt+dev, tests: the tests differ after infer-trace: 1 new
- sqlmodel, alt+dev, tests: the tests differ after infer-ty: 1 new
- requests, alt+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- requests, alt+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- requests, alt+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, alt+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, alt+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- requests, alt+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, alt+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- rich, alt+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- rich, alt+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- rich, alt+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- rich, alt+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- rich, alt+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- trio, alt+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- trio, alt+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds measure
  less of the checker
- trio, alt+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- trio, alt+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- trio, alt+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- trio, alt+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- urllib3, alt+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- urllib3, alt+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- urllib3, alt+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, alt+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, alt+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- urllib3, alt+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- langchain-core, alt+dev, infer-basedpyright: basedpyright's hints for 3 of 3 rounds came from the
  store, so its seconds measure less of the checker
- langchain-core, alt+dev, infer-ty: ty's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- langchain-core, alt+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- langchain-core, alt+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store,
  so its seconds measure less of the checker
- langchain-core, alt+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so
  its seconds measure less of the checker
- langchain-core, alt+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the store,
  so its seconds measure less of the checker
- sqlmodel, alt+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- sqlmodel, alt+dev, infer-pyrefly: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: basedpyright's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: pyrefly's hints for 3 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sqlmodel, alt+dev, infer-union: ty's hints for 3 of 3 rounds came from the store, so its seconds
  measure less of the checker
- marshmallow, alt+dev, infer-basedpyright: basedpyright's hints for 2 of 2 rounds came from the
  store, so its seconds measure less of the checker
- marshmallow, alt+dev, infer-ty: ty's hints for 2 of 2 rounds came from the store, so its seconds
  measure less of the checker
- marshmallow, alt+dev, infer-pyrefly: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- marshmallow, alt+dev, infer-union: basedpyright's hints for 2 of 2 rounds came from the store, so
  its seconds measure less of the checker
- marshmallow, alt+dev, infer-union: pyrefly's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
- marshmallow, alt+dev, infer-union: ty's hints for 2 of 2 rounds came from the store, so its
  seconds measure less of the checker
